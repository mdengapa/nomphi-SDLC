import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProjectIdentifierVerificationTests(unittest.TestCase):
    def bootstrap(self, directory):
        return subprocess.run(
            [str(ROOT / 'bootstrap.sh'), directory, '--name', 'Verification Project', '--id', 'verify-project'],
            capture_output=True,
            text=True,
        )

    def cli(self, target):
        return ['python3', str(target / 'scripts' / 'nomphi.py')]

    def agent_cli(self, target):
        return ['python3', str(target / 'scripts' / 'nomphi_agent.py')]

    def create_task(self, target):
        result = subprocess.run(
            self.cli(target) + ['task-init', 'TEST_01', '--title', 'Verifier task', '--risk', 'LOW'],
            cwd=target,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return target / '.nomphi' / 'tasks' / 'TEST_01' / 'state.json'

    def test_non_string_task_project_ids_fail_before_all_operations_mutate(self):
        for project_id in [True, 1, [], {}]:
            with self.subTest(project_id=project_id), tempfile.TemporaryDirectory() as directory:
                target = Path(directory)
                self.assertEqual(self.bootstrap(directory).returncode, 0)
                state = self.create_task(target)
                data = json.loads(state.read_text())
                data['project_id'] = project_id
                state.write_text(json.dumps(data))
                before = state.read_bytes()
                commands = [
                    self.cli(target) + ['status', 'TEST_01'],
                    self.cli(target) + ['next', 'TEST_01'],
                    self.cli(target) + ['transition', 'TEST_01', 'PLANNING'],
                    self.agent_cli(target) + ['inspect', 'TEST_01'],
                ]
                for command in commands:
                    result = subprocess.run(command, cwd=target, capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0, command)
                    self.assertEqual(state.read_bytes(), before)

    def test_invalid_profile_blocks_read_only_task_operations(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(self.bootstrap(directory).returncode, 0)
            state = self.create_task(target)
            before = state.read_bytes()
            profile = target / '.nomphi' / 'project' / 'project-profile.json'
            data = json.loads(profile.read_text())
            data['project_id'] = 'INVALID'
            profile.write_text(json.dumps(data))
            for command in [
                self.cli(target) + ['status', 'TEST_01'],
                self.cli(target) + ['next', 'TEST_01'],
                self.agent_cli(target) + ['inspect', 'TEST_01'],
            ]:
                result = subprocess.run(command, cwd=target, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0, command)
                self.assertIn('HUMAN_DECISION_REQUIRED', result.stdout + result.stderr)
                self.assertEqual(state.read_bytes(), before)

    def test_task_id_grammar_and_existing_installation_guard_are_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(self.bootstrap(directory).returncode, 0)
            self.create_task(target)
            profile = target / '.nomphi' / 'project' / 'project-profile.json'
            before = profile.read_bytes()
            result = subprocess.run(
                [str(ROOT / 'bootstrap.sh'), directory, '--name', 'Changed', '--id', 'other-project'],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Refusing to overwrite existing', result.stderr)
            self.assertEqual(profile.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
