#!/usr/bin/env python3
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path
import json
import re

import nomphi

ROOT = Path(__file__).resolve().parents[1]

ACCEPT_VERDICTS = {'ACCEPT', 'ACCEPT_WITH_MINOR_ISSUES'}
REJECT_VERDICTS = {'REJECT', 'REJECTED', 'FAIL'}
SECURITY_PASS = {'PASS', 'PASS_WITH_LOW_MEDIUM_FINDINGS'}
SECURITY_BLOCK = {'BLOCK', 'BLOCKED', 'FAIL'}


def fail(message: str) -> None:
    raise SystemExit(message)


def section(text: str, heading: str) -> str:
    pattern = rf'^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)'
    m = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ''


def spec_grounding_issues(task_id: str) -> list[str]:
    path = nomphi.td(task_id) / 'spec.md'
    if not path.is_file():
        return ['missing spec.md']
    text = path.read_text(errors='replace')
    issues: list[str] = []

    if 'Status: COMPLETE' not in text:
        issues.append('spec status is not COMPLETE')
    if re.search(r'^\s*- \[x\]', text, flags=re.MULTILINE | re.IGNORECASE):
        issues.append('planning spec must not contain completed [x] checkboxes')

    evidence = section(text, 'Evidence / grounding')
    if not evidence or evidence.strip() in {'-', '- TBD'}:
        issues.append('Evidence / grounding is empty')

    evidence_paths: set[str] = set()
    for token in re.findall(r'`([^`]+)`', evidence):
        candidate = token.strip()
        if '/' in candidate or candidate.endswith(('.py','.ts','.tsx','.js','.json','.md','.yaml','.yml')):
            evidence_paths.add(candidate)
            if not (ROOT / candidate).exists():
                issues.append(f'evidence path does not exist: {candidate}')

    # Any concrete repository path asserted elsewhere must either exist or be explicitly proposed.
    for line in text.splitlines():
        if line.startswith('## Evidence / grounding'):
            continue
        for token in re.findall(r'`([^`]+)`', line):
            candidate = token.strip()
            looks_like_path = '/' in candidate or candidate.endswith(('.py','.ts','.tsx','.js','.json','.md','.yaml','.yml'))
            if not looks_like_path:
                continue
            if (ROOT / candidate).exists() or candidate in evidence_paths:
                continue
            if 'PROPOSED:' not in line:
                issues.append(f'nonexistent path must be marked PROPOSED: {candidate}')

    unknowns = section(text, 'Unknowns / decisions required')
    if 'UNKNOWN:' in unknowns and 'Status: COMPLETE' in text:
        material_words = ('architecture','invariant','contract','schema','endpoint','persistence','security','auth','migration')
        if any(word in unknowns.lower() for word in material_words):
            issues.append('material UNKNOWN requires Status: PENDING and HUMAN_DECISION_REQUIRED')

    template = nomphi.TEMPLATES / 'spec.md'
    if template.is_file():
        baseline = template.read_text(errors='replace')
        normalized = text.replace('Status: COMPLETE', 'Status: PENDING')
        if normalized.strip() == baseline.strip():
            issues.append('spec is unchanged from template')

    body = re.sub(r'^#.*$', '', text, flags=re.MULTILINE)
    body = re.sub(r'^Status:\s*COMPLETE\s*$', '', body, flags=re.MULTILINE)
    body = re.sub(r'^- \[ \]\s*$', '', body, flags=re.MULTILINE)
    if len(re.sub(r'\s+', '', body)) < 120:
        issues.append('spec lacks substantive content')

    return sorted(set(issues))


def spec_has_substance(task_id: str) -> bool:
    return not spec_grounding_issues(task_id)


def expected_agent(s: dict) -> str | None:
    route = dict(nomphi.ROUTE)
    if s['risk'] == 'LOW' and s['state'] == 'SPEC_READY':
        return 'implementer'
    if s['risk'] == 'LOW' and s['state'] == 'VERIFICATION_ACCEPTED':
        return 'documenter'
    return route.get(s['state'])


