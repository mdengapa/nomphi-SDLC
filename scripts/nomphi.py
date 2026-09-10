#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, re, shutil, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
CORE=ROOT/'.nomphi'/'core'; PROJECT=ROOT/'.nomphi'/'project'; TASKS=ROOT/'.nomphi'/'tasks'
TEMPLATES=CORE/'templates'; TRANSITIONS=CORE/'config'/'transitions.json'
RISKS={'LOW','MEDIUM','HIGH','CRITICAL'}
TASK_ID=re.compile(r'^[A-Z][A-Z0-9_-]{1,63}$')

def now(): return datetime.now(timezone.utc).isoformat()
def read_json(p): return json.loads(Path(p).read_text())
def write_json(p,o): Path(p).write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
def fail(m): raise SystemExit(m)

def validate_adapter():
    names=['project-profile.json','architecture.md','domain.md','invariants.md','conventions.md','security-boundaries.md','commands.json']
    missing=[n for n in names if not (PROJECT/n).is_file()]
    if missing: fail('HUMAN_DECISION_REQUIRED: incomplete project adapter: '+', '.join(missing))
    p=read_json(PROJECT/'project-profile.json')
    if p.get('project_id') in (None,'','REPLACE_ME'):
        fail('HUMAN_DECISION_REQUIRED: project adapter is not initialized; use project-init explicitly')
    if p.get('default_risk','MEDIUM') not in RISKS: fail('Invalid default_risk')
    if not isinstance(read_json(PROJECT/'commands.json'),dict): fail('Invalid commands.json')
    return p

def valid_task(t):
    if not TASK_ID.fullmatch(t): fail('Invalid task id')
    return t

def td(t): return TASKS/valid_task(t)
def sp(t): return td(t)/'state.json'
def state(t):
    if not sp(t).is_file(): fail(f'Unknown task: {t}')
    s=read_json(sp(t))
    if s.get('task_id')!=t: fail('Corrupt task state')
    return s
def save(t,s): write_json(sp(t),s)

def init_project(a):
    p=read_json(PROJECT/'project-profile.json')
    p.update(project_id=a.id,name=a.name,project_type=a.type,default_risk=a.default_risk)
    write_json(PROJECT/'project-profile.json',p); validate_adapter()
    print(f'Initialized project adapter: {a.id} — {a.name}')

def task_init(a):
    pr=validate_adapter(); risk=a.risk or pr.get('default_risk','MEDIUM'); d=td(a.task_id)
    if risk not in RISKS: fail('Invalid risk')
    if d.exists(): fail(f'Task already exists: {a.task_id}')
    d.mkdir(parents=True)
    for n in ['requirement.md','spec.md','threat-model.md','implementation-report.md','verification-report.md','security-report.md','documentation-report.md','release-report.md']:
        src=TEMPLATES/n
        if not src.is_file(): fail(f'Missing template: {n}')
        shutil.copyfile(src,d/n)
    req=(d/'requirement.md').read_text().replace('ID:',f'ID: {a.task_id}',1).replace('Title:',f'Title: {a.title}',1).replace('Risk: LOW | MEDIUM | HIGH | CRITICAL',f'Risk: {risk}',1)
    (d/'requirement.md').write_text(req)
    s={'task_id':a.task_id,'project_id':pr['project_id'],'title':a.title,'risk':risk,'state':'NEW','iterations':{'planning':0,'security_design':0,'implementation':0,'verification':0,'security_audit':0,'documentation':0,'release':0},'history':[{'at':now(),'from':None,'to':'NEW','reason':'task initialized'}]}
    save(a.task_id,s); print(d)

def status(a): print(json.dumps(state(a.task_id),indent=2))

def next_stage(a):
    s=state(a.task_id); st=s['state']; risk=s['risk']
    m={'NEW':'PLANNING','PLANNING':'SPEC_READY after completed spec.md','SPEC_READY':'SECURITY_DESIGN' if risk!='LOW' else 'IMPLEMENTING','SECURITY_DESIGN':'SECURITY_DESIGN_READY after completed threat-model.md','SECURITY_DESIGN_READY':'IMPLEMENTING','IMPLEMENTING':'IMPLEMENTED after implementation-report.md','IMPLEMENTED':'VERIFYING','VERIFYING':'VERIFICATION_ACCEPTED or VERIFICATION_REJECTED','VERIFICATION_REJECTED':'IMPLEMENTING','VERIFICATION_ACCEPTED':'SECURITY_AUDIT' if risk!='LOW' else 'DOCUMENTING','SECURITY_AUDIT':'SECURITY_PASSED or SECURITY_BLOCKED','SECURITY_BLOCKED':'IMPLEMENTING or PLANNING','SECURITY_PASSED':'DOCUMENTING','DOCUMENTING':'DOCUMENTED','DOCUMENTED':'RELEASE_GATE','RELEASE_GATE':'RELEASED only after passing gate','RELEASE_BLOCKED':'route to owning stage','RELEASED':'terminal'}
    print(m.get(st,'unknown'))

