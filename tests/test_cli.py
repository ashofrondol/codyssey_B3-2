"""채점 실행 경로(`python main.py`)를 실제로 띄워서 확인하는 검사.

README `0.10` 의 '🧪 실행 검증 기록' 은 사람이 한 번 손으로 돌린 기록이다.
기록은 다시 돌지 않는다. 같은 세션을 여기서 자동으로 재생해, REPL 이 죽거나
출력 형식이 바뀌면 빨간 불이 뜨게 한다.

`python` 대신 `sys.executable` 을 쓴다 — 실행 파일 이름은 환경마다 다르지만
(`python` / `python3`), 확인하려는 것은 "`main.py` 를 인터프리터에 그대로 넘기면
REPL 이 뜨는가" 이기 때문이다.
"""

import contextlib
import io
import os
import subprocess
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRY_POINT = os.path.join(REPO_ROOT, 'main.py')


def run_repl(*lines, timeout=30):
    """REPL 에 명령을 한 줄씩 넣고 (stdout, returncode) 를 돌려준다."""
    stdin = ''.join(line + '\n' for line in lines)
    completed = subprocess.run(
        [sys.executable, ENTRY_POINT],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=timeout,
    )
    return completed


class EntryPointTest(unittest.TestCase):
    def test_entry_point_exists(self):
        """README 「실행」 절이 안내하는 `python main.py` 의 대상 파일."""
        self.assertTrue(os.path.isfile(ENTRY_POINT), 'main.py 가 저장소 루트에 없다')

    def test_repl_starts_and_exits_cleanly(self):
        result = run_repl('exit')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Mini Git.', result.stdout)
        self.assertIn('mini-git> ', result.stdout)
        self.assertEqual(result.stderr, '')

    def test_quit_also_exits(self):
        self.assertEqual(run_repl('quit').returncode, 0)

    def test_exit_really_breaks_the_loop(self):
        """`exit` 이 정말 루프를 끊는지.

        `run_repl('exit')` 만으로는 아무것도 증명하지 못한다. 마지막 줄 뒤에서
        stdin 이 닫히므로 종료어를 통째로 지워도 EOF 처리가 대신 0 으로 끝내준다
        (실제로 종료 조건을 없애는 돌연변이를 넣어도 검사가 전부 통과했다).
        그래서 종료어 *뒤에* 출력이 뚜렷한 명령을 붙이고, 그 출력이 **없어야**
        한다고 본다. 대조군으로 같은 명령이 단독일 때는 출력이 나오는지 먼저 확인해
        '명령이 원래 조용해서 통과'하는 공회전을 막는다.
        """
        control = run_repl('init Zed')
        self.assertIn('Initialized repository.', control.stdout, '대조군이 조용하면 이 검사는 무의미하다')

        for word in ('exit', 'quit'):
            with self.subTest(word=word):
                result = run_repl(word, 'init Zed')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn(
                    'Initialized repository.',
                    result.stdout,
                    f'{word!r} 뒤의 명령이 실행됐다 — 종료어가 루프를 끊지 못한다',
                )

    def test_eof_without_exit_does_not_crash(self):
        """stdin 이 그냥 닫혀도 (Ctrl-D) 트레이스백 없이 끝나야 한다."""
        result = run_repl()
        self.assertEqual(result.returncode, 0)
        self.assertNotIn('Traceback', result.stderr)


