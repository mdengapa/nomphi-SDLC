import json, subprocess, tempfile, shutil, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class CoreBoundaryTests(unittest.TestCase):
    def test_core_contains_no_known_project_names(self):
        forbidden=['CUADRA','Javier','Cristina','Belén','Belen','Mania de Playa']
        for p in (ROOT/'.nomphi'/'core').rglob('*'):
            if p.is_file():
                text=p.read_text(errors='ignore')
                for term in forbidden:
                    self.assertNotIn(term,text,f'{term} leaked into core file {p}')

    def test_examples_not_inside_core(self):
        self.assertTrue((ROOT/'examples'/'cuadra').exists())
        self.assertFalse((ROOT/'.nomphi'/'core'/'skills'/'cuadra-mobile-design').exists())

    def test_required_manifests(self):
        for n in ['orchestrator','planner','implementer','verifier','security','documenter','release']:
            self.assertTrue((ROOT/'.nomphi/core/manifests'/f'{n}.md').exists())

    def test_transition_config(self):
        data=json.loads((ROOT/'.nomphi/core/config/transitions.json').read_text())
        self.assertEqual(data['NEW'],['PLANNING'])
        self.assertIn('RELEASED',data['RELEASE_GATE'])

    def test_blank_project_profile_exists(self):
        p=json.loads((ROOT/'.nomphi/project/project-profile.json').read_text())
        self.assertEqual(p['project_id'],'REPLACE_ME')

class BootstrapTests(unittest.TestCase):
    def test_bootstrap_does_not_copy_examples(self):
        with tempfile.TemporaryDirectory() as td:
            subprocess.run([str(ROOT/'bootstrap.sh'),td,'--name','Test Project','--id','TEST'],check=True,capture_output=True,text=True)
            target=Path(td)
            self.assertTrue((target/'.nomphi/core').exists())
            self.assertEqual(json.loads((target/'.nomphi/project/project-profile.json').read_text())['project_id'],'TEST')
            self.assertFalse((target/'examples').exists())
            r=subprocess.run(['python3',str(target/'scripts/nomphi.py'),'task-init','TEST-001','--title','Smoke task','--risk','MEDIUM'],cwd=target,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            s=json.loads((target/'.nomphi/tasks/TEST-001/state.json').read_text())
            self.assertEqual(s['project_id'],'TEST')
            self.assertEqual(s['state'],'NEW')

if __name__=='__main__': unittest.main()