def ready(t, n):
    p = td(t) / n
    if not p.is_file() or p.stat().st_size < 20:
        return False

    x = p.read_text(errors='replace')

    if n == 'spec.md':
        return bool(
            re.search(
                r'^Status:\s*COMPLETE\s*$',
                x,
                flags=re.MULTILINE,
            )
        )

    return not any(marker in x for marker in ('PENDING', 'REPLACE_ME'))

PREREQ={('PLANNING','SPEC_READY'):['spec.md'],('SECURITY_DESIGN','SECURITY_DESIGN_READY'):['threat-model.md'],('IMPLEMENTING','IMPLEMENTED'):['implementation-report.md'],('VERIFYING','VERIFICATION_ACCEPTED'):['verification-report.md'],('VERIFYING','VERIFICATION_REJECTED'):['verification-report.md'],('SECURITY_AUDIT','SECURITY_PASSED'):['security-report.md'],('SECURITY_AUDIT','SECURITY_BLOCKED'):['security-report.md'],('DOCUMENTING','DOCUMENTED'):['documentation-report.md'],('RELEASE_GATE','RELEASED'):['release-report.md']}

def transition(a):
    validate_adapter(); s=state(a.task_id); cur=s['state']; allowed=read_json(TRANSITIONS).get(cur,[])
    if a.to not in allowed: fail(f'Invalid transition {cur} -> {a.to}; allowed={allowed}')
    if s['risk']!='LOW' and cur=='SPEC_READY' and a.to=='IMPLEMENTING': fail('Security design is mandatory for MEDIUM/HIGH/CRITICAL')
    missing=[n for n in PREREQ.get((cur,a.to),[]) if not ready(a.task_id,n)]
    if missing: fail(f'Transition blocked; incomplete artifacts: {missing}')
    prev=cur; s['state']=a.to
    keys={'PLANNING':'planning','SECURITY_DESIGN':'security_design','IMPLEMENTING':'implementation','VERIFYING':'verification','SECURITY_AUDIT':'security_audit','DOCUMENTING':'documentation','RELEASE_GATE':'release'}
    if a.to in keys: s['iterations'][keys[a.to]]=s['iterations'].get(keys[a.to],0)+1
    s['history'].append({'at':now(),'from':prev,'to':a.to,'reason':a.reason or 'transition'}); save(a.task_id,s)
    print(f'{a.task_id}: {prev} -> {a.to}')

ROUTE={'NEW':'planner','PLANNING':'planner','SPEC_READY':'security','SECURITY_DESIGN':'security','SECURITY_DESIGN_READY':'implementer','IMPLEMENTING':'implementer','IMPLEMENTED':'verifier','VERIFYING':'verifier','VERIFICATION_REJECTED':'implementer','VERIFICATION_ACCEPTED':'security','SECURITY_AUDIT':'security','SECURITY_BLOCKED':'implementer','SECURITY_PASSED':'documenter','DOCUMENTING':'documenter','DOCUMENTED':'release','RELEASE_GATE':'release','RELEASE_BLOCKED':'orchestrator'}

def handoff(a):
    validate_adapter(); s=state(a.task_id); d=td(a.task_id); expected=ROUTE.get(s['state'])
    if s['risk']=='LOW' and s['state']=='SPEC_READY': expected='implementer'
    if s['risk']=='LOW' and s['state']=='VERIFICATION_ACCEPTED': expected='documenter'
    if expected and a.agent!=expected: fail(f'Handoff blocked: {s["state"]} routes to {expected}, not {a.agent}')
    manifest=CORE/'manifests'/f'{a.agent}.md'
    if not manifest.is_file(): fail('Unknown agent')
    common=[PROJECT/n for n in ['project-profile.json','architecture.md','domain.md','invariants.md','conventions.md','security-boundaries.md']]
    files={'planner':['requirement.md'],'security':['requirement.md','spec.md','threat-model.md','implementation-report.md','verification-report.md'],'implementer':['requirement.md','spec.md','threat-model.md','verification-report.md','security-report.md'],'verifier':['requirement.md','spec.md','threat-model.md','implementation-report.md'],'documenter':['spec.md','implementation-report.md','verification-report.md','security-report.md'],'release':['spec.md','threat-model.md','implementation-report.md','verification-report.md','security-report.md','documentation-report.md'],'orchestrator':['requirement.md']}[a.agent]
    out=[f'# Handoff — {a.task_id} → {a.agent}','','## State','```json',json.dumps(s,indent=2),'```','','## Role manifest',manifest.read_text()]
    for p in common: out += ['',f'## Project context: {p.name}',p.read_text()]
    for n in files:
        p=d/n
        if p.exists(): out += ['',f'## Task artifact: {n}',p.read_text()]
    dest=d/f'handoff-{a.agent}-{s["state"].lower()}.md'; dest.write_text('\n'.join(out)+'\n'); print(dest)

