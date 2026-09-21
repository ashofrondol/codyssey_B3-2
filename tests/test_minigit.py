"""README 가 체크표로만 주장하던 불변식을 '실행되는 assert' 로 옮긴 검사.

배경: 이 저장소는 요구사항 30개를 README `0.10` 절의 ✅ 표로만 주장했고,
기계가 확인하는 검사는 0건이었다. 문서에만 적힌 규칙은 규칙이 아니라 희망이다.

여기서 고정하는 불변식 4개:
  (a) 위상 정렬  — LOG 순서에서 모든 부모가 자기 자식보다 앞에 온다 (R5-5)
  (b) 최단 경로  — 간선 수 최소, 동률이면 경로 문자열의 사전순 최소 (R5-7)
  (c) 정렬 안정성 — merge_sort 는 같은 key 의 상대 순서를 보존한다 (R4-1/R4-2)
  (d) 역색인    — SEARCH 결과가 전체 순회 결과와 정확히 같다 (R3-1~R3-3)

표준 라이브러리(unittest)만 쓴다. 두 가지로 모두 돌아간다:
    python3 -m unittest discover -s tests -v
    python3 tests/test_minigit.py
(pytest 가 있으면 `pytest -q` 로도 수집된다.)

과제 제약을 따라 이 파일도 `sorted()` / `list.sort()` 를 쓰지 않는다.
"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main as minigit  # noqa: E402


# --------------------------------------------------------------------------- #
# 합성 그래프 빌더
# --------------------------------------------------------------------------- #
def build_repo(nodes):
    """(hash, message, author, timestamp, parents) 목록으로 Repository 를 만든다.

    CLI 로는 부모가 2개인 커밋(merge)을 만들 수 없다. 그러나 `Commit.parents` 는
    리스트이고 알고리즘들은 다중 부모를 전제로 짜여 있으므로, 그 경로를 검사하려면
    그래프를 직접 구성해야 한다. `Repository.commit()` 과 같은 순서로 부속 구조를
    갱신한다 (commits / children / keyword_index / author_index).
    """
    repo = minigit.Repository()
    repo.init(nodes[0][2] if nodes else 'tester')
    for commit_hash, message, author, timestamp, parents in nodes:
        node = minigit.Commit(commit_hash, message, author, timestamp, parents)
        repo.commits[commit_hash] = node
        repo.children.setdefault(commit_hash, [])
        for parent in parents:
            repo.children.setdefault(parent, []).append(commit_hash)
        for token in message.split():
            repo.keyword_index.setdefault(token.lower(), []).append(commit_hash)
        repo.author_index.setdefault(author, []).append(commit_hash)
    return repo


def positions(order):
    """hash -> 출력 위치. 위상 정렬 판정에 쓴다."""
    return {h: i for i, h in enumerate(order)}


# --------------------------------------------------------------------------- #
# (a) 위상 정렬 — 부모가 자식보다 먼저
# --------------------------------------------------------------------------- #
class TopologicalLogTest(unittest.TestCase):
    """R5-5: LOG 는 부모 커밋이 항상 자식 커밋보다 먼저 출력돼야 한다."""

    def assert_parents_first(self, repo):
        order = repo.topological_log()
        self.assertEqual(
            len(order), len(repo.commits),
            '위상 정렬이 커밋을 누락했다 (사이클이거나 진입차수 계산 오류)',
        )
        self.assertEqual(len(set(order)), len(order), '같은 커밋이 두 번 출력됐다')
        pos = positions(order)
        for child_hash, commit in repo.commits.items():
            for parent_hash in commit.parents:
                self.assertLess(
                    pos[parent_hash], pos[child_hash],
                    f'부모 {parent_hash} 가 자식 {child_hash} 보다 뒤에 나왔다: {order}',
                )
        return order

    def test_branch_fork_via_public_cli_api(self):
        """실제 CLI 경로(INIT/COMMIT/BRANCH/SWITCH/COMMIT)로 만든 분기 그래프."""
        repo = minigit.Repository()
        repo.init('Alice Kim')
        repo.commit('Initial commit')
        repo.make_branch('feature')
        repo.switch('feature')
        repo.commit('Add login feature')
        repo.switch('main')
        repo.commit('Add payment FEATURE')
        self.assertEqual(len(repo.commits), 3)
        self.assert_parents_first(repo)

    def test_diamond_with_merge_commit(self):
        """부모가 2개인 merge 커밋이 있는 다이아몬드."""
        repo = build_repo([
            ('aaaaaa1', 'root', 'alice', 100.0, []),
            ('bbbbbb2', 'left', 'alice', 101.0, ['aaaaaa1']),
            ('ccccc03', 'right', 'bob', 102.0, ['aaaaaa1']),
            ('ddddd04', 'merge', 'alice', 103.0, ['bbbbbb2', 'ccccc03']),
        ])
        self.assertEqual(
            self.assert_parents_first(repo),
            ['aaaaaa1', 'bbbbbb2', 'ccccc03', 'ddddd04'],
        )

    def test_disconnected_roots(self):
        """부모 없는 루트가 2개인 포레스트에서도 전부 출력되고 순서가 지켜진다."""
        repo = build_repo([
            ('r000001', 'root A', 'alice', 100.0, []),
            ('r000002', 'root B', 'bob', 100.5, []),
            ('c000003', 'child of A', 'alice', 101.0, ['r000001']),
            ('c000004', 'child of B', 'bob', 101.5, ['r000002']),
        ])
        self.assert_parents_first(repo)

    def test_random_dag_60_nodes(self):
        """무작위 DAG 60개. 시드를 고정해 실패를 재현 가능하게 둔다."""
        rng = random.Random(20260921)
        nodes = []
        for i in range(60):
            parents = []
            if i:
                for _ in range(rng.randint(0, 2)):
                    candidate = 'n%05d' % rng.randrange(i)
                    if candidate not in parents:
                        parents.append(candidate)
            nodes.append(('n%05d' % i, 'msg%d' % i, 'author%d' % (i % 3), 100.0 + i, parents))
        self.assert_parents_first(build_repo(nodes))

    def test_tie_break_is_deterministic_and_lexicographic(self):
        """동률(같은 timestamp)이면 hash 가 작은 쪽을 먼저 — 문서가 주장하는 결정성.

        `c000002` 를 먼저 등록해 children 리스트의 '첫 번째'가 오답이 되도록 만들었다.
        따라서 최소 선택 비교가 뒤집히면 이 검사가 빨간 불을 낸다.
        """
        repo = build_repo([
            ('r000001', 'root', 'alice', 100.0, []),
            ('c000002', 'child c', 'alice', 200.0, ['r000001']),
            ('b000003', 'child b', 'alice', 200.0, ['r000001']),
        ])
        self.assertEqual(repo.topological_log(), ['r000001', 'b000003', 'c000002'])

    def test_repeated_calls_give_same_order(self):
        repo = build_repo([
            ('aaaaaa1', 'root', 'alice', 100.0, []),
            ('ccccc03', 'right', 'bob', 101.0, ['aaaaaa1']),
            ('bbbbbb2', 'left', 'alice', 101.0, ['aaaaaa1']),
        ])
        self.assertEqual(repo.topological_log(), repo.topological_log())


# --------------------------------------------------------------------------- #
# (b) 최단 경로 — 간선 수 최소, 동률이면 사전순 최소
# --------------------------------------------------------------------------- #
class ShortestPathTest(unittest.TestCase):
    """R5-7: 부모 간선을 무방향으로 본 최단 경로. 동률이면 사전순 최소."""

    def diamond(self):
        return build_repo([
            ('aaaaaa1', 'root', 'alice', 100.0, []),
            ('bbbbbb2', 'left', 'alice', 101.0, ['aaaaaa1']),
            ('ccccc03', 'right', 'bob', 102.0, ['aaaaaa1']),
            ('ddddd04', 'merge', 'alice', 103.0, ['bbbbbb2', 'ccccc03']),
        ])

    def test_diamond_picks_lexicographically_smallest(self):
        repo = self.diamond()
        self.assertEqual(
            repo.shortest_path('aaaaaa1', 'ddddd04'),
            'aaaaaa1->bbbbbb2->ddddd04',
        )

    def test_diamond_is_undirected(self):
        """자식 → 부모 방향으로도 같은 길이의 경로가 나와야 한다."""
        repo = self.diamond()
        self.assertEqual(
            repo.shortest_path('ddddd04', 'aaaaaa1'),
            'ddddd04->bbbbbb2->aaaaaa1',
        )

    def test_sibling_branches_go_through_common_parent(self):
        repo = self.diamond()
        self.assertEqual(
            repo.shortest_path('bbbbbb2', 'ccccc03'),
            'bbbbbb2->aaaaaa1->ccccc03',
        )

    def test_smallest_is_not_merely_the_first_one_found(self):
        """사전순 최소인 중간 노드를 '나중에' 등록해 삽입 순서 의존을 배제한다.

        `zzzzzz9` 를 먼저 등록했으므로, 인접 리스트를 훑다가 처음 찾은 경로를 그냥
        돌려주는 구현이면 `aaaaaa1->zzzzzz9->ddddd04` 가 나온다.
        """
        repo = build_repo([
            ('aaaaaa1', 'root', 'alice', 100.0, []),
            ('zzzzzz9', 'z side', 'alice', 101.0, ['aaaaaa1']),
            ('mmmmmm5', 'm side', 'alice', 102.0, ['aaaaaa1']),
            ('ddddd04', 'merge', 'alice', 103.0, ['zzzzzz9', 'mmmmmm5']),
        ])
        self.assertEqual(
            repo.shortest_path('aaaaaa1', 'ddddd04'),
            'aaaaaa1->mmmmmm5->ddddd04',
        )

    def test_edge_count_beats_lexicographic_order(self):
        """간선 수가 먼저다. 더 긴 경로가 사전순으로 더 작아도 고르면 안 된다.

        'aaaaaa1->aaaaaa2->ddddd04' < 'aaaaaa1->ddddd04' (사전순) 이지만
        정답은 1홉짜리 직접 경로다.
        """
        repo = build_repo([
            ('aaaaaa1', 'root', 'alice', 100.0, []),
            ('aaaaaa2', 'middle', 'alice', 101.0, ['aaaaaa1']),
            ('ddddd04', 'merge', 'alice', 102.0, ['aaaaaa1', 'aaaaaa2']),
        ])
        self.assertLess('aaaaaa1->aaaaaa2->ddddd04', 'aaaaaa1->ddddd04')
        self.assertEqual(repo.shortest_path('aaaaaa1', 'ddddd04'), 'aaaaaa1->ddddd04')

    def test_no_path_between_disconnected_roots(self):
        repo = build_repo([
            ('r000001', 'root A', 'alice', 100.0, []),
            ('r000002', 'root B', 'bob', 101.0, []),
        ])
        self.assertIsNone(repo.shortest_path('r000001', 'r000002'))

    def test_same_commit_returns_itself(self):
        repo = self.diamond()
        self.assertEqual(repo.shortest_path('aaaaaa1', 'aaaaaa1'), 'aaaaaa1')

    def test_unknown_commit_returns_none(self):
        repo = self.diamond()
        self.assertIsNone(repo.shortest_path('aaaaaa1', 'deadbee'))
        self.assertIsNone(repo.shortest_path('deadbee', 'aaaaaa1'))


# --------------------------------------------------------------------------- #
# (c) 정렬 안정성 — merge_sort docstring 의 '안정 정렬' 주장을 코드로 고정
# --------------------------------------------------------------------------- #
class MergeSortTest(unittest.TestCase):
    """R4-1/R4-2: 직접 구현한 머지 정렬. key 교체 가능, 그리고 안정 정렬."""

    def assert_non_decreasing(self, items, key):
        for i in range(1, len(items)):
            self.assertLessEqual(key(items[i - 1]), key(items[i]), f'정렬되지 않았다: {items}')

    def test_two_equal_keys_keep_input_order(self):
        """가장 작은 안정성 반례. `<=` 가 `<` 로 바뀌면 여기서 즉시 빨간 불."""
        items = [('k', 'first'), ('k', 'second')]
        self.assertEqual(
            minigit.merge_sort(items, key=lambda pair: pair[0]),
            [('k', 'first'), ('k', 'second')],
        )

    def test_duplicate_keys_preserve_relative_order(self):
        items = [(3, 'a'), (1, 'b'), (3, 'c'), (2, 'd'), (1, 'e')]
        self.assertEqual(
            minigit.merge_sort(items, key=lambda pair: pair[0]),
            [(1, 'b'), (1, 'e'), (2, 'd'), (3, 'a'), (3, 'c')],
        )

    def test_stability_on_many_duplicates(self):
        """key 가 8종뿐인 200개 입력. 각 key 안에서 원래 색인이 증가해야 한다."""
        rng = random.Random(1123)
        items = [(rng.randrange(8), index) for index in range(200)]
        result = minigit.merge_sort(items, key=lambda pair: pair[0])

        self.assertEqual(len(result), len(items))
        self.assert_non_decreasing(result, key=lambda pair: pair[0])

        last_index_seen = {}
        for group_key, original_index in result:
            previous = last_index_seen.get(group_key)
            if previous is not None:
                self.assertLess(
                    previous, original_index,
                    f'key={group_key} 안에서 원래 순서가 뒤집혔다 — 안정 정렬이 아니다',
                )
            last_index_seen[group_key] = original_index

    def test_multiset_is_preserved(self):
        rng = random.Random(77)
        items = [rng.randrange(50) for _ in range(120)]
        result = minigit.merge_sort(items, key=lambda value: value)
        counts_in, counts_out = {}, {}
        for value in items:
            counts_in[value] = counts_in.get(value, 0) + 1
        for value in result:
            counts_out[value] = counts_out.get(value, 0) + 1
        self.assertEqual(counts_in, counts_out, '정렬이 원소를 잃거나 복제했다')

    def test_empty_and_single(self):
        self.assertEqual(minigit.merge_sort([], key=lambda v: v), [])
        self.assertEqual(minigit.merge_sort([7], key=lambda v: v), [7])

    def test_input_list_is_not_mutated(self):
        items = [3, 1, 2]
        minigit.merge_sort(items, key=lambda v: v)
        self.assertEqual(items, [3, 1, 2])

    def test_key_is_swappable(self):
        """R4-2: 같은 자료를 날짜 기준과 작성자 기준으로 각각 정렬할 수 있어야 한다."""
        repo = build_repo([
            ('h000001', 'first', 'carol', 300.0, []),
            ('h000002', 'second', 'alice', 100.0, ['h000001']),
            ('h000003', 'third', 'bob', 200.0, ['h000002']),
        ])
        commits = list(repo.commits.values())

        by_date = minigit.merge_sort(commits, key=lambda c: (c.timestamp, c.hash))
        self.assertEqual([c.hash for c in by_date], ['h000002', 'h000003', 'h000001'])

        by_author = minigit.merge_sort(commits, key=lambda c: (c.author, c.timestamp, c.hash))
        self.assertEqual([c.author for c in by_author], ['alice', 'bob', 'carol'])


# --------------------------------------------------------------------------- #
# (d) 역색인 — 전체 순회와 같은 답을 내야 한다
# --------------------------------------------------------------------------- #
def linear_scan_keyword(repo, keyword):
    """역색인을 쓰지 않는 참조 구현 (느리지만 자명하게 옳다)."""
    want = keyword.lower()
    found = []
    for commit_hash, commit in repo.commits.items():
        for token in commit.message.split():
            if token.lower() == want:
                found.append(commit_hash)
                break
    return found


def linear_scan_author(repo, name):
    return [h for h, commit in repo.commits.items() if commit.author == name]


def dedupe(hashes):
    """cmd_search 와 같은 중복 제거 (메시지에 같은 토큰이 여러 번 나올 수 있다)."""
    seen, unique = set(), []
    for h in hashes:
        if h not in seen:
            seen.add(h)
            unique.append(h)
    return unique


class InvertedIndexTest(unittest.TestCase):
    """R3-1~R3-3: 역색인 결과 == 전체 순회 결과."""

    MESSAGES = [
        ('Alice Kim', 'Initial commit'),
        ('Alice Kim', 'Add login feature'),
        ('Bob Lee', 'Add payment FEATURE'),
        ('Bob Lee', 'Fix login bug'),
        ('Carol Park', 'refactor LOGIN login Login'),   # 같은 토큰 3회 — 중복 등록 경로
        ('Carol Park', 'docs: update README'),
        ('Alice Kim', 'Add tests for payment'),
        ('Bob Lee', 'chore bump version'),
    ]

    QUERIES = [
        'login', 'LOGIN', 'Login', 'feature', 'FEATURE', 'add', 'Add',
        'payment', 'commit', 'readme', 'README', 'nonexistent', '',
    ]

    def make_repo(self):
        repo = minigit.Repository()
        repo.init(self.MESSAGES[0][0])
        for author, message in self.MESSAGES:
            repo.author = author
            repo.commit(message)
        return repo

    def test_keyword_index_matches_linear_scan(self):
        repo = self.make_repo()
        for query in self.QUERIES:
            with self.subTest(query=query):
                self.assertEqual(
                    dedupe(repo.search_keyword(query)),
                    linear_scan_keyword(repo, query),
                    f'역색인과 전체 순회의 답이 다르다: {query!r}',
                )

    def test_author_index_matches_linear_scan(self):
        repo = self.make_repo()
        for name in ['Alice Kim', 'Bob Lee', 'Carol Park', 'Nobody', 'alice kim']:
            with self.subTest(author=name):
                self.assertEqual(
                    dedupe(repo.search_author(name)),
                    linear_scan_author(repo, name),
                    f'작성자 색인과 전체 순회의 답이 다르다: {name!r}',
                )

    def test_every_message_token_is_indexed(self):
        """R3-2: 공백 분리 + 소문자 정규화된 모든 토큰이 색인에 들어가야 한다."""
        repo = self.make_repo()
        for commit_hash, commit in repo.commits.items():
            for token in commit.message.split():
                with self.subTest(token=token):
                    self.assertIn(commit_hash, repo.search_keyword(token))

    def test_search_result_is_a_copy(self):
        """호출자가 결과를 건드려도 색인이 오염되면 안 된다."""
        repo = self.make_repo()
        result = repo.search_keyword('login')
        self.assertTrue(result)
        result.append('tampered')
        self.assertNotIn('tampered', repo.search_keyword('login'))

    def test_index_survives_reinit(self):
        """INIT 재실행은 색인까지 비워야 한다 (남아 있으면 유령 커밋이 검색된다)."""
        repo = self.make_repo()
        repo.init('Dave')
        self.assertEqual(repo.search_keyword('login'), [])
        self.assertEqual(repo.search_author('Alice Kim'), [])


# --------------------------------------------------------------------------- #
# 조상 탐색 — 다이아몬드에서 중복 없이
# --------------------------------------------------------------------------- #
class AncestorsTest(unittest.TestCase):
    """R5-8: 도달 가능한 모든 조상을, 빠짐없이 그리고 중복 없이."""

    def test_diamond_collects_three_without_duplicates(self):
        repo = build_repo([
            ('aaaaaa1', 'root', 'alice', 100.0, []),
            ('bbbbbb2', 'left', 'alice', 101.0, ['aaaaaa1']),
            ('ccccc03', 'right', 'bob', 102.0, ['aaaaaa1']),
            ('ddddd04', 'merge', 'alice', 103.0, ['bbbbbb2', 'ccccc03']),
        ])
        self.assertEqual(repo.ancestors('ddddd04'), {'aaaaaa1', 'bbbbbb2', 'ccccc03'})

    def test_root_has_no_ancestors(self):
        repo = build_repo([('aaaaaa1', 'root', 'alice', 100.0, [])])
        self.assertEqual(repo.ancestors('aaaaaa1'), set())

    def test_unknown_commit_returns_none(self):
        repo = build_repo([('aaaaaa1', 'root', 'alice', 100.0, [])])
        self.assertIsNone(repo.ancestors('deadbee'))


# --------------------------------------------------------------------------- #
# 커밋 해시 유일성 / 브랜치·HEAD
# --------------------------------------------------------------------------- #
class RepositoryStateTest(unittest.TestCase):
    """R2-5, R5-1~R5-4."""

    def test_hashes_are_unique_for_identical_messages(self):
        """같은 메시지를 500번 커밋해도 해시가 겹치면 안 된다 (카운터가 섞인다)."""
        repo = minigit.Repository()
        repo.init('alice')
        hashes = [repo.commit('same message').hash for _ in range(500)]
        self.assertEqual(len(set(hashes)), 500)

    def test_branch_points_at_head_and_switch_moves_head(self):
        repo = minigit.Repository()
        repo.init('alice')
        first = repo.commit('first').hash
        repo.make_branch('feature')
        self.assertEqual(repo.branches['feature'], first)

        repo.switch('feature')
        second = repo.commit('second').hash
        self.assertEqual(repo.branches['feature'], second)
        self.assertEqual(repo.branches['main'], first, 'main 브랜치가 따라 움직였다')

        self.assertEqual(repo.commits[second].parents, [first])

    def test_duplicate_branch_and_unknown_branch_raise(self):
        repo = minigit.Repository()
        repo.init('alice')
        repo.make_branch('feature')
        with self.assertRaises(ValueError):
            repo.make_branch('feature')
        with self.assertRaises(ValueError):
            repo.switch('nope')

    def test_root_commit_has_no_parents(self):
        repo = minigit.Repository()
        repo.init('alice')
        self.assertEqual(repo.commit('first').parents, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
