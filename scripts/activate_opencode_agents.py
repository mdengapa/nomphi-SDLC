#!/usr/bin/env python3
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'.opencode'/'agents'
for src,dst in [('planner.template.md','planner.md'),('verifier.template.md','verifier.md'),('security.template.md','security.md')]:
    s=D/src; t=D/dst
    if t.exists(): print(f'skip {t}')
    else: shutil.copyfile(s,t); print(f'created {t}')
print('Bind the active external provider/model IDs in the generated files before use.')