class ReplSessionTest(unittest.TestCase):
    """README 0.10 🧪 절의 세션을 그대로 재생한다."""

    def setUp(self):
        self.result = run_repl(
            'init "Alice Kim"',
            'commit "Initial commit"',
            'branch feature',
            'switch feature',
            'COMMIT "Add login feature"',        # 대문자 명령 — R1-1
            'switch main',
            'commit "Add payment FEATURE"',
            'log',
            'log --sort-by=date',
            'log --sort-by=author',
            'search LOGIN',
            'search feature',
            'search "--author=Alice Kim"',
            'search --author=Nobody',
            'exit',
        )
        self.out = self.result.stdout

    def test_session_survives(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.assertNotIn('Traceback', self.result.stderr)

    def test_init_reports_branch_and_user_with_spaces(self):
        """R1-2/R1-3: 따옴표로 감싼 공백 포함 인자."""
        self.assertIn('Initialized repository.', self.out)
        self.assertIn('Current branch: main', self.out)
        self.assertIn('Current user: Alice Kim', self.out)

    def test_uppercase_command_works(self):
        """R1-1: 대문자 COMMIT 도 동작해야 한다."""
        self.assertIn('[feature ', self.out)
        self.assertIn('Add login feature', self.out)

    def test_log_prints_parents_before_children(self):
        """R5-5: 분기 그래프에서도 부모가 자식보다 먼저 나온다."""
        first = self.out.index('Initial commit')
        self.assertLess(first, self.out.index('Add login feature'))
        self.assertLess(first, self.out.index('Add payment FEATURE'))

    def test_log_marks_current_branches(self):
        self.assertIn('[feature]', self.out)
        self.assertIn('[main]', self.out)

    def test_search_is_case_insensitive_and_deduped(self):
        """R3-2: `search LOGIN` 이 'Add login feature' 를 찾는다."""
        self.assertIn('Found 1 commit:', self.out)     # LOGIN
        self.assertIn('Found 2 commits:', self.out)    # feature / FEATURE
        self.assertIn('Found 3 commits:', self.out)    # --author=Alice Kim
        self.assertIn('Found 0 commits.', self.out)    # --author=Nobody


class ErrorPathTest(unittest.TestCase):
    """R1-5 / R6-2: 잘못된 입력에도 REPL 이 죽지 않고 표준 메시지를 낸다."""

    def setUp(self):
        self.result = run_repl(
            'log',                              # INIT 전
            'init alice',
            'commit "root"',
            'branch',                           # 인자 개수 틀림
            'commit Add login feature',         # 따옴표 없음 → 인자 3개
            'commit "unclosed',                 # 닫히지 않은 따옴표
            'log --sort-by=xyz',                # 허용되지 않는 값
            'log --nope',                       # 모르는 옵션
            'switch nope',
            'ancestors deadbee',
            'path deadbee cafebab',
            'bogus arg',
            'exit',
        )
        self.out = self.result.stdout

    def test_repl_never_dies(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.assertNotIn('Traceback', self.result.stderr)

    def test_requires_init_first(self):
        self.assertIn('Repository not initialized. Run: INIT <user_name>', self.out)

    def test_standard_error_messages(self):
        self.assertGreaterEqual(self.out.count('Invalid args'), 4)
        self.assertIn('Unknown branch: nope', self.out)
        self.assertIn('Unknown commit: deadbee', self.out)
        self.assertIn('Unknown command: bogus', self.out)


class CommandOutputTest(unittest.TestCase):
    """`cmd_*` 핸들러의 출력 문구를 in-process 로 고정한다.

    커밋 hash 는 메시지·카운터·시각으로 만들어져 실행마다 달라진다. 그래서
    `PATH <hash> <hash>` 처럼 **앞선 출력에서 읽은 값을 인자로 넣어야 하는 명령**은
    stdin 을 미리 다 밀어넣는 서브프로세스 방식으로는 검사할 수 없다.
    여기서는 핸들러를 직접 부르고 stdout 을 가로채 같은 경로를 덮는다.
    """

    def setUp(self):
        sys.path.insert(0, REPO_ROOT)
        import main as minigit

        self.minigit = minigit
        self.repo = minigit.Repository()
        self.repo.init('Alice')

    def capture(self, handler, args):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            handler(self.repo, args)
        return buffer.getvalue()

    def diamond(self):
        """부모 2개짜리 merge 커밋이 있는 그래프 — CLI 로는 만들 수 없는 모양."""
        nodes = [
            ('aaaaaa1', 'root', 'alice', 100.0, []),
            ('bbbbbb2', 'left', 'alice', 101.0, ['aaaaaa1']),
            ('ccccc03', 'right', 'bob', 102.0, ['aaaaaa1']),
            ('ddddd04', 'merge', 'alice', 103.0, ['bbbbbb2', 'ccccc03']),
        ]
        for commit_hash, message, author, timestamp, parents in nodes:
            self.repo.commits[commit_hash] = self.minigit.Commit(
                commit_hash, message, author, timestamp, parents
            )
            self.repo.children.setdefault(commit_hash, [])
            for parent in parents:
                self.repo.children.setdefault(parent, []).append(commit_hash)

    def test_path_prints_lexicographically_smallest(self):
        self.diamond()
        self.assertEqual(
            self.capture(self.minigit.cmd_path, ['aaaaaa1', 'ddddd04']),
            'Path: aaaaaa1->bbbbbb2->ddddd04\n',
        )

    def test_path_prints_no_path_for_disconnected_commits(self):
        """R5-7: 경로가 없으면 `No path`."""
        self.diamond()
        self.repo.commits['eeeee05'] = self.minigit.Commit('eeeee05', 'lone', 'bob', 104.0, [])
        self.repo.children.setdefault('eeeee05', [])
        self.assertEqual(
            self.capture(self.minigit.cmd_path, ['aaaaaa1', 'eeeee05']),
            'No path\n',
        )

    def test_path_reports_unknown_commit(self):
        self.diamond()
        self.assertEqual(
            self.capture(self.minigit.cmd_path, ['aaaaaa1', 'deadbee']),
            'Unknown commit: deadbee\n',
        )
        self.assertEqual(
            self.capture(self.minigit.cmd_path, ['deadbee', 'aaaaaa1']),
            'Unknown commit: deadbee\n',
        )

    def test_path_rejects_wrong_arity(self):
        self.diamond()
        self.assertEqual(self.capture(self.minigit.cmd_path, ['aaaaaa1']), 'Invalid args\n')

    def test_ancestors_output(self):
        self.diamond()
        self.assertEqual(
            self.capture(self.minigit.cmd_ancestors, ['aaaaaa1']),
            '(no ancestors)\n',
        )
        printed = self.capture(self.minigit.cmd_ancestors, ['ddddd04'])
        self.assertEqual(
            [line.split()[0] for line in printed.splitlines()],
            ['aaaaaa1', 'bbbbbb2', 'ccccc03'],
            '조상은 (timestamp, hash) 오름차순으로 나와야 한다',
        )
        self.assertEqual(
            self.capture(self.minigit.cmd_ancestors, ['deadbee']),
            'Unknown commit: deadbee\n',
        )

    def test_log_orders_parents_before_children(self):
        self.diamond()
        printed = self.capture(self.minigit.cmd_log, [])
        order = [line.split()[1] for line in printed.splitlines() if line.startswith('commit ')]
        self.assertEqual(order, ['aaaaaa1', 'bbbbbb2', 'ccccc03', 'ddddd04'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
