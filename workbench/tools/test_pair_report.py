"""Offline opponent splits and Discord summaries for pair reports."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pair_report as report


def row(win, us, them):
    return dict(win=win, us=us, them=them)


class PairReport(unittest.TestCase):
    def run_report(self, new, pool, opponents=None, old=None, post=True, old_only=False, versions=False,
                   rollback=None, hashes=None):
        st = {'rollback': rollback or {'id': 42}, 'old_only': old_only}
        if versions:
            st.update(ref='saved card', halves={'new': {'submission': {'version': 43}},
                                             'old': {'submission': {'version': 42}}})
        if opponents is not None:
            st['opponents'] = [{'name': name} for name in opponents]
        with tempfile.TemporaryDirectory() as root:
            smoke = Path(root) / 'data/online/smoke'
            smoke.mkdir(parents=True)
            guide = Path(root) / 'data/guide'
            guide.mkdir(parents=True)
            output = io.StringIO()
            with patch.object(report, 'ROOT', root), patch.object(report, 'SMOKE', str(smoke)), \
                 patch.object(report, 'state', return_value=st), \
                 patch.object(report, 'source_hashes', return_value=dict(hashes or {})), \
                 patch.object(report, 'load', side_effect=[new, old or {}]) as load, \
                 patch.object(report, 'baseline', return_value=(pool, [('earlier', 1, 60)])) as baseline, \
                 patch.object(report.subprocess, 'run') as run, contextlib.redirect_stdout(output):
                report.main(['pair_report.py', 'sample'] + (['--post', 'card'] if post else []))
            load.assert_any_call('sample', st, 'new')
            load.assert_any_call('sample', st, 'old')
            expected = dict(hashes or {})
            if st['rollback'].get('source_hash'):
                expected[str(st['rollback']['id'])] = st['rollback']['source_hash']
            baseline.assert_called_once_with(st['rollback']['id'], old if old_only else new, expected)
            text = output.getvalue()
            self.assertEqual((smoke / 'sample-result.txt').read_text(), text)
            if post:
                run.assert_called_once()
                self.assertEqual(run.call_args.args[0][-1], str(guide / 'res-sample.txt'))
                message = (guide / 'res-sample.txt').read_text().rstrip('\n')
            else:
                run.assert_not_called()
                self.assertFalse((guide / 'res-sample.txt').exists())
                message = None
            return text, message

    def test_live_only_text_and_message(self):
        old = {('test4', 'm'): row(1, 20, 5), ('WeHaveQuizzes', 'm'): row(0, 10, 30)}
        pool = {('test4', 'm'): [row(1, 20, 5)] * 3,
                ('WeHaveQuizzes', 'm'): [row(0, 10, 30)] * 2}
        text, message = self.run_report({}, pool, ['test4', 'WeHaveQuizzes'], old=old, old_only=True)
        self.assertIn('live bot 2 games | wins: 1/2', text)
        self.assertIn('our avg score 15.0 | their avg score 17.5', text)
        self.assertIn('vs test4: wins live 1/1 | our avg score 20.0 | their avg score 5.0 | pooled wins 15.0/15 | pooled games 3', text)
        self.assertIn('pooled games 2', text)
        self.assertEqual(message.count('```'), 2)
        self.assertIn('no bot swap or upload', message)
        self.assertNotIn('wins new', message)
        block = message.split('```')[1].strip().splitlines()
        for line in block[1:]:
            self.assertEqual(line.index('/1') - 1, block[0].index('wins this run'))
        self.assertLess(message.index('test4'), message.index('WeHaveQuizzes'))
        text, message = self.run_report({}, pool, old=old, old_only=True, post=False)
        self.assertIsNone(message)

    def test_live_only_baseline_includes_current_complete_run(self):
        old = {('test4', 'm'): row(1, 20, 5)}
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'current.json'
            st = dict(kind='pair', old_only=True, phase='rolled-back', halves={
                'old': dict(submission={'id': 42}, batches=[{'maps': [1]}], battle_ids=[123]),
                'new': dict(submission=None, battle_ids=[])})
            path.write_text(json.dumps(st))
            with patch.object(report, 'SMOKE', root), patch.object(report, 'load', return_value=old):
                pool, runs = report.baseline(42, old)
            self.assertEqual(pool, {('test4', 'm'): [old[('test4', 'm')]]})
            self.assertEqual(runs, [('current', 1, 1)])

    def smoke_dir(self, root, runs):
        for name, sub in runs.items():
            st = dict(kind='pair', phase='rolled-back', halves={
                'old': dict(submission=sub, batches=[{'maps': [1]}], battle_ids=[123]),
                'new': dict(submission=None, battle_ids=[])})
            (Path(root) / (name + '.json')).write_text(json.dumps(st))

    def pooled(self, live_id, runs, hashes=None):
        old = {('test4', 'm'): row(1, 20, 5)}
        with tempfile.TemporaryDirectory() as root:
            self.smoke_dir(root, runs)
            with patch.object(report, 'SMOKE', root), patch.object(report, 'load', return_value=old), \
                 patch.object(report.subprocess, 'run') as run:
                pool, used = report.baseline(live_id, old) if hashes is None else report.baseline(live_id, old, hashes)
            run.assert_not_called()
        return [name for name, _, _ in used], len(pool.get(('test4', 'm'), []))

    def test_baseline_recorded_under_a_sibling_copy_is_found(self):
        runs = {'under-v44': {'id': 44}, 'under-v47': {'id': 47}, 'other-code': {'id': 45}, 'unknown': {'id': 30}}
        hashes = {'44': 'main', '47': 'main', '45': 'card', '48': 'main'}
        self.assertEqual(self.pooled(47, runs, hashes), (['under-v44', 'under-v47'], 2))
        self.assertEqual(self.pooled(44, runs, hashes), (['under-v44', 'under-v47'], 2))
        self.assertEqual(self.pooled(48, runs, hashes), (['under-v44', 'under-v47'], 2))
        self.assertEqual(self.pooled(45, runs, hashes), (['other-code'], 1))

    def test_baseline_without_hashes_stays_keyed_by_id(self):
        runs = {'under-v44': {'id': 44}, 'under-v47': {'id': 47}}
        self.assertEqual(self.pooled(47, runs), (['under-v47'], 1))
        self.assertEqual(self.pooled(47, runs, {}), (['under-v47'], 1))
        self.assertEqual(self.pooled(47, runs, {'44': 'main'}), (['under-v47'], 1))
        self.assertEqual(self.pooled(47, runs, {'47': 'main'}), (['under-v47'], 1))
        self.assertEqual(self.pooled(47, runs, {'44': 'main', '47': 'card'}), (['under-v47'], 1))
        self.assertEqual(self.pooled(30, {'no-id': {}, 'none': None}, {'30': 'main'}), ([], 0))

    def test_baseline_uses_the_hash_saved_in_the_run(self):
        runs = {'under-v44': {'id': 44, 'source_hash': 'main'}, 'other-code': {'id': 45, 'source_hash': 'card'}}
        self.assertEqual(self.pooled(47, runs, {'47': 'main'}), (['under-v44'], 1))

    def test_report_looks_up_the_baseline_with_the_saved_hash(self):
        new, pool = self.fixture()
        self.run_report(new, pool, rollback={'id': 47, 'source_hash': 'main'}, hashes={'44': 'main'})
        self.run_report(new, pool, rollback={'id': 47}, hashes={'44': 'main', '47': 'main'})

    def test_source_hashes_merges_the_saved_map_with_the_server_list(self):
        rows = [{'id': 44, 'sourceHash': 'main'}, {'id': 47, 'sourceHash': 'main'}, {'id': 45, 'sourceHash': None}, {'id': 46}]
        with tempfile.TemporaryDirectory() as root:
            saved = Path(root) / 'data/online/source-hashes.json'
            saved.parent.mkdir(parents=True)
            saved.write_text(json.dumps({'30': 'old', '31': ''}))
            with patch.object(report, 'ROOT', root), patch.object(report.subprocess, 'run') as run:
                run.return_value.stdout = json.dumps(rows)
                self.assertEqual(report.source_hashes(), {'30': 'old', '44': 'main', '47': 'main'})
                command = run.call_args.args[0]
                self.assertEqual(command[2:], ['submissions', '--all', '--json'])
                self.assertEqual(json.loads(saved.read_text()), {'30': 'old', '44': 'main', '47': 'main'})
                for failure in ('fetch failed', '{"error": "x"}', '[1, 2]'):
                    run.return_value.stdout = failure
                    self.assertEqual(report.source_hashes(), {'30': 'old', '44': 'main', '47': 'main'})
                run.side_effect = report.subprocess.TimeoutExpired('node', 120)
                self.assertEqual(report.source_hashes(), {'30': 'old', '44': 'main', '47': 'main'})
                saved.unlink()
                self.assertEqual(report.source_hashes(), {})
                self.assertFalse(saved.exists())

    def test_live_only_message_cap(self):
        splits = [dict(opponent='opponent' + str(i), wins=8, n=15, live=7.5, games=60) for i in range(100)]
        message = report.live_only_message('x' * 3000, splits)
        self.assertLess(len(message), 1900)
        self.assertEqual(message.count('```'), 2)

    def fixture(self):
        new = {('test4', 'm'): row(1, 20, 5), ('WeHaveQuizzes', 'm'): row(0, 10, 30)}
        pool = {('test4', 'm'): [row(0, 4, 40)] * 30,
                ('WeHaveQuizzes', 'm'): [row(1, 30, 10)] * 30}
        return new, pool

    def test_two_opponents_text_and_message_in_run_order(self):
        new, pool = self.fixture()
        text, message = self.run_report(new, pool, ['test4', 'WeHaveQuizzes'])
        self.assertIn('vs test4: wins new 1/1 vs live 0.0/1 | our avg score 4.0 -> 20.0 | their avg score 40.0 -> 5.0', text)
        self.assertIn('vs WeHaveQuizzes: wins new 0/1 vs live 1.0/1 | our avg score 30.0 -> 10.0 | their avg score 10.0 -> 30.0', text)
        self.assertLess(text.index('vs test4:'), text.index('vs WeHaveQuizzes:'))
        self.assertIn('4.0 → 20.0', message)
        self.assertIn('30.0 → 10.0', message)
        self.assertTrue(message.startswith('📊 card online result, same teams + maps\n```\n'))
        self.assertNotIn('thin baseline', message)
        self.assertEqual(text.splitlines()[-1], '  m                  wins  1.0->1 | ours   34.0->  30 | theirs   50.0->  35')

    def test_versions_prefix_and_discord_message(self):
        new, pool = self.fixture()
        original, _ = self.run_report(new, pool, ['test4', 'WeHaveQuizzes'])
        text, message = self.run_report(new, pool, ['test4', 'WeHaveQuizzes'], versions=True)
        self.assertEqual(text, 'v43 = v42 main + card\n' + original)
        self.assertTrue(message.startswith('📊 v43 = v42 main + card, online result, same teams + maps\n'))
        self.assertIn('wins v43', message)
        self.assertIn('wins v42', message)
        self.assertIn('v42 baseline 60 games. about ±4 wins in 30 games is luck', message)
        text, message = self.run_report(new, pool, versions=True, post=False)
        self.assertTrue(text.startswith('v43 = v42 main + saved card\n'))
        self.assertIsNone(message)

    def test_partial_versions_fall_back(self):
        lines = ['new bot 0 games', 'our avg score 0.0 -> 0.0']
        original = report.discord_message('card', lines, [], 1, 0)
        for new, live in [(None, 'v42'), ('v43', None)]:
            self.assertEqual(report.discord_message('card', lines, [], 1, 0, new, live), original)

    def test_live_only_version_message(self):
        old = {('test4', 'm'): row(1, 20, 5)}
        pool = {('test4', 'm'): [row(1, 20, 5)]}
        original, _ = self.run_report({}, pool, old=old, old_only=True)
        text, message = self.run_report({}, pool, old=old, old_only=True, versions=True)
        self.assertEqual(text, original)
        self.assertTrue(message.startswith('📊 v42 main (card): baseline result. no bot swap or upload\n'))

    def test_column_alignment_and_truncated_unicode_names(self):
        names = ['상대이름' * 8, 'short']
        new = {(name, 'm'): row(1, 20, 5) for name in names}
        pool = {key: [row(0, 4, 40)] * 30 for key in new}
        _, message = self.run_report(new, pool, names)
        block = message.split('```')[1].strip().splitlines()
        column = block[0].index('wins new')
        for line in block[1:]:
            self.assertEqual(line.index('1/1' if not line.startswith('all ') else '2/2'), column)
        self.assertIn(names[0][:18], message)
        self.assertNotIn(names[0], message)

    def test_fallback_order_by_name(self):
        new, pool = self.fixture()
        text, message = self.run_report(new, pool)
        self.assertLess(text.index('vs WeHaveQuizzes:'), text.index('vs test4:'))
        self.assertLess(message.index('WeHaveQuizzes'), message.index('test4'))

    def test_single_opponent_has_text_split_but_no_message_split(self):
        new = {('test4', 'm'): row(1, 20, 5)}
        pool = {('test4', 'm'): [row(0, 4, 40)] * 45}
        text, message = self.run_report(new, pool, ['test4'])
        self.assertIn('vs test4: wins new 1/1 vs live 0.0/1', text)
        self.assertNotIn('\nall ', message)
        self.assertIn('\ntest4 ', message)
        self.assertNotIn('thin baseline', message)

    def test_opponent_without_baseline(self):
        new, pool = self.fixture()
        del pool[('WeHaveQuizzes', 'm')]
        pool[('test4', 'm')] *= 2
        text, message = self.run_report(new, pool, ['test4', 'WeHaveQuizzes'])
        self.assertIn('no live baseline yet vs WeHaveQuizzes: new 0/1 wins, our avg score 10.0, theirs 30.0', text)
        self.assertNotIn('\nvs WeHaveQuizzes:', text)
        self.assertIn('WeHaveQuizzes', message)
        self.assertIn('- → 10.0', message)
        self.assertIn('- → 30.0', message)
        self.assertIn('thin for WeHaveQuizzes', message)

    def test_thin_baseline_counts_only_shared_keys(self):
        new, pool = self.fixture()
        pool[('test4', 'm')] = pool[('test4', 'm')][:2]
        pool[('WeHaveQuizzes', 'm')] = pool[('WeHaveQuizzes', 'm')][:3]
        pool[('test4', 'unplayed')] = [row(1, 100, 0)] * 100
        text, message = self.run_report(new, pool, ['test4', 'WeHaveQuizzes'])
        self.assertIn('live baseline pooled over 5 games', text)
        self.assertIn('live baseline 5 games (thin, under 45) · thin for test4, WeHaveQuizzes. about ±4 wins in 30 games is luck', message)
        self.assertNotIn('thin baseline', text)

    def test_pool_is_averaged_per_key_not_per_game(self):
        new = {('test4', 'm1'): row(1, 10, 20), ('test4', 'm2'): row(0, 30, 40)}
        pool = {('test4', 'm1'): [row(1, 100, 10)] * 40,
                ('test4', 'm2'): [row(0, 0, 30)] * 5}
        text, _ = self.run_report(new, pool)
        self.assertIn('vs test4: wins new 1/2 vs live 1.0/2 | our avg score 50.0 -> 20.0 | their avg score 20.0 -> 30.0', text)

    def test_this_run_only_unchanged_and_no_post(self):
        new, pool = self.fixture()
        old = {('test4', 'm'): row(0, 4, 40), ('WeHaveQuizzes', 'm'): row(1, 30, 10)}
        text, _ = self.run_report(new, pool, old=old, post=False)
        self.assertIn('this run only, 2 pairs | wins: live 1 -> new 1 (new only +1, live only -1)', text)

    def test_cap_drops_whole_opponents_from_end(self):
        names = [f'{i:02d}-' + 'x' * 120 for i in range(30)]
        new = {(name, 'm'): row(1, 20, 5) for name in names}
        pool = {key: [row(0, 4, 40)] * 30 for key in new}
        _, message = self.run_report(new, pool, names)
        self.assertLess(len(message), 1900)
        self.assertIn(names[0][:18], message)
        self.assertNotIn(names[-1][:18], message)
        self.assertIn('\n…\n```', message)
        present = [name[:18] in message for name in names]
        self.assertEqual(present, sorted(present, reverse=True))

    def test_cap_when_first_opponent_or_prefix_is_too_long(self):
        for names in [['x' * 2000, 'last'], ['first', 'last']]:
            new = {(name, 'm'): row(1, 20, 5) for name in names}
            pool = {key: [row(0, 4, 40)] * 30 for key in new}
            _, message = self.run_report(new, pool, names)
            self.assertLess(len(message), 1900)
            self.assertTrue(message.endswith('about ±4 wins in 30 games is luck'))
        message = report.discord_message('x' * 3000, ['new bot 0 games | wins: new 0/0 vs live 0.0/0', 'our avg score 0.0 -> 0.0'], [], 1, 0)
        self.assertLess(len(message), 1900)
        self.assertIn('…', message)


if __name__ == '__main__':
    unittest.main()
