"""과제 제약(README `0.6`)과 구조 요구(R3-1, R7-1, R7-2)를 실행되는 검사로 옮긴다.

지금까지 이 제약들은 README 의 문장과, 사람이 한 번 돌린 `grep` 기록으로만
존재했다. 문장은 리팩터링을 따라오지 않는다. 여기서는 `main.py` 를 AST 로 읽어
금지 API 사용을 기계가 실패시킨다.

검사하는 것:
  - 표준 라이브러리 화이트리스트 (그래프 전용 라이브러리 금지)
  - `sorted()` / `list.sort()` / `heapq` / `bisect` / `most_common` / `cmp_to_key` 금지
  - 정렬을 우회하는 `min()` / `max()` 금지 (0.6 💡 의 보수적 해석)
  - R3-1: 검색 경로에 전체 순회 루프가 없다
  - R7-1: 알고리즘 함수가 `print` 를 부르지 않는다 (계층 분리)
  - R7-2: 알고리즘 함수/클래스에 docstring 이 있다
"""

import ast
import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_PATH = os.path.join(REPO_ROOT, 'main.py')

# 0.6 「라이브러리 제한」 에서 허용되는 것만. 새 import 를 쓰려면 이 표를 먼저 고쳐야 한다.
ALLOWED_TOP_LEVEL_IMPORTS = {'hashlib', 'shlex', 'sys', 'time', 'collections', 'datetime'}

# 0.6 🚫 「정렬 관련 표준 API 전부 금지」
FORBIDDEN_NAMES = {'sorted', 'min', 'max'}
FORBIDDEN_ATTRIBUTES = {'sort', 'most_common', 'cmp_to_key', 'insort', 'heappush', 'heappop'}

# 알고리즘 로직 — 여기에 print 가 들어가면 계층이 무너지고 단위 테스트가 불가능해진다.
ALGORITHM_FUNCTIONS = {
    'merge_sort',
    'Repository.topological_log',
    'Repository.shortest_path',
    'Repository.ancestors',
    'Repository.search_keyword',
    'Repository.search_author',
    'Repository._new_hash',
}
DOCSTRING_REQUIRED = {
    'Commit',
    'Repository',
    'merge_sort',
    'Repository.topological_log',
    'Repository.shortest_path',
    'Repository.ancestors',
    'Repository._new_hash',
    'parse_line',
}


def load_tree():
    with open(MAIN_PATH, encoding='utf-8') as handle:
        return ast.parse(handle.read(), filename=MAIN_PATH)


def qualified_definitions(tree):
    """'merge_sort', 'Repository.commit' 같은 이름 -> AST 노드."""
    found = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found[node.name] = node
        elif isinstance(node, ast.ClassDef):
            found[node.name] = node
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    found[f'{node.name}.{child.name}'] = child
    return found


class ParseSanityTest(unittest.TestCase):
    """검사가 '아무것도 못 찾아서' 통과하는 일을 막는다."""

    def test_main_is_parsed_and_not_empty(self):
        definitions = qualified_definitions(load_tree())
        self.assertGreater(len(definitions), 15, 'main.py 를 제대로 읽지 못했다')
        for name in ALGORITHM_FUNCTIONS | DOCSTRING_REQUIRED:
            self.assertIn(name, definitions, f'검사가 가리키는 {name} 이(가) 사라졌다')


class ImportConstraintTest(unittest.TestCase):
    """0.6: 표준 라이브러리만. 그래프 전용 라이브러리 금지."""

    def imported_modules(self):
        modules = set()
        for node in ast.walk(load_tree()):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    modules.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module.split('.')[0])
        return modules

    def test_only_allowlisted_modules(self):
        unexpected = self.imported_modules() - ALLOWED_TOP_LEVEL_IMPORTS
        self.assertEqual(
            unexpected, set(),
            f'허용 목록에 없는 import: {unexpected}. 제약을 확인하고 목록을 먼저 고쳐라.',
        )

    def test_collections_only_provides_deque(self):
        """`Counter.most_common()` 같은 정렬 우회 경로를 막는다."""
        for node in ast.walk(load_tree()):
            if isinstance(node, ast.ImportFrom) and node.module == 'collections':
                self.assertEqual({alias.name for alias in node.names}, {'deque'})


