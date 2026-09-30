"""Isolated behavioral tests; never reads or writes production projects."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import records


class RecordsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tasks = self.root / 'management/tasks'
        self.tasks.mkdir(parents=True)
        (self.root / 'receipt.json').write_text('{"result":"test fixture"}')

    def card(self, name='T-1', checked=True, **changes):
        data = dict(schema_version=1, id=name, type='task', project='P', title='Test',
                    status='done', owner='agent-a', created_at='2026-09-28T09:00:00+08:00',
                    updated_at='2026-09-29T09:00:00+08:00', parent=None, depends_on=[],
                    links=[], evidence=['receipt.json'], verified_at='2026-09-29T09:00:00+08:00')
        data.update(changes)
        path = self.tasks / (name + '.md')
        text = '---\n' + '\n'.join(k + ': ' + json.dumps(v) for k, v in data.items())
        text += '\n---\n## 验收清单\n- [' + ('x' if checked else ' ') + '] Confirm receipt\n'
        path.write_text(text)
        return path

    def report(self):
        return records.audit(self.root)

    def test_valid_done_and_no_mutation(self):
        self.card()
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob('*') if p.is_file()}
        report, cards = self.report()
        self.assertEqual(report['errors'], [])
        self.assertIn('- [x] T-1', records.render_todo(report, cards))
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob('*') if p.is_file()})

    def test_done_missing_evidence(self):
        self.card(evidence=[])
        self.assertTrue(any('requires evidence' in e for e in self.report()[0]['errors']))

    def test_unchecked_acceptance(self):
        self.card(checked=False)
        report, cards = self.report()
        self.assertTrue(report['errors'])
        with self.assertRaises(ValueError):
            records.render_todo(report, cards)

    def test_no_acceptance(self):
        path = self.card()
        path.write_text(path.read_text().replace('- [x] Confirm receipt', 'No checks'))
        self.assertTrue(self.report()[0]['errors'])

    def test_duplicate_id(self):
        self.card()
        self.card('T-2', id='T-1')
        self.assertIn('duplicate task ID: T-1', self.report()[0]['errors'])

    def test_dependency_cycle(self):
        self.card(depends_on=['T-2'])
        self.card('T-2', depends_on=['T-1'])
        self.assertTrue(any('dependency cycle' in e for e in self.report()[0]['errors']))

    def test_self_dependency(self):
        self.card(depends_on=['T-1'])
        self.assertTrue(any('cycle' in e for e in self.report()[0]['errors']))

    def test_parent_cycle(self):
        self.card(parent='T-2')
        self.card('T-2', parent='T-1')
        self.assertTrue(any('parent cycle' in e for e in self.report()[0]['errors']))

    def test_unresolved_dependency(self):
        self.card(depends_on=['T-404'])
        self.assertTrue(any('unresolved dependency' in e for e in self.report()[0]['errors']))

    def test_owner_required(self):
        self.card(status='doing', owner=None)
        self.assertTrue(any('requires an owner' in e for e in self.report()[0]['errors']))

    def test_pause_cancel_not_done(self):
        self.card(status='paused', checked=False, verified_at=None)
        self.card('T-2', status='cancelled', checked=False, verified_at=None)
        report, cards = self.report()
        self.assertFalse(report['errors'])
        rendered = records.render_todo(report, cards)
        self.assertNotIn('- [x]', rendered)
        self.assertIn('## cancelled', rendered)
        self.assertIn('## paused', rendered)

    def test_missing_local_evidence(self):
        self.card(evidence=['absent.json'])
        self.assertTrue(any('missing local evidence' in e for e in self.report()[0]['errors']))

    def test_remote_evidence_not_verified(self):
        self.card(evidence=['ssh://server/receipt.json'])
        report, _ = self.report()
        self.assertFalse(report['errors'])
        self.assertTrue(any('unverified' in w for w in report['warnings']))

    def test_metadata_format_and_duplicate_key(self):
        path = self.card()
        good = path.read_text()
        for bad in (good.replace('owner: "agent-a"', 'owner: agent-a'),
                    good.replace('owner: "agent-a"', 'owner: "agent-a"\nowner: "agent-b"')):
            path.write_text(bad)
            self.assertTrue(self.report()[0]['errors'])

    def test_path_escape(self):
        report, _ = records.audit(self.root, '../')
        self.assertTrue(report['errors'])
        report, _ = records.audit(self.root, str(self.tasks))
        self.assertTrue(report['errors'])

    def test_symlink_not_read(self):
        with tempfile.TemporaryDirectory() as other:
            secret = Path(other) / 'other.md'
            secret.write_text('not task data')
            (self.tasks / 'escape.md').symlink_to(secret)
            report, cards = self.report()
            self.assertFalse(cards)
            self.assertTrue(any('symlink' in e for e in report['errors']))

    def test_external_evidence_not_inspected(self):
        self.card(evidence=['../other-project/result.json'])
        report, _ = self.report()
        self.assertFalse(report['errors'])
        self.assertTrue(any('not inspected' in w for w in report['warnings']))

    def test_empty_project_unknown(self):
        report, _ = self.report()
        self.assertFalse(report['errors'])
        self.assertTrue(any('unknown' in w for w in report['warnings']))

    def test_timezone_required(self):
        self.card(updated_at='2026-09-29T09:00:00')
        self.assertTrue(any('timezone' in e for e in self.report()[0]['errors']))

    def test_fenced_example_not_acceptance(self):
        path = self.card()
        path.write_text(path.read_text().replace('- [x] Confirm receipt', '```md\n- [x] Example\n```'))
        self.assertTrue(self.report()[0]['errors'])

    def test_custom_task_mapping(self):
        self.card()
        self.tasks.rename(self.root / 'existing-tasks')
        report, _ = records.audit(self.root, 'existing-tasks')
        self.assertFalse(report['errors'])
        self.assertEqual(report['task_count'], 1)

    def test_stale_verification(self):
        self.card(verified_at='2026-09-28T20:00:00+08:00')
        self.assertTrue(any('freshness' in w for w in self.report()[0]['warnings']))


if __name__ == '__main__':
    unittest.main()
