"""Mini Git: 학습용 CLI 기반 미니 버전관리 시스템.

- 커밋 그래프(DAG)와 브랜치, HEAD를 메모리상에서 관리한다.
- LOG는 부모가 자식보다 먼저 출력되는 위상 정렬(Kahn) 순서로 보여준다.
- PATH는 부모 간선을 무방향으로 본 최단 경로(BFS)이며, 동률이면 사전순 최소를 고른다.
- 검색은 메시지 토큰/작성자 역색인(inverted index)으로 처리한다.
- 정렬은 Python 표준 정렬 API를 쓰지 않고 직접 구현한 머지 정렬을 사용한다.
"""

import hashlib
import shlex
import sys
import time
from collections import deque
from datetime import datetime


# --------------------------------------------------------------------------- #
# 자료구조                                                                     #
# --------------------------------------------------------------------------- #
class Commit:
    """커밋 노드. 그래프의 정점이자 최소 메타데이터의 모음."""

    def __init__(self, commit_hash, message, author, timestamp, parents):
        self.hash = commit_hash
        self.message = message
        self.author = author
        self.timestamp = timestamp  # epoch float
        self.parents = list(parents)  # 부모 hash 목록 (0개 이상)

    def time_str(self):
        return datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')


# --------------------------------------------------------------------------- #
# 정렬 (표준 API 미사용)                                                       #
# --------------------------------------------------------------------------- #
def merge_sort(items, key):
    """안정 정렬인 머지 정렬. 평균/최악 모두 O(n log n)."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left = merge_sort(items[:mid], key)
    right = merge_sort(items[mid:], key)
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):  # '<='로 안정성 유지
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    while i < len(left):
        merged.append(left[i])
        i += 1
    while j < len(right):
        merged.append(right[j])
        j += 1
    return merged


# --------------------------------------------------------------------------- #
# 저장소                                                                       #
# --------------------------------------------------------------------------- #
class Repository:
    """커밋 그래프, 브랜치, HEAD, 역색인을 갖는 메모리 저장소."""

    def __init__(self):
        self.commits = {}          # hash -> Commit
        self.children = {}         # hash -> list[child hash]  (그래프 보조 정보)
        self.branches = {}         # branch_name -> hash | None
        self.head_branch = None    # 현재 체크아웃된 브랜치 이름
        self.author = None         # INIT 시 지정한 사용자
        self._counter = 0          # 해시 유일성 확보용
        self.keyword_index = {}    # keyword(lower) -> list[hash]
        self.author_index = {}     # author -> list[hash]
        self.initialized = False

    # ----- 기본 헬퍼 ------------------------------------------------------- #
    def head_commit(self):
        if self.head_branch is None:
            return None
        return self.branches.get(self.head_branch)

    def _new_hash(self, message, author, ts):
        """세션 내 유일한 해시를 만든다. 충돌 시 카운터를 늘려 재시도."""
        while True:
            self._counter += 1
            raw = f'{self._counter}|{author}|{message}|{ts}'.encode('utf-8')
            h = hashlib.sha1(raw).hexdigest()[:7]
            if h not in self.commits:
                return h

    def _branches_pointing_to(self, h):
        return [b for b, target in self.branches.items() if target == h]

    # ----- 명령 구현 ------------------------------------------------------- #
    def init(self, user_name):
        # 기존 상태를 모두 초기화
        self.commits = {}
        self.children = {}
        self.branches = {'main': None}
        self.head_branch = 'main'
        self.author = user_name
        self._counter = 0
        self.keyword_index = {}
        self.author_index = {}
        self.initialized = True

    def make_branch(self, name):
        if name in self.branches:
            raise ValueError(f'Branch already exists: {name}')
        self.branches[name] = self.head_commit()

    def switch(self, name):
        if name not in self.branches:
            raise ValueError(f'Unknown branch: {name}')
        self.head_branch = name

    def commit(self, message):
        ts = time.time()
        h = self._new_hash(message, self.author, ts)
        parent = self.head_commit()
        parents = [parent] if parent is not None else []
        node = Commit(h, message, self.author, ts, parents)
        self.commits[h] = node
        self.children.setdefault(h, [])
        for p in parents:
            self.children.setdefault(p, []).append(h)
        # 현재 브랜치의 끝을 이 커밋으로 이동
        self.branches[self.head_branch] = h
        # 역색인 갱신
        for token in message.split():  # 공백 분리 후
            key = token.lower()          # 소문자로 정규화
            self.keyword_index.setdefault(key, []).append(h)
        self.author_index.setdefault(self.author, []).append(h)
        return node

    # ----- 그래프 알고리즘 ------------------------------------------------- #
    def topological_log(self):
        """Kahn 알고리즘: 부모가 자식보다 먼저 출력되는 순서를 반환."""
        indeg = {h: len(c.parents) for h, c in self.commits.items()}
        # 결정적인 출력을 위해 같은 레벨에서는 (timestamp, hash) 오름차순
        ready = [h for h, d in indeg.items() if d == 0]
        order = []
        while ready:
            # ready에서 (timestamp, hash) 최소를 선택
            pick = 0
            for i in range(1, len(ready)):
                a = self.commits[ready[i]]
                b = self.commits[ready[pick]]
                if (a.timestamp, a.hash) < (b.timestamp, b.hash):
                    pick = i
            h = ready.pop(pick)
            order.append(h)
            for child in self.children.get(h, []):
                indeg[child] -= 1
                if indeg[child] == 0:
                    ready.append(child)
        return order

    def shortest_path(self, src, dst):
        """무방향 그래프(부모 간선)에서 src→dst 최단 경로 문자열을 반환.

        같은 길이의 경로가 여러 개면 'h1->h2->...' 사전순 최소를 고른다.
        """
        if src not in self.commits or dst not in self.commits:
            return None
        if src == dst:
            return src

        # 인접 리스트 (무방향)
        adj = {h: set() for h in self.commits}
        for h, c in self.commits.items():
            for p in c.parents:
                adj[h].add(p)
                adj[p].add(h)

        # BFS로 거리 산출
        dist = {src: 0}
        queue = deque([src])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    queue.append(v)

        if dst not in dist:
            return None

        # 같은 거리에 도달하는 경로들 중 사전순 최소 문자열을 BFS 레벨별로 계산.
        # 모든 해시 길이가 같으므로, 동일 길이 문자열들의 비교는 일반 사전순과 일치한다.
        best = {src: src}
        level = [src]
        while level:
            nxt = []
            seen_in_next = set()
            for u in level:
                for v in adj[u]:
                    if dist.get(v) == dist[u] + 1 and v not in seen_in_next:
                        nxt.append(v)
                        seen_in_next.add(v)
            for v in nxt:
                candidate = None
                for u in adj[v]:
                    if dist.get(u) == dist[v] - 1:
                        s = best[u] + '->' + v
                        if candidate is None or s < candidate:
                            candidate = s
                best[v] = candidate
            level = nxt

        return best.get(dst)

    def ancestors(self, h):
        """h에서 부모 방향으로 도달 가능한 모든 조상 hash 집합."""
        if h not in self.commits:
            return None
        visited = set()
        stack = list(self.commits[h].parents)
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            for p in self.commits[node].parents:
                if p not in visited:
                    stack.append(p)
        return visited

    # ----- 검색 ------------------------------------------------------------ #
    def search_keyword(self, keyword):
        # 역색인이므로 O(1)에 후보를 얻는다. (전체 순회 X)
        return list(self.keyword_index.get(keyword.lower(), []))

    def search_author(self, name):
        return list(self.author_index.get(name, []))


# --------------------------------------------------------------------------- #
# 출력 헬퍼                                                                    #
# --------------------------------------------------------------------------- #
def format_commit_line(repo, commit, with_branches=True):
    labels = ''
    if with_branches:
        bs = repo._branches_pointing_to(commit.hash)
        if bs:
            labels = ' [' + ', '.join(bs) + ']'
    return f'commit {commit.hash} ({commit.author}, {commit.time_str()}){labels}\n{commit.message}'


# --------------------------------------------------------------------------- #
# 명령 디스패치                                                                #
# --------------------------------------------------------------------------- #
INVALID = 'Invalid args'


def require_init(repo):
    if not repo.initialized:
        print('Repository not initialized. Run: INIT <user_name>')
        return False
    return True


def cmd_init(repo, args):
    if len(args) != 1:
        print(INVALID)
        return
    repo.init(args[0])
    print('Initialized repository.')
    print(f'Current branch: {repo.head_branch}')
    print(f'Current user: {repo.author}')


def cmd_branch(repo, args):
    if not require_init(repo):
        return
    if len(args) != 1:
        print(INVALID)
        return
    try:
        repo.make_branch(args[0])
    except ValueError as e:
        print(str(e))
        return
    print(f'Created branch: {args[0]}')


def cmd_switch(repo, args):
    if not require_init(repo):
        return
    if len(args) != 1:
        print(INVALID)
        return
    try:
        repo.switch(args[0])
    except ValueError as e:
        print(str(e))
        return
    print(f'Switched to branch: {args[0]}')


def cmd_commit(repo, args):
    if not require_init(repo):
        return
    if len(args) != 1:
        print(INVALID)
        return
    node = repo.commit(args[0])
    print(f'[{repo.head_branch} {node.hash}] {node.message}')


def cmd_log(repo, args):
    if not require_init(repo):
        return
    sort_by = None
    for a in args:
        if a.startswith('--sort-by='):
            sort_by = a.split('=', 1)[1]
        else:
            print(INVALID)
            return
    if sort_by is not None and sort_by not in ('date', 'author'):
        print(INVALID)
        return

    if sort_by is None:
        # 위상 정렬: 부모 → 자식 순서
        order = repo.topological_log()
        commits = [repo.commits[h] for h in order]
    else:
        all_commits = list(repo.commits.values())
        if sort_by == 'date':
            commits = merge_sort(all_commits, key=lambda c: (c.timestamp, c.hash))
        else:  # author
            commits = merge_sort(all_commits, key=lambda c: (c.author, c.timestamp, c.hash))

    if not commits:
        return
    for c in commits:
        print(format_commit_line(repo, c, with_branches=(sort_by is None)))


def cmd_path(repo, args):
    if not require_init(repo):
        return
    if len(args) != 2:
        print(INVALID)
        return
    a, b = args
    if a not in repo.commits:
        print(f'Unknown commit: {a}')
        return
    if b not in repo.commits:
        print(f'Unknown commit: {b}')
        return
    result = repo.shortest_path(a, b)
    if result is None:
        print('No path')
    else:
        print(f'Path: {result}')


def cmd_ancestors(repo, args):
    if not require_init(repo):
        return
    if len(args) != 1:
        print(INVALID)
        return
    h = args[0]
    res = repo.ancestors(h)
    if res is None:
        print(f'Unknown commit: {h}')
        return
    if not res:
        print('(no ancestors)')
        return
    # 안정적인 출력 순서를 위해 (timestamp, hash)로 정렬
    nodes = [repo.commits[x] for x in res]
    nodes = merge_sort(nodes, key=lambda c: (c.timestamp, c.hash))
    for c in nodes:
        print(f'{c.hash} ({c.author}, {c.time_str()}) {c.message}')


def cmd_search(repo, args):
    if not require_init(repo):
        return
    if len(args) != 1:
        print(INVALID)
        return
    token = args[0]
    if token.startswith('--author='):
        name = token.split('=', 1)[1]
        hashes = repo.search_author(name)
    else:
        hashes = repo.search_keyword(token)

    if not hashes:
        print('Found 0 commits.')
        return
    # 중복 제거 (메시지에 같은 토큰이 여러 번 나오면 중복 등록될 수 있음)
    seen = set()
    unique = []
    for h in hashes:
        if h not in seen:
            seen.add(h)
            unique.append(h)
    print(f'Found {len(unique)} commit{"s" if len(unique) != 1 else ""}:')
    for h in unique:
        c = repo.commits[h]
        print(f'- {c.hash}: {c.message}')


COMMANDS = {
    'init': cmd_init,
    'branch': cmd_branch,
    'switch': cmd_switch,
    'commit': cmd_commit,
    'log': cmd_log,
    'path': cmd_path,
    'ancestors': cmd_ancestors,
    'search': cmd_search,
}


# --------------------------------------------------------------------------- #
# REPL                                                                         #
# --------------------------------------------------------------------------- #
def parse_line(line):
    """공백 분리. 따옴표로 감싼 인자는 한 토큰으로 인식."""
    try:
        return shlex.split(line, posix=True)
    except ValueError:
        return None


def main():
    repo = Repository()
    print('Mini Git. Type "exit" or "quit" to leave.')
    while True:
        try:
            line = input('mini-git> ')
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue
        line = line.strip()
        if not line:
            continue
        if line.lower() in ('exit', 'quit'):
            break
        tokens = parse_line(line)
        if tokens is None or not tokens:
            print(INVALID)
            continue
        cmd = tokens[0].lower()  # 명령은 대소문자 무시
        args = tokens[1:]
        handler = COMMANDS.get(cmd)
        if handler is None:
            print(f'Unknown command: {cmd}')
            continue
        try:
            handler(repo, args)
        except Exception as e:  # 학습용 안전망
            print(f'Error: {e}')


if __name__ == '__main__':
    main()
