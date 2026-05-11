# Mini Git

학습용 CLI 기반 미니 버전관리 시스템. 커밋 그래프(DAG), 브랜치, HEAD, 역색인 검색, 직접 구현한 정렬을 메모리상에서 동작시킵니다.

## 실행

```
python main.py
```

`mini-git>` 프롬프트가 뜨면 명령을 입력하고, `exit` 또는 `quit`으로 종료합니다.

> Python 3.10+ 필요. 표준 라이브러리만 사용합니다. 데이터는 메모리에만 저장되며 종료 시 사라집니다.

## 공통 규칙

- 명령어는 대소문자 무관: `INIT`, `init` 모두 허용.
- 공백을 포함하는 문자열 인자는 따옴표로 감쌉니다: `COMMIT "Add login feature"`.
- 옵션 표기는 `--key=value` 형식: `SEARCH --author=Alice`, `LOG --sort-by=date`.
- 입력이 잘못되면 `Invalid args`, 없는 브랜치/커밋은 `Unknown branch: <name>` / `Unknown commit: <hash>`를 출력합니다.

## 지원 명령

| 명령 | 설명 |
| --- | --- |
| `INIT <user_name>` | 저장소 초기화, `main` 브랜치 생성, 사용자 지정 |
| `BRANCH <branch_name>` | 현재 HEAD에서 새 브랜치 생성 |
| `SWITCH <branch_name>` | 다른 브랜치로 HEAD 이동 |
| `COMMIT <message>` | 현재 HEAD를 부모로 하는 새 커밋 |
| `LOG` | 부모가 자식보다 먼저 출력되는 위상 정렬(Kahn) 순서 |
| `LOG --sort-by=date\|author` | 직접 구현한 머지 정렬로 정렬 |
| `PATH <c1> <c2>` | 무방향 그래프로 본 최단 경로, 동률이면 사전순 최소 |
| `ANCESTORS <commit_hash>` | 모든 조상 커밋 |
| `SEARCH <keyword>` | 메시지 토큰 역색인 검색 (소문자 정규화) |
| `SEARCH --author=<name>` | 작성자 역색인 검색 |
| `exit` / `quit` | 종료 |

## 핵심 자료구조와 알고리즘

- **커밋 노드**: `hash`, `message`, `author`, `timestamp`, `parents`를 가지는 단순 객체.
- **그래프**: 커밋 hash → 노드 매핑(`dict`)으로 O(1) 조회, 부모 리스트로 간선을 표현. 비순환을 보장하기 위해 새 커밋은 항상 기존 HEAD를 부모로 가집니다.
- **위상 정렬 (LOG)**: Kahn 알고리즘으로 in-degree=0인 노드부터 출력. 같은 레벨에서는 `(timestamp, hash)` 오름차순으로 결정적 출력을 만듭니다.
- **최단 경로 (PATH)**: 부모 간선을 무방향으로 본 BFS. 같은 길이 경로가 여러 개일 때는, BFS 레벨별로 `best[v] = min(best[u] + "->" + v)`를 계산해 사전순 최소 문자열을 산출합니다. 모든 hash 길이가 같아 같은 거리의 경로 문자열들은 길이가 같으므로 사전 비교가 정확합니다.
- **조상 탐색 (ANCESTORS)**: 부모 방향 DFS로 도달 가능한 모든 노드를 수집.
- **역색인**:
  - `keyword(lower) -> [hash...]`: 커밋 메시지를 공백으로 분리, `lower()`로 정규화해 등록. 검색 시 전체 커밋 순회 없이 `O(1)` 사전 조회 + 결과 개수만큼만 출력.
  - `author -> [hash...]`: 작성자 검색용.
- **정렬**: 표준 `sorted()` / `list.sort()` 사용 금지 요건에 따라 **머지 정렬을 직접 구현**. 평균/최악 모두 `O(n log n)`이고, 비교 시 `<=`를 사용해 **안정 정렬**을 유지합니다.

## 사용 예시

```
mini-git> init "Alice"
Initialized repository.
Current branch: main
Current user: Alice

mini-git> commit "Initial commit"
[main 7f3a9c1] Initial commit

mini-git> branch feature
Created branch: feature

mini-git> switch feature
Switched to branch: feature

mini-git> commit "Add login feature"
[feature 2b8e4f2] Add login feature

mini-git> switch main
Switched to branch: main

mini-git> commit "Add payment feature"
[main 9c1d3a7] Add payment feature

mini-git> log
commit 7f3a9c1 (Alice, 2026-05-11 22:30:00)
Initial commit
commit 2b8e4f2 (Alice, 2026-05-11 22:30:05) [feature]
Add login feature
commit 9c1d3a7 (Alice, 2026-05-11 22:30:10) [main]
Add payment feature

mini-git> path 7f3a9c1 9c1d3a7
Path: 7f3a9c1->9c1d3a7

mini-git> search "login"
Found 1 commit:
- 2b8e4f2: Add login feature

mini-git> search --author=Alice
Found 3 commits:
- 7f3a9c1: Initial commit
- 2b8e4f2: Add login feature
- 9c1d3a7: Add payment feature

mini-git> log --sort-by=author
commit 7f3a9c1 (Alice, 2026-05-11 22:30:00)
Initial commit
commit 2b8e4f2 (Alice, 2026-05-11 22:30:05)
Add login feature
commit 9c1d3a7 (Alice, 2026-05-11 22:30:10)
Add payment feature
```

## 학습 체크리스트

- 커밋 그래프는 왜 DAG인가? → 새 커밋은 항상 기존 노드(과거)를 부모로만 가리키므로 사이클이 생길 수 없다.
- 왜 LOG는 위상 정렬인가? → 자식보다 부모가 먼저 보여야 변경의 인과관계를 따라갈 수 있다.
- PATH 동률을 어떻게 결정하는가? → 같은 길이의 경로 문자열들 중 사전순 최소.
- 머지 정렬 시간복잡도와 안정성은? → 평균/최악 `O(n log n)`, `<=` 비교로 안정 정렬.
- 역색인이 빠른 이유? → 메시지 전체를 매번 토큰화/검사하는 `O(N·M)` 대신, 사전 조회 `O(1)` + 결과 개수만큼만 본다.

## 제약/범위

- 파일 내용 추적 없음 (커밋 메타데이터 중심).
- 네트워크 통신 없음.
- 데이터 영속화 없음 (메모리 동작).
- 그래프 전용 라이브러리 미사용, 정렬 표준 API 미사용.
