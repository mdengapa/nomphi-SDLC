#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / '.nomphi' / 'core'
PROJECT = ROOT / '.nomphi' / 'project'
TASKS = ROOT / '.nomphi' / 'tasks'
TEMPLATES = CORE / 'templates'
TRANSITIONS = CORE / 'config' / 'transitions.json'
RISKS = {'LOW','MEDIUM','HIGH','CRITICAL'}


def now(): return datetime.now(timezone.utc).isoformat()

def read_json(p): return json.loads(Path(p).read_text())
def write_json(p,obj): Path(p).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')

def profile():
    p = PROJECT / 'project-profile.json'
    if not p.exists(): raise SystemExit('Missing .nomphi/project/project-profile.json')
    data = read_json(p)
    if data.get('project_id') in (None,'','REPLACE_ME'):
        raise SystemExit('Project adapter not initialized: set project_id in .nomphi/project/project-profile.json')
    return data

def td(task): return TASKS / task
def sp(task): return td(task) / 'state.json'
def state(task):
    if not sp(task).exists(): raise SystemExit(f'Unknown task: {task}')
    return read_json(sp(task))
def save(task,s): write_json(sp(task),s)

def init_project(args):
    p = read_json(PROJECT/'project-profile.json')
    p['project_id']=args.id
    p['name']=args.name
    p['project_type']=args.type
    p['default_risk']=args.default_risk
    write_json(PROJECT/'project-profile.json',p)
    print(f'Initialized project adapter: {args.id} — {args.name}')

def task_init(args):
    pr=profile(); risk=args.risk or pr.get('default_risk','MEDIUM')
    if risk not in RISKS: raise SystemExit('Invalid risk')
    d=td(args.task_id)
    if d.exists(): raise SystemExit(f'Task already exists: {args.task_id}')
    d.mkdir(parents=True)
    for name in ['requirement.md','spec.md','threat-model.md','implementation-report.md','verification-report.md','security-report.md','documentation-report.md','release-report.md']:
        shutil.copyfile(TEMPLATES/name,d/name)
    req=(d/'requirement.md').read_text()
    req=req.replace('ID:',f'ID: {args.task_id}',1).replace('Title:',f'Title: {args.title}',1).replace('Risk: LOW | MEDIUM | HIGH | CRITICAL',f'Risk: {risk}',1)
    (d/'requirement.md').write_text(req)
    s={'task_id':args.task_id,'project_id':pr['project_id'],'title':args.title,'risk':risk,'state':'NEW',
       'iterations':{'planning':0,'security_design':0,'implementation':0,'verification':0,'security_audit':0,'documentation':0,'release':0},
       'history':[{'at':now(),'from':None,'to':'NEW','reason':'task initialized'}]}
    save(args.task_id,s); print(d)

def status(args): print(json.dumps(state(args.task_id),indent=2))

def next_stage(args):
    s=state(args.task_id); st=s['state']; risk=s['risk']
    m={'NEW':'PLANNING','PLANNING':'complete spec.md then SPEC_READY','SPEC_READY':'SECURITY_DESIGN' if risk!='LOW' else 'IMPLEMENTING (or SECURITY_DESIGN if project policy requires)',
       'SECURITY_DESIGN':'complete threat-model.md then SECURITY_DESIGN_READY','SECURITY_DESIGN_READY':'IMPLEMENTING','IMPLEMENTING':'complete code/tests + implementation-report.md then IMPLEMENTED',
       'IMPLEMENTED':'VERIFYING','VERIFYING':'produce verification report then ACCEPT/REJECT','VERIFICATION_REJECTED':'IMPLEMENTING unless the finding is a specification defect',
       'VERIFICATION_ACCEPTED':'SECURITY_AUDIT' if risk!='LOW' else 'DOCUMENTING or SECURITY_AUDIT if project policy requires','SECURITY_AUDIT':'produce security report then PASS/BLOCK',
       'SECURITY_BLOCKED':'IMPLEMENTING for code defect; PLANNING for design defect','SECURITY_PASSED':'DOCUMENTING','DOCUMENTING':'complete documentation report then DOCUMENTED',
       'DOCUMENTED':'RELEASE_GATE','RELEASE_GATE':'run gate --run-checks; RELEASED only on PASS','RELEASE_BLOCKED':'route to owning stage','RELEASED':'terminal'}
    print(m.get(st,'unknown'))

def transition(args):
    s=state(args.task_id); tr=read_json(TRANSITIONS); cur=s['state']
    if args.to not in tr.get(cur,[]): raise SystemExit(f'Invalid transition {cur} -> {args.to}; allowed={tr.get(cur,[])}')
    prev=cur; s['state']=args.to
    keys={'PLANNING':'planning','SECURITY_DESIGN':'security_design','IMPLEMENTING':'implementation','VERIFYING':'verification','SECURITY_AUDIT':'security_audit','DOCUMENTING':'documentation','RELEASE_GATE':'release'}
    if args.to in keys: s['iterations'][keys[args.to]]=s['iterations'].get(keys[args.to],0)+1
    s['history'].append({'at':now(),'from':prev,'to':args.to,'reason':args.reason or 'transition'})
    save(args.task_id,s); print(f'{args.task_id}: {prev} -> {args.to}')