class SortingApiConstraintTest(unittest.TestCase):
    """R4-1: 정렬은 직접 구현한다."""

    def test_no_forbidden_builtin_calls(self):
        offenders = []
        for node in ast.walk(load_tree()):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Name) and func.id in FORBIDDEN_NAMES:
                offenders.append((func.id, node.lineno))
            elif isinstance(func, ast.Attribute) and func.attr in FORBIDDEN_ATTRIBUTES:
                offenders.append((func.attr, node.lineno))
        self.assertEqual(offenders, [], f'금지된 정렬 API 사용: {offenders}')

    def test_merge_sort_is_implemented_here(self):
        """금지만으로는 부족하다 — 직접 구현이 실제로 있어야 한다."""
        self.assertIn('merge_sort', qualified_definitions(load_tree()))


class SearchIsIndexedTest(unittest.TestCase):
    """R3-1: 검색은 전체 커밋을 순회하지 않는다."""

    def test_search_has_no_loop(self):
        definitions = qualified_definitions(load_tree())
        for name in ('Repository.search_keyword', 'Repository.search_author'):
            node = definitions[name]
            loops = [child for child in ast.walk(node) if isinstance(child, (ast.For, ast.While))]
            comprehensions = [
                child for child in ast.walk(node)
                if isinstance(child, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp))
            ]
            self.assertEqual(
                loops + comprehensions, [],
                f'{name} 에 순회가 생겼다 — 역색인 요구(R3-1)를 벗어난다',
            )

    def test_both_indexes_exist(self):
        """R3-3: keyword / author 두 종류."""
        sys.path.insert(0, REPO_ROOT)
        import main as minigit

        repo = minigit.Repository()
        repo.init('alice')
        self.assertIsInstance(repo.keyword_index, dict)
        self.assertIsInstance(repo.author_index, dict)


class LayerSeparationTest(unittest.TestCase):
    """R7-1: 알고리즘은 출력하지 않는다. 출력하지 않으므로 단위 테스트가 가능하다."""

    def test_algorithms_do_not_print(self):
        definitions = qualified_definitions(load_tree())
        for name in ALGORITHM_FUNCTIONS:
            node = definitions[name]
            printing = [
                child.lineno for child in ast.walk(node)
                if isinstance(child, ast.Call)
                and isinstance(child.func, ast.Name)
                and child.func.id == 'print'
            ]
            self.assertEqual(printing, [], f'{name} 안에서 print 를 부른다 (줄 {printing})')

    def test_algorithms_have_docstrings(self):
        """R7-2."""
        definitions = qualified_definitions(load_tree())
        for name in DOCSTRING_REQUIRED:
            self.assertTrue(
                (ast.get_docstring(definitions[name]) or '').strip(),
                f'{name} 에 docstring 이 없다',
            )


class DispatchTableTest(unittest.TestCase):
    """R1-1 / R6-2: 명령 표가 소문자 키로만 이뤄지고, 전부 호출 가능해야 한다."""

    def test_commands_are_lowercase_and_callable(self):
        sys.path.insert(0, REPO_ROOT)
        import main as minigit

        self.assertTrue(minigit.COMMANDS)
        for name, handler in minigit.COMMANDS.items():
            self.assertEqual(name, name.lower(), f'명령 키 {name!r} 가 소문자가 아니다')
            self.assertTrue(callable(handler), f'{name!r} 의 핸들러가 호출 불가')

    def test_every_required_command_is_registered(self):
        """R5-1~R5-10 이 요구하는 명령이 표에 전부 있어야 한다."""
        sys.path.insert(0, REPO_ROOT)
        import main as minigit

        required = {'init', 'branch', 'switch', 'commit', 'log', 'path', 'ancestors', 'search'}
        self.assertEqual(required - set(minigit.COMMANDS), set())


if __name__ == '__main__':
    unittest.main(verbosity=2)