def next_transition(s: dict) -> tuple[str | None, str | None]:
    state = s['state']
    risk = s['risk']
    fixed = {
        'NEW': 'PLANNING',
        'PLANNING': 'SPEC_READY',
        'SPEC_READY': 'IMPLEMENTING' if risk == 'LOW' else 'SECURITY_DESIGN',
        'SECURITY_DESIGN': 'SECURITY_DESIGN_READY',
        'SECURITY_DESIGN_READY': 'IMPLEMENTING',
        'IMPLEMENTING': 'IMPLEMENTED',
        'IMPLEMENTED': 'VERIFYING',
        'VERIFICATION_REJECTED': 'IMPLEMENTING',
        'VERIFICATION_ACCEPTED': 'DOCUMENTING' if risk == 'LOW' else 'SECURITY_AUDIT',
        'SECURITY_PASSED': 'DOCUMENTING',
        'DOCUMENTING': 'DOCUMENTED',
        'DOCUMENTED': 'RELEASE_GATE',
    }
    if state in fixed:
        return fixed[state], None
    if state == 'VERIFYING':
        verdict = nomphi.verdict(nomphi.td(s['task_id']) / 'verification-report.md')
        if verdict in ACCEPT_VERDICTS:
            return 'VERIFICATION_ACCEPTED', None
        if verdict in REJECT_VERDICTS:
            return 'VERIFICATION_REJECTED', None
        return None, 'verification verdict is missing or ambiguous'
    if state == 'SECURITY_AUDIT':
        verdict = nomphi.verdict(nomphi.td(s['task_id']) / 'security-report.md')
        if verdict in SECURITY_PASS:
            return 'SECURITY_PASSED', None
        if verdict in SECURITY_BLOCK:
            return 'SECURITY_BLOCKED', None
        return None, 'security verdict is missing or ambiguous'
    if state in {'SECURITY_BLOCKED', 'RELEASE_BLOCKED'}:
        return None, 'routing requires ownership classification'
    if state == 'RELEASE_GATE':
        return None, 'release requires explicit gate execution'
    if state == 'RELEASED':
        return None, 'task is terminal'
    return None, f'no semantic transition defined for {state}'


def inspect_task(task_id: str) -> dict:
    nomphi.validate_adapter()
    s = nomphi.state(task_id)
    target, blocked = next_transition(s)
    requirements: list[str] = []
    if s['state'] == 'PLANNING':
        for issue in spec_grounding_issues(task_id):
            requirements.append('spec: ' + issue)
    for name in nomphi.PREREQ.get((s['state'], target), []) if target else []:
        if not nomphi.ready(task_id, name):
            requirements.append(f'complete {name}')
    return {
        'task_id': task_id,
        'state': s['state'],
        'risk': s['risk'],
        'next_transition': target,
        'handoff_target': expected_agent(s),
        'blocked_reason': blocked,
        'requirements': sorted(set(requirements)),
    }


def command_inspect(args: Namespace) -> None:
    print(json.dumps(inspect_task(args.task_id), indent=2))


def command_advance(args: Namespace) -> None:
    info = inspect_task(args.task_id)
    if info['blocked_reason']:
        fail('HUMAN_DECISION_REQUIRED: ' + info['blocked_reason'])
    if info['requirements']:
        fail('ADVANCE_BLOCKED: ' + '; '.join(info['requirements']))
    target = info['next_transition']
    if not target:
        fail('HUMAN_DECISION_REQUIRED: no deterministic next transition')
    nomphi.transition(Namespace(task_id=args.task_id, to=target, reason='semantic advance'))
    print(json.dumps(inspect_task(args.task_id), indent=2))


def command_route(args: Namespace) -> None:
    info = inspect_task(args.task_id)
    agent = info['handoff_target']
    if not agent:
        fail('HUMAN_DECISION_REQUIRED: no deterministic handoff target')
    nomphi.handoff(Namespace(task_id=args.task_id, agent=agent))
    print(json.dumps({'task_id': args.task_id, 'state': info['state'], 'handoff_target': agent}, indent=2))


def command_create(args: Namespace) -> None:
    nomphi.task_init(Namespace(task_id=args.task_id, title=args.title, risk=args.risk))
    print(json.dumps(inspect_task(args.task_id), indent=2))


def command_doctor(_: Namespace) -> None:
    nomphi.doctor(Namespace())


def parser() -> ArgumentParser:
    p = ArgumentParser(prog='nomphi-agent', description='Semantic fail-closed API for autonomous agents')
    sub = p.add_subparsers(dest='cmd', required=True)
    x = sub.add_parser('doctor'); x.set_defaults(func=command_doctor)
    x = sub.add_parser('create'); x.add_argument('task_id'); x.add_argument('--title', required=True); x.add_argument('--risk', choices=sorted(nomphi.RISKS)); x.set_defaults(func=command_create)
    x = sub.add_parser('inspect'); x.add_argument('task_id'); x.set_defaults(func=command_inspect)
    x = sub.add_parser('advance'); x.add_argument('task_id'); x.set_defaults(func=command_advance)
    x = sub.add_parser('route'); x.add_argument('task_id'); x.set_defaults(func=command_route)
    return p


def main() -> None:
    args = parser().parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