def handoff(args):
    s=state(args.task_id); d=td(args.task_id); manifest=CORE/'manifests'/f'{args.agent}.md'
    if not manifest.exists(): raise SystemExit('Unknown agent')
    common=[PROJECT/'project-profile.json',PROJECT/'architecture.md',PROJECT/'domain.md',PROJECT/'invariants.md',PROJECT/'conventions.md',PROJECT/'security-boundaries.md']
    task_files={'planner':['requirement.md'],'security':['requirement.md','spec.md','threat-model.md','implementation-report.md','verification-report.md'],
      'implementer':['requirement.md','spec.md','threat-model.md','verification-report.md','security-report.md'],
      'verifier':['requirement.md','spec.md','threat-model.md','implementation-report.md'],
      'documenter':['spec.md','implementation-report.md','verification-report.md','security-report.md'],
      'release':['spec.md','threat-model.md','implementation-report.md','verification-report.md','security-report.md','documentation-report.md'],
      'orchestrator':['requirement.md']}.get(args.agent,[])
    out=[f'# Handoff — {args.task_id} → {args.agent}','', '## State','```json',json.dumps(s,indent=2),'```','', '## Role manifest',manifest.read_text()]
    for p in common:
        if p.exists(): out += ['',f'## Project context: {p.name}',p.read_text()]
    for name in task_files:
        p=d/name
        if p.exists(): out += ['',f'## Task artifact: {name}',p.read_text()]
    dest=d/f'handoff-{args.agent}-{s["state"].lower()}.md'; dest.write_text('\n'.join(out)+'\n'); print(dest)

def verdict(path):
    if not path.exists(): return None
    for line in path.read_text().splitlines():
        if line.startswith('Verdict:'):
            v=line.split(':',1)[1].strip()
            if v and v!='PENDING': return v
    return None

def run_cmds(kind):
    cfg=read_json(PROJECT/'commands.json'); cmds=cfg.get(kind,[]) or []
    results=[]
    for cmd in cmds:
        print(f'[{kind}] {cmd}')
        r=subprocess.run(cmd,shell=True,cwd=ROOT)
        results.append((cmd,r.returncode))
    return results

def gate(args):
    s=state(args.task_id); d=td(args.task_id); risk=s['risk']; failures=[]; evidence={}
    required=['requirement.md','spec.md','implementation-report.md','verification-report.md','documentation-report.md']
    if risk!='LOW': required += ['threat-model.md','security-report.md']
    missing=[f for f in required if not (d/f).exists() or (d/f).stat().st_size<20]
    if missing: failures += [f'missing_or_empty:{x}' for x in missing]
    vv=verdict(d/'verification-report.md'); evidence['verification_verdict']=vv
    if vv not in ('ACCEPT','ACCEPT_WITH_MINOR_ISSUES'): failures.append('verification_not_accepted')
    if risk!='LOW':
        sv=verdict(d/'security-report.md'); evidence['security_verdict']=sv
        if sv not in ('PASS','PASS_WITH_LOW_MEDIUM_FINDINGS'): failures.append('security_not_accepted')
    command_results={}
    if args.run_checks:
        for kind in ['test','typecheck','lint']:
            rs=run_cmds(kind); command_results[kind]=rs
            if any(code for _,code in rs): failures.append(f'{kind}_failed')
        if args.e2e:
            rs=run_cmds('e2e'); command_results['e2e']=rs
            if any(code for _,code in rs): failures.append('e2e_failed')
    evidence['commands']=command_results
    result={'task':args.task_id,'project':s['project_id'],'pass':not failures,'failures':failures,'evidence':evidence}
    print(json.dumps(result,indent=2))
    if failures: sys.exit(2)

def parser():
    p=argparse.ArgumentParser(prog='nomphi'); sub=p.add_subparsers(dest='cmd',required=True)
    x=sub.add_parser('project-init'); x.add_argument('--id',required=True); x.add_argument('--name',required=True); x.add_argument('--type',default='other'); x.add_argument('--default-risk',default='MEDIUM',choices=sorted(RISKS)); x.set_defaults(func=init_project)
    x=sub.add_parser('task-init'); x.add_argument('task_id'); x.add_argument('--title',required=True); x.add_argument('--risk',choices=sorted(RISKS)); x.set_defaults(func=task_init)
    x=sub.add_parser('status'); x.add_argument('task_id'); x.set_defaults(func=status)
    x=sub.add_parser('next'); x.add_argument('task_id'); x.set_defaults(func=next_stage)
    x=sub.add_parser('transition'); x.add_argument('task_id'); x.add_argument('to'); x.add_argument('--reason'); x.set_defaults(func=transition)
    x=sub.add_parser('handoff'); x.add_argument('task_id'); x.add_argument('agent',choices=['orchestrator','planner','implementer','verifier','security','documenter','release']); x.set_defaults(func=handoff)
    x=sub.add_parser('gate'); x.add_argument('task_id'); x.add_argument('--run-checks',action='store_true'); x.add_argument('--e2e',action='store_true'); x.set_defaults(func=gate)
    return p

def main():
    a=parser().parse_args(); a.func(a)
if __name__=='__main__': main()
