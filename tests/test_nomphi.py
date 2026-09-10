import json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import nomphi

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

    def test_current_project_profile_has_canonical_identity(self):
        p=json.loads((ROOT/'.nomphi/project/project-profile.json').read_text())
        self.assertEqual(p['project_id'],'nomphi-sdlc')

class BootstrapTests(unittest.TestCase):
    def _bootstrap(self, td):
        subprocess.run([str(ROOT/'bootstrap.sh'),td,'--name','Test Project','--id','test-project'],check=True,capture_output=True,text=True)
        return Path(td)

    def _cli(self,target):
        return ['python3',str(target/'scripts/nomphi.py')]

    def _agent_cli(self,target):
        return ['python3',str(target/'scripts/nomphi_agent.py')]

    def test_bootstrap_does_not_copy_examples(self):
        with tempfile.TemporaryDirectory() as td:
            target=self._bootstrap(td)
            self.assertTrue((target/'.nomphi/core').exists())
            self.assertEqual(json.loads((target/'.nomphi/project/project-profile.json').read_text())['project_id'],'test-project')
            self.assertFalse((target/'examples').exists())
            r=subprocess.run(self._cli(target)+['task-init','TEST-001','--title','Smoke task','--risk','MEDIUM'],cwd=target,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            s=json.loads((target/'.nomphi/tasks/TEST-001/state.json').read_text())
            self.assertEqual(s['project_id'],'test-project')
            self.assertEqual(s['state'],'NEW')

    def test_uninitialized_adapter_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            target=self._bootstrap(td)
            p=target/'.nomphi/project/project-profile.json'
            data=json.loads(p.read_text()); data['project_id']='REPLACE_ME'; p.write_text(json.dumps(data))
            r=subprocess.run(self._cli(target)+['task-init','TEST-001','--title','Smoke task','--risk','LOW'],cwd=target,capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)
            self.assertIn('HUMAN_DECISION_REQUIRED',r.stderr+r.stdout)
            self.assertFalse((target/'.nomphi/tasks/TEST-001').exists())

    def test_invalid_task_id_cannot_escape_tasks_directory(self):
        with tempfile.TemporaryDirectory() as td:
            target=self._bootstrap(td)
            r=subprocess.run(self._cli(target)+['task-init','../EVIL','--title','Bad task','--risk','LOW'],cwd=target,capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)
            self.assertFalse((target/'.nomphi/EVIL').exists())

    def test_transition_requires_completed_spec(self):
        with tempfile.TemporaryDirectory() as td:
            target=self._bootstrap(td); cli=self._cli(target)
            subprocess.run(cli+['task-init','TEST-001','--title','Smoke task','--risk','LOW'],cwd=target,check=True,capture_output=True,text=True)
            subprocess.run(cli+['transition','TEST-001','PLANNING'],cwd=target,check=True,capture_output=True,text=True)
            r=subprocess.run(cli+['transition','TEST-001','SPEC_READY'],cwd=target,capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)
            self.assertIn('incomplete artifacts',r.stderr+r.stdout)

    def test_handoff_routing_is_enforced(self):
        with tempfile.TemporaryDirectory() as td:
            target=self._bootstrap(td); cli=self._cli(target)
            subprocess.run(cli+['task-init','TEST-001','--title','Smoke task','--risk','LOW'],cwd=target,check=True,capture_output=True,text=True)
            r=subprocess.run(cli+['handoff','TEST-001','implementer'],cwd=target,capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)
            self.assertIn('routes to planner',r.stderr+r.stdout)

    def test_semantic_advance_moves_new_to_planning(self):
        with tempfile.TemporaryDirectory() as td:
            target=self._bootstrap(td); agent=self._agent_cli(target)
            subprocess.run(agent+['create','TEST-001','--title','Smoke task','--risk','LOW'],cwd=target,check=True,capture_output=True,text=True)
            r=subprocess.run(agent+['advance','TEST-001'],cwd=target,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            s=json.loads((target/'.nomphi/tasks/TEST-001/state.json').read_text())
            self.assertEqual(s['state'],'PLANNING')

    def test_semantic_advance_rejects_status_only_spec(self):
        with tempfile.TemporaryDirectory() as td:
            target=self._bootstrap(td); agent=self._agent_cli(target)
            subprocess.run(agent+['create','TEST-001','--title','Smoke task','--risk','LOW'],cwd=target,check=True,capture_output=True,text=True)
            subprocess.run(agent+['advance','TEST-001'],cwd=target,check=True,capture_output=True,text=True)
            spec=target/'.nomphi/tasks/TEST-001/spec.md'
            spec.write_text(spec.read_text().replace('Status: PENDING','Status: COMPLETE'))
            r=subprocess.run(agent+['advance','TEST-001'],cwd=target,capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)
            self.assertIn('ADVANCE_BLOCKED',r.stderr+r.stdout)
            self.assertEqual(json.loads((target/'.nomphi/tasks/TEST-001/state.json').read_text())['state'],'PLANNING')

    def test_semantic_advance_and_route_low_risk(self):
        with tempfile.TemporaryDirectory() as td:
            target=self._bootstrap(td); agent=self._agent_cli(target)
            subprocess.run(agent+['create','TEST-001','--title','Smoke task','--risk','LOW'],cwd=target,check=True,capture_output=True,text=True)
            subprocess.run(agent+['advance','TEST-001'],cwd=target,check=True,capture_output=True,text=True)
            spec=target/'.nomphi/tasks/TEST-001/spec.md'
            spec.write_text('''# Technical Specification\n\nStatus: COMPLETE\n\n## Evidence / grounding\n- `AGENTS.nomphi.md` — repository-level Nomphi agent policy installed by bootstrap.\n\n## Objective\nValidate project identifiers before persistence.\n\n## Scope\nPROPOSED: add a pure validation helper with no side effects.\n\n## Proposed changes\nPROPOSED: validation helper; exact implementation path will be selected by the Implementer after repository inspection.\n\n## Unknowns / decisions required\nNone material for this isolated smoke-test task.\n\n## Acceptance criteria\n- [ ] Valid uppercase identifiers are accepted.\n- [ ] Invalid characters are rejected.\n- [ ] Empty input is rejected.\n\n## Tests required\n### Unit\n- [ ] Valid, invalid, empty, and boundary cases are covered.\n\n## Definition of Done\n- [ ] Implementation exists and all required tests pass.\n''')
            r=subprocess.run(agent+['advance','TEST-001'],cwd=target,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual(json.loads((target/'.nomphi/tasks/TEST-001/state.json').read_text())['state'],'SPEC_READY')
            r=subprocess.run(agent+['route','TEST-001'],cwd=target,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertTrue((target/'.nomphi/tasks/TEST-001/handoff-implementer-spec_ready.md').exists())

    def test_planner_rejects_completed_checkboxes(self):
        with tempfile.TemporaryDirectory() as td:
            target=self._bootstrap(td); agent=self._agent_cli(target)
            subprocess.run(agent+['create','TEST-001','--title','Smoke task','--risk','LOW'],cwd=target,check=True,capture_output=True,text=True)
            subprocess.run(agent+['advance','TEST-001'],cwd=target,check=True,capture_output=True,text=True)
            spec=target/'.nomphi/tasks/TEST-001/spec.md'
            spec.write_text('''# Technical Specification\n\nStatus: COMPLETE\n\n## Evidence / grounding\n- `AGENTS.nomphi.md`\n\n## Objective\nValidate project identifiers.\n\n## Scope\nPROPOSED: add validation.\n\n## Proposed changes\nPROPOSED: pure validation helper.\n\n## Unknowns / decisions required\nNone.\n\n## Acceptance criteria\n- [x] Invalid values are rejected.\n''')
            r=subprocess.run(agent+['advance','TEST-001'],cwd=target,capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)
            self.assertIn('must not contain completed [x] checkboxes',r.stderr+r.stdout)

    def test_planner_rejects_invented_repository_path(self):
        with tempfile.TemporaryDirectory() as td:
            target=self._bootstrap(td); agent=self._agent_cli(target)
            subprocess.run(agent+['create','TEST-001','--title','Smoke task','--risk','LOW'],cwd=target,check=True,capture_output=True,text=True)
            subprocess.run(agent+['advance','TEST-001'],cwd=target,check=True,capture_output=True,text=True)
            spec=target/'.nomphi/tasks/TEST-001/spec.md'
            spec.write_text('''# Technical Specification\n\nStatus: COMPLETE\n\n## Evidence / grounding\n- `AGENTS.nomphi.md`\n\n## Objective\nValidate project identifiers.\n\n## Scope\nAdd validation.\n\n## Files/modules likely affected\n- `src/services/fake-validator.ts`\n\n## Proposed changes\nPROPOSED: validation helper.\n\n## Unknowns / decisions required\nNone.\n\n## Acceptance criteria\n- [ ] Invalid values are rejected.\n''')
            r=subprocess.run(agent+['advance','TEST-001'],cwd=target,capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)
            self.assertIn('nonexistent path must be marked PROPOSED',r.stderr+r.stdout)

    def test_planner_ignores_markdown_heading_reference_as_path(self):
        with tempfile.TemporaryDirectory() as td:
            target=self._bootstrap(td); agent=self._agent_cli(target)
            subprocess.run(agent+['create','TEST-001','--title','Smoke task','--risk','LOW'],cwd=target,check=True,capture_output=True,text=True)
            subprocess.run(agent+['advance','TEST-001'],cwd=target,check=True,capture_output=True,text=True)
            spec=target/'.nomphi/tasks/TEST-001/spec.md'
            spec.write_text('''# Technical Specification\n\nStatus: COMPLETE\n\n## Evidence / grounding\n- `AGENTS.nomphi.md`\n\n## Existing context\nOnly state facts supported by `## Evidence / grounding`.\n\n## Objective\nValidate project identifiers.\n\n## Scope\nPROPOSED: add validation with no side effects.\n\n## Proposed changes\nPROPOSED: validation helper; exact path chosen after repository inspection.\n\n## Unknowns / decisions required\nNone.\n\n## Acceptance criteria\n- [ ] Valid identifiers are accepted.\n- [ ] Invalid identifiers are rejected.\n\n## Definition of Done\n- [ ] Implementation and tests pass.\n''')
            r=subprocess.run(agent+['advance','TEST-001'],cwd=target,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual(json.loads((target/'.nomphi/tasks/TEST-001/state.json').read_text())['state'],'SPEC_READY')

class ProjectIdentifierTests(unittest.TestCase):
    def _bootstrap(self, td, project_id='test-project'):
        return subprocess.run([str(ROOT/'bootstrap.sh'),td,'--name','Unrelated Name','--id',project_id],capture_output=True,text=True)

    def _cli(self, target):
        return ['python3',str(target/'scripts/nomphi.py')]

    def _agent_cli(self, target):
        return ['python3',str(target/'scripts/nomphi_agent.py')]

    def _task(self, target):
        subprocess.run(self._cli(target)+['task-init','TEST-001','--title','Smoke task','--risk','LOW'],cwd=target,check=True,capture_output=True,text=True)
        return target/'.nomphi/tasks/TEST-001/state.json'

    def test_project_id_predicate_accepts_only_approved_grammar(self):
        for value in ['a','0','a1','0a-1b','a-b-c','a'*1000]:
            self.assertTrue(nomphi.valid_project_id(value),value)
        for value in ['', 'A', 'a_B', 'a.b', 'a/b', 'a\\b', 'a b', '-a', 'a-', 'a--b', 'a\nb', 'cafe\u00e9', 'REPLACE_ME', None, True, 1, [], {}]:
            self.assertFalse(nomphi.valid_project_id(value),value)

    def test_schemas_use_the_approved_project_id_pattern(self):
        for name in ['project-profile.schema.json','task-state.schema.json']:
            schema=json.loads((ROOT/'.nomphi/core/schemas'/name).read_text())
            field=schema['properties']['project_id']
            self.assertEqual(field['type'],'string')
            self.assertEqual(field['pattern'],'^[a-z0-9]+(?:-[a-z0-9]+)*$')

    def test_initialization_validates_before_writing_and_preserves_identity(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td); self.assertEqual(self._bootstrap(td).returncode,0)
            profile=target/'.nomphi/project/project-profile.json'
            before=profile.read_bytes()
            for project_id in ['INVALID','bad_id','']:
                result=subprocess.run(self._cli(target)+['project-init','--id',project_id,'--name','Changed','--type','other'],cwd=target,capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0)
                self.assertNotIn('Initialized project adapter',result.stdout)
                self.assertEqual(profile.read_bytes(),before)
            result=subprocess.run(self._cli(target)+['project-init','--id','other-project','--name','Changed','--type','other'],cwd=target,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(profile.read_bytes(),before)
            result=subprocess.run(self._cli(target)+['project-init','--id','test-project','--name','Changed','--type','other'],cwd=target,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            updated=json.loads(profile.read_text())
            self.assertEqual(updated['project_id'],'test-project')
            self.assertEqual(updated['name'],'Changed')

    def test_uninitialized_profile_requires_explicit_valid_initialization(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td); self.assertEqual(self._bootstrap(td).returncode,0)
            profile=target/'.nomphi/project/project-profile.json'
            data=json.loads(profile.read_text()); data['project_id']='REPLACE_ME'; profile.write_text(json.dumps(data))
            result=subprocess.run(self._cli(target)+['project-init','--id','chosen-id','--name','Independent Name','--type','other'],cwd=target,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(profile.read_text())['project_id'],'chosen-id')

    def test_invalid_profile_values_fail_doctor_and_task_creation(self):
        for value in [None, True, 1, [], {}, '', 'REPLACE_ME', 'UPPER', 'bad_id', 'bad--id']:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as td:
                target=Path(td); self.assertEqual(self._bootstrap(td).returncode,0)
                profile=target/'.nomphi/project/project-profile.json'
                data=json.loads(profile.read_text()); data['project_id']=value; profile.write_text(json.dumps(data))
                doctor=subprocess.run(self._cli(target)+['doctor'],cwd=target,capture_output=True,text=True)
                self.assertNotEqual(doctor.returncode,0)
                self.assertIn('HUMAN_DECISION_REQUIRED',doctor.stdout+doctor.stderr)
                create=subprocess.run(self._cli(target)+['task-init','TEST-001','--title','Blocked','--risk','LOW'],cwd=target,capture_output=True,text=True)
                self.assertNotEqual(create.returncode,0)
                self.assertFalse((target/'.nomphi/tasks/TEST-001').exists())

    def test_task_state_identity_is_copied_and_all_loads_fail_closed(self):
        for replacement in [None, 'invalid_id', 'other-project']:
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory() as td:
                target=Path(td); self.assertEqual(self._bootstrap(td).returncode,0)
                state=self._task(target)
                data=json.loads(state.read_text())
                self.assertEqual(data['project_id'],'test-project')
                if replacement is None:
                    del data['project_id']
                else:
                    data['project_id']=replacement
                state.write_text(json.dumps(data))
                before=state.read_bytes()
                commands=[self._cli(target)+['status','TEST-001'],self._cli(target)+['next','TEST-001'],self._cli(target)+['transition','TEST-001','PLANNING'],self._agent_cli(target)+['inspect','TEST-001']]
                for command in commands:
                    result=subprocess.run(command,cwd=target,capture_output=True,text=True)
                    self.assertNotEqual(result.returncode,0,command)
                    self.assertEqual(state.read_bytes(),before)

    def test_bootstrap_uses_caller_identity_without_mutating_donor(self):
        source_profile=(ROOT/'.nomphi/project/project-profile.json').read_bytes()
        with tempfile.TemporaryDirectory(prefix='unrelated-directory-') as td:
            target=Path(td)
            result=self._bootstrap(td,'caller-chosen-id')
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual((ROOT/'.nomphi/project/project-profile.json').read_bytes(),source_profile)
            self.assertEqual(json.loads((target/'.nomphi/project/project-profile.json').read_text())['project_id'],'caller-chosen-id')
            self.assertEqual(subprocess.run(self._cli(target)+['doctor'],cwd=target,capture_output=True,text=True).returncode,0)
            state=self._task(target)
            self.assertEqual(json.loads(state.read_text())['project_id'],'caller-chosen-id')
            self.assertEqual(subprocess.run(self._cli(target)+['status','TEST-001'],cwd=target,capture_output=True,text=True).returncode,0)
            self.assertEqual(subprocess.run(self._agent_cli(target)+['inspect','TEST-001'],cwd=target,capture_output=True,text=True).returncode,0)

    def test_invalid_bootstrap_input_leaves_target_uninitialized_and_donor_unchanged(self):
        source_profile=(ROOT/'.nomphi/project/project-profile.json').read_bytes()
        with tempfile.TemporaryDirectory() as td:
            target=Path(td); result=self._bootstrap(td,'INVALID')
            self.assertNotEqual(result.returncode,0)
            self.assertEqual((ROOT/'.nomphi/project/project-profile.json').read_bytes(),source_profile)
            profile=json.loads((target/'.nomphi/project/project-profile.json').read_text())
            self.assertEqual(profile['project_id'],'REPLACE_ME')

if __name__=='__main__': unittest.main()