def verdict(p):
    if not p.exists(): return None
    for line in p.read_text().splitlines():
        if line.startswith('Verdict:'):
            v=line.split(':',1)[1].strip()
            if v and v!='PENDING': return v

def run_cmds(kind):
    cmds=read_json(PROJECT/'commands.json').get(kind,[]) or []
    if not isinstance(cmds,list): fail(f'{kind} commands must be a list')
    result=[]
    for cmd in cmds:
        if not isinstance(cmd,str) or not cmd.strip(): fail(f'Invalid {kind} command')
        print(f'[{kind}] {cmd}'); r=subprocess.run(cmd,shell=True,cwd=ROOT); result.append((cmd,r.returncode))
    return result

def gate(a):
    validate_adapter(); s=state(a.task_id); d=td(a.task_id); failures=[]; evidence={}
    if s['state']!='RELEASE_GATE': failures.append(f'invalid_state:{s["state"]}')
    required=['requirement.md','spec.md','implementation-report.md','verification-report.md','documentation-report.md']
    if s['risk']!='LOW': required += ['threat-model.md','security-report.md']
    failures += [f'missing_or_incomplete:{n}' for n in required if not ready(a.task_id,n)]
    vv=verdict(d/'verification-report.md'); evidence['verification_verdict']=vv
    if vv not in ('ACCEPT','ACCEPT_WITH_MINOR_ISSUES'): failures.append('verification_not_accepted')
    if s['risk']!='LOW':
        sv=verdict(d/'security-report.md'); evidence['security_verdict']=sv
        if sv not in ('PASS','PASS_WITH_LOW_MEDIUM_FINDINGS'): failures.append('security_not_accepted')
    evidence['commands']={}
    if a.run_checks:
        for kind in ['test','typecheck','lint']:
            rs=run_cmds(kind); evidence['commands'][kind]=rs
            if not rs: failures.append(f'{kind}_not_configured')
            elif any(code for _,code in rs): failures.append(f'{kind}_failed')
    result={'task':a.task_id,'project':s['project_id'],'pass':not failures,'failures':failures,'evidence':evidence}
    print(json.dumps(result,indent=2))
    if failures: sys.exit(2)

def doctor(a):
    errors=[]
    try: validate_adapter()
    except SystemExit as e: errors.append(str(e))
    print(json.dumps({'ok':not errors,'errors':errors},indent=2)); sys.exit(0 if not errors else 2)

def parser():
    p=argparse.ArgumentParser(prog='nomphi'); sub=p.add_subparsers(dest='cmd',required=True)
    x=sub.add_parser('project-init'); x.add_argument('--id',required=True); x.add_argument('--name',required=True); x.add_argument('--type',default='other'); x.add_argument('--default-risk',default='MEDIUM',choices=sorted(RISKS)); x.set_defaults(func=init_project)
    x=sub.add_parser('doctor'); x.set_defaults(func=doctor)
    x=sub.add_parser('task-init'); x.add_argument('task_id'); x.add_argument('--title',required=True); x.add_argument('--risk',choices=sorted(RISKS)); x.set_defaults(func=task_init)
    x=sub.add_parser('status'); x.add_argument('task_id'); x.set_defaults(func=status)
    x=sub.add_parser('next'); x.add_argument('task_id'); x.set_defaults(func=next_stage)
    x=sub.add_parser('transition'); x.add_argument('task_id'); x.add_argument('to'); x.add_argument('--reason'); x.set_defaults(func=transition)
    x=sub.add_parser('handoff'); x.add_argument('task_id'); x.add_argument('agent',choices=['orchestrator','planner','implementer','verifier','security','documenter','release']); x.set_defaults(func=handoff)
    x=sub.add_parser('gate'); x.add_argument('task_id'); x.add_argument('--run-checks',action='store_true'); x.set_defaults(func=gate)
    return p

def main():
    a=parser().parse_args(); a.func(a)
if __name__=='__main__': main()
