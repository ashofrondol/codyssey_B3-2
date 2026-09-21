# Mini Git

학습용 CLI 기반 미니 버전관리 시스템. 커밋 그래프(DAG), 브랜치, HEAD, 역색인 검색, 직접 구현한 정렬을 메모리상에서 동작시킵니다.

## 0. 과제 명세 (원본 미션 요구사항)

> 출처: `codyssey_assignments/B3-2.pdf` — 원문 요구사항을 그대로 옮기고, 해설은 💡 로 구분했다.

### 0.1 미션 한눈에 보기

| 항목 | 내용 |
| --- | --- |
| 분야 | AI/SW 기초 |
| 구분 | 자료구조와 알고리즘 |
| 학습시간 | 80시간 |
| 미션 제목 | 파일이 언제 어떻게 바뀌었는지 기록하는 작은 프로그램 만들기 |
| 산출물 | CLI 기반 Mini Git 프로그램 1개 |
| 실행 예 | `python main.py` |

#### 원문 — 1. 미션 소개

> Git의 커밋 하나에는 그래프 자료구조와 해시가 담겨 있습니다. 이걸 알고 쓰면 rebase, merge, cherry-pick이 다르게 보이고, 알고리즘 공부와도 연결됩니다. Mini Git을 직접 구현하면서 그 안의 구조를 손으로 확인합니다.
>
> Git은 전 세계 개발자들이 사용하는 분산 버전 관리 시스템입니다.
> 브랜치로 병렬 작업을 지원하고, 변경 이력을 추적하며, 그 핵심에는 그래프 자료구조와 탐색 알고리즘이 있습니다.
>
> 이번 미션에서는 Git의 핵심 구조를 직접 구현하며 CLI 기반 Mini Git을 완성합니다. 커밋 구조를 구축하고 브랜치를 관리하는 기능, 커밋을 검색하고 정렬하는 시스템 등을 만들며 실제 Git의 동작 원리를 체득합니다.
>
> 이 경험은 다양한 알고리즘 학습의 토대가 되며 코딩 테스트를 준비하는 데 도움이 됩니다.

#### (해설) 이 과제가 진짜로 묻는 것

> 💡 이 과제는 "Git 클론 만들기"가 아니다. Git은 **소재**일 뿐이고, 실제 평가 대상은 자료구조·알고리즘을 **라이브러리 없이 손으로 구현했는가**이다.
>
> 💡 핵심 축은 네 가지다. ① 커밋 이력을 **DAG(방향성 비순환 그래프)** 로 모델링하기, ② 그 위에서 **위상 정렬 성격의 출력(LOG)** · **BFS 최단 경로(PATH)** · **도달 가능성 탐색(ANCESTORS)** 을 수행하기, ③ **정렬 알고리즘을 직접 구현**해 비교 기준을 바꿔 끼우기, ④ **역색인(Inverted Index)** 으로 선형 순회 검색을 대체하기.
>
> 💡 그래서 "파일 내용 추적", "네트워크", "파일 영속성" 은 명시적으로 **구현 대상이 아니다**. 거기에 시간을 쓰면 평가 포인트를 벗어난다.
>
> 💡 `sorted()` / `list.sort()` 금지, 그래프 전용 라이브러리 금지는 단순 제약이 아니라 **이 과제의 본체**다. 금지를 우회하지 않고 정면으로 구현했는지가 채점의 중심이다.
>
> 💡 평가 체크리스트를 보면 "동작하는가"만큼 "**왜 그렇게 했는지 설명할 수 있는가**"를 묻는다. 코드가 돌아가도 설계 근거(왜 DAG인가, 왜 BFS인가, 역색인이 왜 빠른가)를 말로 못 하면 미완성으로 본다.

### 0.2 최종 산출물 (제출물)

#### 원문 — 2. 최종 결과물

> 다음 기능이 정상 동작하는 CLI 기반 Mini Git 프로그램 1개를 완성한다.

**1. 저장소 및 브랜치 관리**

- 입력/요청: `INIT <user_name>` , `BRANCH <branch_name>` , `SWITCH <branch_name>` , `COMMIT <message>`
- 출력/화면: 저장소 초기화 결과, 브랜치 생성/전환 결과, 커밋 생성 결과(커밋 hash 포함)

**2. 커밋 로그 및 탐색**

- 입력/요청: `LOG` , `PATH <commit1> <commit2>` , `ANCESTORS <commit_hash>`
- 출력/화면: 커밋 목록 출력, 최단 경로 출력(없으면 `No path`), 조상 목록 출력

**3. 검색 및 정렬**

- 입력/요청: `SEARCH <keyword>` , `SEARCH --author=<name>` , `LOG --sort-by=date|author`
- 출력/화면: 검색 결과 커밋 목록, 정렬 기준에 따른 로그 출력

**4. CLI 인터페이스(REPL)**

- 입력/요청: `mini-git>` 프롬프트에서 명령을 반복 입력
- 출력/화면: 명령 파싱 → 실행 → 결과 출력이 반복, `exit` / `quit` 로 종료

**5. 필수 제출물 / 실행**

- 필수 제출물: 엔트리 포인트(예: `main.py`) 1개 + `README.md` 1개
- 실행(예): `python main.py`

#### 제출 증거 체크리스트

- [ ] 엔트리 포인트 파일 1개 (예: `main.py`)
- [ ] `README.md` 1개
- [ ] `python main.py` 로 실행되어 `mini-git>` 프롬프트가 뜨는 것
- [ ] 위 1~4의 모든 명령이 정상 동작하는 것

> 💡 PDF에 명시된 제출물은 **엔트리 포인트 1개 + README.md 1개**가 전부다. 모듈을 여러 파일로 나누는 것은 금지되지 않았지만(오히려 "알고리즘 로직은 독립된 함수 또는 클래스로 분리한다"는 요구가 있다), **`python main.py` 한 줄로 실행 가능해야 한다**는 조건은 유지해야 한다.

### 0.3 과제 목표 — 수료 후 스스로 설명할 수 있어야 하는 것

#### 원문 — 3. 과제 목표

> 이 과제를 마친 후, 학습자는 아래를 스스로 설명할 수 있어야 한다.

- [ ] 커밋 그래프를 구현하고, Git의 커밋 구조가 왜 DAG인지 말로 설명할 수 있다.
- [ ] "부모가 먼저 출력되는 로그"를 만들기 위해 어떤 접근(예: 위상 정렬 성격의 출력)이 필요한지 설명할 수 있다.
- [ ] 두 커밋 사이의 최단 경로를 찾는 방법과 특정 커밋의 모든 조상을 탐색하는 방법을 설명할 수 있다.
- [ ] 정렬 알고리즘을 직접 구현하고, 평균/최악 시간복잡도 및 안정 정렬 여부를 설명할 수 있다.
- [ ] 역색인의 동작 원리와, 순회 검색보다 빠른 이유를 시간복잡도 관점에서 설명할 수 있다.

### 0.4 기능 요구 사항 (필수)

> 원문 — 4. 기능 요구 사항: "다음 요구사항을 모두 만족해야 한다."

각 항목의 ID(`R1`, `R2-1` …)는 이 문서에서 부여한 것이며, PDF 원문에는 번호만 있다.

#### R1. CLI 공통 규칙(문법 표준)

- [ ] **R1-1** 명령어는 대소문자를 구분하지 않는다. (예: `INIT`, `init` 모두 허용)
- [ ] **R1-2** 문자열 인자(사용자명/커밋 메시지/검색 키워드)는 공백을 포함할 수 있다.
- [ ] **R1-3** 공백 포함 시 따옴표로 감싼다. (예: `COMMIT "Add login feature"`)
- [ ] **R1-4** 옵션 표기는 아래 형식으로 통일한다.
  - `SEARCH --author=<name>`
  - `LOG --sort-by=date|author`
- [ ] **R1-5** 잘못된 입력에 대한 최소 에러 메시지를 표준화한다.
  - 예: `Invalid args` , `Unknown branch: <name>` , `Unknown commit: <hash>`

#### R2. 커밋 그래프(핵심 자료구조)

- [ ] **R2-1** 커밋 노드는 최소 필드를 가진다: `hash` , `message` , `author` , `timestamp` , `parents`
- [ ] **R2-2** 각 커밋은 0개 이상의 부모 커밋을 가질 수 있다.
- [ ] **R2-3** 커밋 그래프는 DAG(방향성 비순환) 구조여야 한다.
- [ ] **R2-4** 커밋 저장소는 커밋 hash로 빠르게 찾을 수 있어야 한다(예: 해시맵 기반).
- [ ] **R2-5** 커밋 hash는 세션 내 유일해야 한다(중복 금지).
  - 구현 방식은 자유(예: 증가 카운터 기반, 난수 기반 등) 단, 중복이 발생하지 않도록 보장해야 한다.

#### R3. 역색인(Inverted Index)

- [ ] **R3-1** 검색 시 모든 커밋을 순회하지 않고 후보를 빠르게 가져올 수 있어야 한다.
- [ ] **R3-2** 키워드 추출 기준(최소 기준): 커밋 메시지를 공백 기준으로 분리(split)하고, 소문자(lower)로 정규화한 토큰을 키워드로 저장한다.
- [ ] **R3-3** 최소 2종 인덱스를 지원한다.
  - `keyword -> commit_hash` 목록
  - `author -> commit_hash` 목록

#### R4. 정렬 알고리즘 직접 구현

- [ ] **R4-1** Python 표준 정렬 API 사용 금지: `sorted()` , `list.sort()` 금지
- [ ] **R4-2** 비교 기준을 바꿔 정렬할 수 있어야 한다. (예: 날짜 기준, 작성자 기준)

#### R5. 명령어 기능 요구

- [ ] **R5-1** `INIT <user_name>`
  - 저장소 초기화
  - `main` 브랜치 생성 및 HEAD 설정
  - 현재 사용자(author) 설정
- [ ] **R5-2** `BRANCH <branch_name>`
  - 현재 커밋(HEAD)을 가리키는 새 브랜치 생성
- [ ] **R5-3** `SWITCH <branch_name>`
  - HEAD를 지정한 브랜치로 이동
- [ ] **R5-4** `COMMIT <message>`
  - 현재 HEAD를 부모로 하는 새 커밋 생성
  - 생성 시 역색인(author/keyword)을 갱신
- [ ] **R5-5** `LOG`
  - 학습 목적상 "최신순 나열"이 아니라, **부모 커밋이 항상 자식 커밋보다 먼저 출력되도록** 출력한다(위상 정렬 성격).
  - 출력 포맷은 자유이나, 커밋 `hash` / `author` / `timestamp` / `message` 가 식별 가능해야 한다.
- [ ] **R5-6** `LOG --sort-by=date|author`
  - `date` : `timestamp` 기준으로 정렬(동률 처리 규칙은 자유)
  - `author` : 작성자 이름 기준으로 정렬(동률 처리 규칙은 자유)
- [ ] **R5-7** `PATH <commit1> <commit2>`
  - 최단 경로는 "커밋-부모 연결을 **무방향 간선**으로 간주"했을 때의 최단 경로(간선 수 최소)로 정의한다.
  - 경로가 없으면 `No path` 를 출력한다.
  - 최단 경로가 여러 개면, "경로를 `hash1->hash2->...` 문자열로 만들었을 때 **사전순이 가장 작은 경로**"를 선택한다.
- [ ] **R5-8** `ANCESTORS <commit_hash>`
  - 해당 커밋에서 도달 가능한 모든 조상 커밋을 빠짐없이 출력한다.
- [ ] **R5-9** `SEARCH <keyword>`
  - 키워드가 포함된 커밋 메시지의 커밋들을 출력한다(역색인 기반).
- [ ] **R5-10** `SEARCH --author=<name>`
  - 특정 작성자의 커밋들을 출력한다(역색인 기반).

#### R6. CLI 인터페이스(REPL)

> 출처: PDF "2. 최종 결과물 — 4. CLI 인터페이스(REPL)". 기능 요구 사항 절에는 따로 번호가 없지만 필수 동작이므로 여기에 ID를 부여한다.

- [ ] **R6-1** `mini-git>` 프롬프트에서 명령을 반복 입력받는다.
- [ ] **R6-2** 명령 파싱 → 실행 → 결과 출력이 반복된다.
- [ ] **R6-3** `exit` / `quit` 로 종료한다.

#### R7. 구조/품질 요구

> 출처: PDF "7. 제약 사항 — 구조/품질". 제약이지만 채점 대상 요구사항이므로 ID를 부여한다.

- [ ] **R7-1** 알고리즘 로직(탐색/정렬/인덱싱)은 독립된 함수 또는 클래스로 분리한다.
- [ ] **R7-2** 주요 함수/클래스에 주석 또는 docstring을 작성한다.

### 0.5 보너스 과제 (선택)

#### 원문 — 5. 보너스 과제 (선택)

- [ ] **B1. Diff(간단 비교) 추가**
  - `diff <file1> <file2>` 명령을 추가해 두 텍스트 파일을 줄 단위로 비교한다.
  - 추가/삭제/공통 줄을 구분해 출력한다.
- [ ] **B2. Merge(브랜치 병합) 흉내내기**
  - `merge <branch_name>` 명령을 추가한다.
  - 부모가 2개인 merge commit을 생성한다(현재 브랜치의 HEAD와 대상 브랜치의 HEAD를 부모로).
- [ ] **B3. 정렬 알고리즘 성능 비교**
  - 서로 다른 정렬 알고리즘을 2개 이상 구현하고, 입력 크기에 따른 실행 시간을 비교한다.

> 💡 B2(merge commit)는 R2-2("각 커밋은 0개 이상의 부모 커밋을 가질 수 있다")를 실제로 써먹는 유일한 경로다. 부모를 리스트로 모델링해 두면 B2는 거의 공짜로 붙고, 부모를 단일 값으로 두면 나중에 전체 구조를 뜯어야 한다.
>
> 💡 B1(diff)은 LCS(최장 공통 부분 수열) 계열 DP 연습이며, 파일 입출력이 허용되는 유일한 지점이다(제약 사항의 "문자열/파일 입출력/시간 처리는 사용 가능").

### 0.6 개발 환경 · 제약 사항

#### 원문 — 6. 개발 환경

- Python 3.10 이상

#### 원문 — 7. 제약 사항

**실행**

- 실행 커맨드(예): `python main.py`

**라이브러리 제한 (⚠️ 금지 사항)**

- 🚫 **그래프 전용 라이브러리 사용 금지**
- 🚫 **정렬 관련 표준 API 전부 금지: `sorted()` , `list.sort()` 등**
- ✅ 기본 자료형(예: `list` , `dict` , `set`)과 문자열/파일 입출력/시간 처리는 사용 가능

**구조/품질**

- 알고리즘 로직(탐색/정렬/인덱싱)은 독립된 함수 또는 클래스로 분리한다.
- 주요 함수/클래스에 주석 또는 docstring을 작성한다.

**기능 범위 (구현하지 않아도 되는 것)**

- 파일 내용 추적은 구현하지 않는다(커밋 메타데이터 중심).
- 네트워크 통신은 구현하지 않는다.
- 데이터 영속성(파일 저장)은 구현하지 않아도 된다(메모리 상 동작으로 충분).

> 💡 "정렬 관련 표준 API **전부** 금지 … `등`" 이라는 표현에 주의. `sorted()` / `list.sort()` 만 피하고 `heapq`, `bisect.insort`, `collections.Counter.most_common()`, `max()` 반복으로 정렬을 흉내 내는 것은 문구상 회색지대이며, 과제 의도(정렬을 직접 구현)에 반한다. 비교·교환을 자기 코드로 쓰는 것이 안전하다. (이 문장은 추론이다.)
>
> 💡 "그래프 전용 라이브러리 금지" 는 `networkx` 같은 것을 말한다. `collections.deque` 를 BFS 큐로 쓰는 것은 기본 자료형 범주로 보는 것이 일반적이지만, 논란을 피하려면 `list` 인덱스 포인터로 큐를 직접 구현해도 된다. (이 문장은 추론이다.)

### 0.7 결과/출력 예시

#### 원문 — 8. 결과 예시

> 아래는 정답이 아니라 참고 예시다. 실제 문구와 디자인은 달라도 된다

실행 예시(예시)

```text
mini-git> init "Alice"
Initialized repository.
Current branch: main
Current user: Alice

mini-git> commit "Initial commit"
[main a1b2c3] Initial commit

mini-git> branch feature
Created branch: feature

mini-git> switch feature
Switched to branch: feature

mini-git> commit "Add login feature"
[feature d4e5f6] Add login feature

mini-git> switch main
Switched to branch: main

mini-git> commit "Add payment feature"
[main g7h8i9] Add payment feature

mini-git> log
commit a1b2c3 (Alice, 2024-01-15 09:00:00) [main]
Initial commit
commit d4e5f6 (Alice, 2024-01-15 09:15:00) [feature]
Add login feature
commit g7h8i9 (Alice, 2024-01-15 09:30:00) [main]
Add payment feature

mini-git> path a1b2c3 g7h8i9
Path: a1b2c3 -> g7h8i9

mini-git> search "login"
Found 1 commit:
- d4e5f6: Add login feature

mini-git> log --sort-by=author
commit a1b2c3 (Alice, 2024-01-15 09:00:00)
Initial commit
commit d4e5f6 (Alice, 2024-01-15 09:15:00)
Add login feature
commit g7h8i9 (Alice, 2024-01-15 09:30:00)
Add payment feature
```

> 💡 예시에서 읽어야 할 힌트들:
> - 명령이 전부 **소문자**로 입력되었다 → R1-1(대소문자 무시)이 실제로 동작해야 한다는 증거.
> - `init "Alice"` 처럼 인자에 따옴표가 붙는다 → R1-3 파싱이 따옴표를 벗겨내야 한다.
> - 커밋 출력 헤더가 `[main a1b2c3] <message>` 형태다 → 커밋 hash가 반드시 화면에 나와야 한다(최종 결과물 1번).
> - `log` 출력이 `a1b2c3 → d4e5f6 → g7h8i9` 순이다. 이는 **부모 먼저**(R5-5) 조건을 만족하며, 동시에 생성 순서이기도 하다. 브랜치가 갈라진 그래프에서는 "최신순"과 결과가 달라진다는 점이 핵심.
> - `path a1b2c3 g7h8i9` 결과가 `a1b2c3 -> g7h8i9` 다 → 부모 방향의 역방향으로도 이동했다는 뜻이고, 이것이 R5-7의 "무방향 간선" 정의를 보여준다.
> - `Found 1 commit:` 처럼 결과 개수를 먼저 알려준다(포맷은 자유).

### 0.8 📚 이 과제가 공부하길 원하는 것 (학습 지도)

| 요구사항 | 표면적으로 시키는 일 | 실제로 학습시키려는 개념 | 스스로 답해볼 질문 |
| --- | --- | --- | --- |
| R2-1, R2-2 | 커밋에 `hash/message/author/timestamp/parents` 필드를 넣어라 | **노드-간선 모델링**. `parents`를 리스트로 두는 순간 커밋 이력은 트리가 아니라 그래프가 된다. 인접 리스트(adjacency list) 표현의 실물 예시 | 부모를 리스트로 둬야 하는 이유는? 단일 부모로 두면 무엇이 불가능해지는가(merge)? |
| R2-3 | "DAG 구조여야 한다" | **방향성 비순환 그래프의 정의와 불변식**. 사이클이 있으면 위상 정렬이 불가능하고, 조상 탐색이 무한 루프에 빠진다 | 커밋 그래프에 사이클이 생기면 `LOG`와 `ANCESTORS`에 각각 어떤 일이 일어나는가? 사이클이 구조적으로 불가능한 이유는(부모는 항상 과거의 커밋)? |
| R2-4 | 커밋을 hash로 빠르게 찾아라 | **해시 테이블의 평균 O(1) 조회**. 리스트 선형 탐색 O(N)과의 차이, 그리고 그래프 탐색에서 "다음 노드 꺼내기"가 매번 일어난다는 점 | `dict` 조회가 평균 O(1)인 이유는? 최악 O(N)이 되는 경우는? 커밋 1만 개에서 리스트 탐색 대비 실제 차이는? |
| R2-5 | hash는 세션 내 유일해야 한다 | **식별자 생성 전략과 충돌 회피**. 카운터 기반(결정적·재현 가능) vs 난수/해시 기반(현실적·충돌 확률 존재)의 트레이드오프 | 카운터 기반으로 바꾸면 테스트 재현성과 디버깅은 어떻게 달라지는가? 난수 기반이면 충돌 검사를 어디에 넣어야 하는가? |
| R5-5 | LOG는 부모가 자식보다 먼저 나오게 | **위상 정렬(Topological Sort)**. Kahn 알고리즘(진입차수 큐) vs DFS 후위순회 역순. "정렬"이 비교 기반이 아니라 **의존 관계 기반**일 수 있다는 감각 | Kahn과 DFS 방식의 차이는? 여러 개의 유효한 위상 순서가 존재할 때 무엇으로 tie-break 할 것인가? |
| R5-5 | "최신순 나열이 아니다"라는 단서 | **요구사항 독해**. 익숙한 `git log`의 동작(역시간순)을 그대로 베끼면 틀린다 | 브랜치가 갈라진 그래프에서 "최신순"과 "위상순"의 출력이 실제로 달라지는 최소 예시를 만들 수 있는가? |
| R5-7 | 두 커밋 사이 최단 경로 | **BFS = 비가중 그래프 최단 경로**. DFS로는 최단이 보장되지 않는 이유, 레벨 단위 탐색과 `prev` 포인터 역추적 | 왜 DFS가 아니라 BFS인가? 간선에 가중치가 생기면 무엇으로 바꿔야 하는가(Dijkstra)? |
| R5-7 | "커밋-부모 연결을 무방향 간선으로 간주" | **방향 그래프를 무방향으로 보는 관점 전환**. 자식→부모 간선만으로는 형제 브랜치끼리 도달할 수 없다. 역방향 인접 리스트(children) 구축 필요 | 간선을 "부모 방향만 허용"으로 바꾸면 예시의 `path a1b2c3 g7h8i9` 결과는 어떻게 달라지는가? 구현에서 무엇을 지워야 하는가? |
| R5-7 | 최단 경로가 여럿이면 사전순 최소 | **결정적(deterministic) 알고리즘과 tie-break 규칙**. 같은 입력에 항상 같은 출력이 나오게 만드는 설계. 채점 자동화가 가능해지는 이유 | 탐색 중 이웃을 어떤 순서로 방문해야 사전순 최소가 보장되는가? BFS 도중 tie-break vs 모든 최단 경로 수집 후 비교, 어느 쪽이 맞는가? |
| R5-8 | 도달 가능한 모든 조상 출력 | **도달 가능성(reachability)과 방문 표시**. `visited` 집합이 없으면 다이아몬드 형태 그래프에서 중복 출력·지수적 폭발이 발생 | merge 커밋이 있는 다이아몬드 그래프에서 `visited` 없이 돌리면 몇 번 방문하는가? BFS와 DFS 중 무엇을 써도 되는 이유는? |
| R3-1, R3-3 | 검색 시 전체 순회 금지, 2종 인덱스 | **역색인(Inverted Index)**. 문서→단어를 단어→문서로 뒤집는 것. 검색 엔진의 최소 단위. 조회 O(1) + 결과 크기 k 만큼의 비용 vs 순회 O(N·L) | 역색인이 순회보다 빠른 이유를 N(커밋 수)·L(메시지 길이)·k(매칭 수)로 표현하면? 인덱스가 차지하는 추가 메모리는 얼마인가? |
| R3-2 | split + lower 로 토큰화 | **정규화(normalization)와 토크나이징**. 대소문자·구두점 처리 방침이 검색 품질을 결정. 색인 시점과 질의 시점의 정규화가 **같아야** 한다 | `"Add login feature"` 를 색인하면 `Login` 으로 검색될까? 구두점(`fix: bug.`)은 어떻게 되는가? 부분 문자열 검색은 왜 역색인으로 안 되는가? |
| R5-4 | 커밋 생성 시 역색인 갱신 | **쓰기 시점 인덱싱(write-time indexing)**. 인덱스는 원본과 동기화되어야 하는 파생 데이터. 갱신을 빠뜨리면 검색 결과가 조용히 틀린다 | 인덱스 갱신을 커밋 생성 함수 안에 둘 것인가, 밖에서 호출할 것인가? 각각의 장단점은? |
| R4-1 | `sorted()` / `list.sort()` 금지 | **정렬 알고리즘 직접 구현**. 버블/선택/삽입(O(N²))과 병합/퀵(O(N log N))의 구현과 차이. 파이썬이 감춰둔 것을 열어보기 | 내가 구현한 정렬의 평균/최악 복잡도는? **안정 정렬인가?** 안정성이 왜 문제가 되는가(동률 커밋의 순서)? |
| R4-2 | 비교 기준을 바꿔 정렬 | **비교 함수 분리 = 전략 패턴 / key 함수**. 정렬 알고리즘 본체와 "무엇으로 비교하는가"를 분리하는 설계 | 같은 정렬 함수에 date/author 기준을 주입하려면 시그니처를 어떻게 잡아야 하는가? `key` 방식과 `cmp` 방식의 차이는? |
| R1-2, R1-3 | 따옴표로 감싼 공백 포함 인자 | **렉싱/파싱의 기초**. 단순 `split()` 으로는 `"Add login feature"` 를 못 자른다. 상태 기계(quote 안/밖) 또는 수동 토크나이저 | 따옴표가 닫히지 않은 입력은 어떻게 처리할 것인가? 중첩 따옴표는? |
| R1-5 | 에러 메시지 표준화 | **에러 처리의 일관성과 사용자 인터페이스 계약**. `Invalid args` / `Unknown branch: <name>` / `Unknown commit: <hash>` 를 한 군데서 생성 | 에러 메시지를 각 명령 함수에 흩뿌리는 것과 한 곳에 모으는 것, 나중에 무엇이 달라지는가? 크래시(스택 트레이스)와 에러 메시지의 차이는? |
| R7-1, R7-2 | 알고리즘 로직 분리 + docstring | **관심사의 분리(SoC)와 테스트 가능성**. 그래프 탐색이 CLI 출력 코드와 섞이면 단위 테스트가 불가능해진다 | `LOG`/`PATH`/`ANCESTORS` 가 공유하는 탐색 로직을 어떻게 한 벌로 재사용했는가? 출력 포맷팅은 어디에 있는가? |
| (확장) | — | **스케일 감각**. 커밋이 10배 늘면 어디가 먼저 무너지는가: O(N²) 정렬, 매 검색마다의 전체 순회, 재귀 DFS의 스택 깊이 | 커밋 10,000개에서 병목은 무엇이고, 어떤 자료구조/알고리즘으로 개선하는가? 재귀 조상 탐색이 `RecursionError` 를 내는 깊이는? |
| (확장) | — | **요구사항 변경에 대한 설계 탄력성**. "`LOG --sort-by=author` 가 부모-자식 선후도까지 지켜야 한다"로 강화되면? | 그것은 제약 있는 위상 정렬 문제다. 우선순위 큐 기반 Kahn 알고리즘으로 풀 수 있는가? 왜 단순 정렬로는 안 되는가? |

### 0.9 자주 놓치는 함정

1. **`LOG`를 `git log`처럼 최신순으로 만든다.** 명세는 명시적으로 "최신순 나열이 아니라, 부모 커밋이 항상 자식 커밋보다 먼저 출력되도록"(R5-5) 요구한다. 단일 직선 이력에서는 우연히 같아 보이므로, **브랜치가 갈라진 케이스로 꼭 검증**해야 드러난다.

2. **`PATH`를 부모 방향으로만 탐색한다.** R5-7은 "커밋-부모 연결을 **무방향 간선**으로 간주"라고 못 박았다. 자식 방향 인접 리스트를 만들지 않으면 형제 브랜치 사이의 경로를 찾지 못하고 엉뚱하게 `No path` 가 나온다.

3. **최단 경로 tie-break 규칙을 무시한다.** "최단 경로가 여러 개면 `hash1->hash2->...` 문자열의 **사전순 최소**"(R5-7)는 쉽게 흘려 읽는 조건이다. 아무 최단 경로나 출력하면 요구사항 미달이다.

4. **경로 없음을 `None` / 빈 줄 / 예외로 처리한다.** 출력 문자열은 정확히 `No path` 다(R5-7, 최종 결과물 2번).

5. **`SEARCH --author=` 를 역색인 없이 처리한다.** 키워드 검색만 역색인으로 만들고 author 검색은 전체 순회로 끝내는 경우가 흔하다. R3-3은 **최소 2종**(`keyword -> hash`, `author -> hash`)을 요구한다.

6. **정렬 금지를 우회한다.** `sorted()`/`list.sort()` 만 피하고 `min()` 반복, `heapq`, `dict` 삽입 순서 등에 의존하면 과제의 본체(R4-1)를 건너뛴 것이다. 그리고 **안정 정렬 여부를 설명할 수 있어야** 한다(과제 목표 4번).

7. **`ANCESTORS` 에서 `visited` 를 빠뜨린다.** merge 커밋(B2)이나 다이아몬드 구조에서 같은 조상이 중복 출력되거나 탐색이 폭증한다. "빠짐없이"(R5-8)는 "중복 없이 전부"로 읽어야 한다.

8. **범위를 넘어선 구현에 시간을 쓴다.** 파일 내용 추적·네트워크는 **구현하지 않는다**, 영속성은 **구현하지 않아도 된다**(제약 사항 7). 여기에 투자한 시간은 점수가 되지 않는다.

9. **대소문자/따옴표 파싱을 건너뛴다.** 예시 출력이 전부 소문자 명령(`init`, `commit`, `log`)인데, `INIT` 만 처리하도록 만들면 예시 자체가 재현되지 않는다(R1-1, R1-3).

10. **`exit`/`quit` 종료와 에러 종료를 섞는다.** REPL은 `exit`/`quit` 로만 종료한다(R6-3). 잘못된 입력은 표준 에러 메시지를 출력하고 **루프를 계속 돌아야** 한다 — 프로그램이 죽으면 안 된다. (에러 시 계속 진행한다는 점은 R1-5의 "최소 에러 메시지를 표준화한다"와 REPL 구조에서 도출한 추론이다.)

### 0.10 ✅ 과제 수행 점검 (명세 대조)

> 점검 방식: 저장소의 실제 소스를 명세의 요구사항 ID 와 1:1 대조. 판정 근거는 파일 경로로 명시.
> 저장소 구성은 `main.py`(473줄) + `README.md` + `pyproject.toml` + `tests/` 이며, README 주장은 모두 소스에서 재확인했다. 추가로 실제 REPL 세션과 합성 그래프(diamond)로 실행 검증했다(아래 🧪 절).

**종합 판정: 충족** — 필수 30개 중 충족 30 / 부분 0 / 미충족 0 / 로컬검증불가 0
(보너스 3개는 전부 미구현: B1 ❌ / B2 ❌ / B3 ❌)

> **2026-09-21 추가.** 이 표는 오랫동안 ✅ 체크만 있고 실행되는 검사는 0건이었다. 문서에만 적힌 규칙은 규칙이 아니라 희망이다. 아래 판정의 상당수를 이제 `tests/` 의 자동 검사 **70개**가 함께 지킨다 (`python3 -m unittest discover -s tests`, 0.4초). 어떤 검사가 무엇을 고정하는지와, **각 검사를 일부러 깨뜨려 빨간 불을 확인한 기록**은 아래 「테스트」 절에 있다.

| ID | 요구사항 (요약) | 판정 | 근거 / 비고 |
| --- | --- | --- | --- |
| R1-1 | 명령어 대소문자 무시 | ✅ 충족 | `main.py:460` — `cmd = tokens[0].lower()`, 디스패치 키는 소문자(`main.py:416-425`). 종료어도 `line.lower() in ('exit','quit')`(`main.py:454`). 실행 검증에서 `COMMIT "..."` 대문자 입력이 정상 동작 |
| R1-2 | 문자열 인자에 공백 허용 | ✅ 충족 | `main.py:431-436` `parse_line()` → `shlex.split(line, posix=True)`. 실행 검증: `init "Alice Kim"` → `Current user: Alice Kim` |
| R1-3 | 공백 포함 시 따옴표로 감쌈 | ✅ 충족 | 동일 `main.py:434`. 따옴표는 posix 모드에서 벗겨짐. 닫히지 않은 따옴표는 `ValueError`→`None` 반환(`main.py:435-436`) 후 `Invalid args`(`main.py:457-459`)로 처리 — 크래시 없음 |
| R1-4 | 옵션 표기 `--author=` / `--sort-by=` 통일 | ✅ 충족 | `main.py:320-321`(`--sort-by=` 파싱), `main.py:394-395`(`--author=` 파싱). 값은 `split('=',1)[1]` 로 추출 |
| R1-5 | 에러 메시지 표준화(`Invalid args` 등) | ✅ 충족 | 상수 `INVALID = 'Invalid args'`(`main.py:257`) 사용처 `269,285,296,310,323,327,351,370,391,458`. `Unknown branch: <name>` → `main.py:118`. `Unknown commit: <hash>` → `main.py:354,357,375`. 비고: 문구는 표준화됐으나 `Unknown …` 계열은 3곳에 인라인 생성돼 상수화까지는 안 됨(명세는 문구 표준화만 요구) |
| R2-1 | 커밋 최소 필드 `hash/message/author/timestamp/parents` | ✅ 충족 | `main.py:24-29` `Commit.__init__` 이 5개 필드를 모두 보유. `timestamp`는 epoch float, 표시는 `time_str()`(`main.py:31-32`) |
| R2-2 | 커밋은 0개 이상의 부모 | ✅ 충족 | `main.py:29` `self.parents = list(parents)` — 리스트 모델링. 루트 커밋은 `parents=[]`(`main.py:125`). 다중 부모 처리도 알고리즘 전반에서 정상 동작 확인(합성 merge 노드 테스트 통과). 비고: B2(merge) 미구현이라 **실행 경로상 부모가 2개가 되는 명령은 없다** |
| R2-3 | DAG(비순환) 보장 | ✅ 충족 | `main.py:121-132` — 새 커밋은 항상 기존 HEAD(과거 노드)만 부모로 잡고, 기존 커밋의 `parents`는 절대 수정되지 않아 구조적으로 사이클 불가. 설계 근거는 `README.md 「핵심 자료구조와 알고리즘」` 과 `README.md 「학습 체크리스트」` 에 서술(줄번호 대신 절 이름으로 가리킨다 — 줄번호는 문서가 한 줄만 늘어도 거짓이 된다). 사이클 부재는 `tests/test_minigit.py` 의 위상 정렬 검사가 "출력 커밋 수 == 전체 커밋 수"로 간접 확인한다. 별도 사이클 검증 루틴은 없으나 불변식이 생성 시점에 유지됨 |
| R2-4 | hash로 빠른 조회(해시맵) | ✅ 충족 | `main.py:70` `self.commits = {}  # hash -> Commit`. 조회는 `repo.commits[h]` / `in repo.commits`(`main.py:168,219,332,353,356,412`) 로 평균 O(1) |
| R2-5 | hash 세션 내 유일 | ✅ 충족 | `main.py:86-93` `_new_hash()` — 증가 카운터를 해시 입력에 섞고(`sha1(f'{counter}\|{author}\|{message}\|{ts}')[:7]`) `if h not in self.commits` 충돌 검사 후 재시도. 비고: `INIT` 재실행 시 카운터가 0으로 리셋되나(`main.py:106`) 동시에 `commits`도 비워지므로(`main.py:101`) 살아있는 저장소 내 충돌은 없음 |
| R3-1 | 검색 시 전체 순회 금지 | ✅ 충족 | `main.py:234-239` — `search_keyword`/`search_author` 모두 `dict.get()` 단일 조회. 커밋 전체를 도는 루프 없음(명시 주석 `main.py:235`) |
| R3-2 | split + lower 토큰 정규화 | ✅ 충족 | `main.py:134-136` — `for token in message.split(): key = token.lower()`. 질의 시점도 동일 정규화(`main.py:236` `keyword.lower()`) → 실행 검증에서 `search LOGIN` 이 `Add login feature` 를 찾음 |
| R3-3 | 최소 2종 인덱스(keyword/author) | ✅ 충족 | `main.py:76-77` `keyword_index` / `author_index` 선언, 갱신은 `main.py:136,137`. author 검색도 순회가 아닌 인덱스 사용(`main.py:239`) — 명세 0.9의 함정 5를 피함 |
| R4-1 | `sorted()` / `list.sort()` 금지 | ✅ 충족 | `grep -nE '\bsorted\(\|\.sort\(\|heapq\|bisect\|most_common\|functools\.cmp' main.py` → **0건**. import는 `hashlib, shlex, sys, time, collections.deque, datetime` 뿐(`main.py:10-15`)으로 그래프 라이브러리도 없음. 정렬은 직접 구현한 머지 정렬(`main.py:38-60`). 위상 정렬의 최소 선택도 `min()` 없이 수동 루프(`main.py:149-154`), 검색 중복 제거도 수동(`main.py:404-409`) |
| R4-2 | 비교 기준 교체 가능 | ✅ 충족 | `main.py:38` `merge_sort(items, key)` — key 주입형. date 기준 `main.py:336`, author 기준 `main.py:338`, 조상 출력 정렬 `main.py:382` 로 3가지 기준 재사용 |
| R5-1 | `INIT <user_name>` (초기화/main/HEAD/author) | ✅ 충족 | `main.py:99-109` — `branches={'main':None}`, `head_branch='main'`, `author=user_name`. 출력 `main.py:272-274` |
| R5-2 | `BRANCH <name>` HEAD 가리키는 새 브랜치 | ✅ 충족 | `main.py:111-114` `self.branches[name] = self.head_commit()`. 중복 이름은 `Branch already exists: <name>`(`main.py:113`) |
| R5-3 | `SWITCH <name>` HEAD 이동 | ✅ 충족 | `main.py:116-119`. 없는 브랜치는 `Unknown branch: <name>` |
| R5-4 | `COMMIT <message>` + 역색인 갱신 | ✅ 충족 | `main.py:121-138` — 부모=현재 HEAD(`124-125`), 브랜치 끝 이동(`132`), 역색인 갱신이 커밋 생성 함수 **안**에 있음(`134-137`). 출력에 hash 포함 `[{branch} {hash}] {message}`(`main.py:312`) |
| R5-5 | `LOG` 부모가 자식보다 먼저(위상 정렬) | ✅ 충족 | `main.py:141-161` Kahn 알고리즘(진입차수=부모 수, `children` 역인접 리스트 `main.py:71,128-130`). tie-break `(timestamp, hash)`(`main.py:150-154`)로 결정적. 출력에 hash/author/timestamp/message 모두 포함(`main.py:251`). **브랜치 분기 케이스로 실행 검증**했고 부모-먼저 불변식 True |
| R5-6 | `LOG --sort-by=date\|author` | ✅ 충족 | `main.py:318-338` — 값 검증(`325-327`) 후 `merge_sort` 호출. date는 `(timestamp,hash)`, author는 `(author,timestamp,hash)` 키. 잘못된 값은 `Invalid args` |
| R5-7 | `PATH` 무방향 최단 경로 / `No path` / 사전순 최소 | ✅ 충족 | `main.py:163-215` — 무방향 인접 리스트 `adj[h].add(p); adj[p].add(h)`(`176-178`), BFS 거리(`181-188`), 경로 없음 시 `None`→`No path` 출력(`main.py:360-361`), 사전순 최소는 레벨별 `best[v]=min(best[u]+'->'+v)` DP(`195-215`). 실행 검증: 형제 브랜치 간 경로 `afdff43->82f1d75->82856af` 산출, 분리된 루트끼리는 `No path`. 합성 diamond 로 사전순 tie-break도 확인 |
| R5-8 | `ANCESTORS` 도달 가능한 모든 조상 | ✅ 충족 | `main.py:217-231` — 명시 스택 DFS + `visited` 집합으로 중복/폭증 방지(`221-230`). 자기 자신은 제외하고 부모부터 시작(`222`). 미존재 hash는 `Unknown commit`(`main.py:375`). diamond 테스트에서 조상 3개 중복 없이 수집 |
| R5-9 | `SEARCH <keyword>` (역색인) | ✅ 충족 | `main.py:398` → `search_keyword`(`234-236`). 결과 중복 제거 후 `Found N commit(s):` + `- hash: message`(`main.py:403-413`) |
| R5-10 | `SEARCH --author=<name>` (역색인) | ✅ 충족 | `main.py:394-396` → `search_author`(`238-239`). 공백 포함 이름은 `search "--author=Alice Kim"` 로 동작 확인 |
| R6-1 | `mini-git>` 프롬프트 반복 입력 | ✅ 충족 | `main.py:444` `input('mini-git> ')`, `main.py:442` 무한 루프 |
| R6-2 | 파싱 → 실행 → 출력 반복 | ✅ 충족 | `main.py:456-469` — 파싱(`456`) → 디스패치(`462-467`) → 핸들러 내부 출력. 핸들러 예외는 `except Exception`(`468-469`)으로 잡아 **루프가 죽지 않음**(명세 0.9 함정 10 회피). EOF/Ctrl-C 처리도 있음(`445-450`) |
| R6-3 | `exit` / `quit` 종료 | ✅ 충족 | `main.py:454-455` |
| R7-1 | 알고리즘 로직을 독립 함수/클래스로 분리 | ✅ 충족 | 정렬은 모듈 수준 순수 함수(`main.py:38-60`), 그래프/색인은 `Repository` 메서드(`141,163,217,234,238`), 출력 포맷은 `format_commit_line`(`245-251`), CLI 파싱/디스패치는 `cmd_*` + `main()`(`267-469`)로 계층 분리. 알고리즘 함수 안에 `print` 없음 → 단위 테스트 가능(실제로 그렇게 검증함) |
| R7-2 | 주요 함수/클래스에 주석/docstring | ✅ 충족 | 모듈 docstring `main.py:1-8`, `Commit`(`22`), `merge_sort`(`39`, 복잡도·안정성 명시), `Repository`(`67`), `_new_hash`(`87`), `topological_log`(`142`), `shortest_path`(`164-167`), `ancestors`(`218`), `parse_line`(`432`). 필드에도 인라인 주석(`70-78`). 비고: `cmd_*` 핸들러 8개는 docstring이 없음(이름이 자명한 얇은 래퍼라 "주요 함수" 요건은 충족으로 본다) |

#### 보너스 과제

| ID | 요구사항 (요약) | 판정 | 근거 / 비고 |
| --- | --- | --- | --- |
| B1 | `diff <file1> <file2>` 줄 단위 비교 | ❌ 미충족 | `COMMANDS` 딕셔너리(`main.py:416-425`)에 `diff` 없음. `grep -niE 'diff' main.py` → 0건. LCS/DP 코드도 없음 |
| B2 | `merge <branch_name>` 부모 2개 merge commit | ❌ 미충족 | `COMMANDS`(`main.py:416-425`)에 `merge` 없음. `grep -niE '\bmerge\b' main.py` 는 `merge_sort`(정렬)만 매칭. `Repository.commit`(`main.py:124-125`)은 부모를 항상 최대 1개(`[parent]`)로만 만든다 |
| B3 | 정렬 알고리즘 2개 이상 + 입력 크기별 실행시간 비교 | ❌ 미충족 | 구현된 정렬은 `merge_sort` 1종뿐(`main.py:38-60`). `grep -niE 'bubble\|insertion\|selection\|quick_sort\|bench\|perf' main.py` → 0건. 벤치마크 스크립트/결과표도 없음(`README.md` 전체에 없음) |

#### 🔍 발견된 격차와 보완 제안

필수 요구사항(R1~R7)에서는 미충족/부분 충족 항목이 **없음**. 아래는 보너스 미구현과 경미한 품질 사항이다.

1. **B1 (diff) 미구현** — `diff <file1> <file2>` 명령이 없다.
   → `COMMANDS`에 `'diff': cmd_diff` 를 추가하고, LCS(최장 공통 부분 수열) DP로 두 파일의 줄 배열을 비교해 `+`/`-`/` ` 접두사로 출력하면 된다. 파일 입출력은 제약 사항에서 허용된 영역이다.

2. **B2 (merge) 미구현** — 가장 아깝다. 자료구조(`parents`가 리스트)·알고리즘(위상 정렬/BFS/조상 탐색)이 **이미 다중 부모를 정상 처리**하도록 짜여 있음을 합성 diamond 테스트로 확인했다. 즉 `Repository.merge(branch)` 하나만 추가하면 거의 공짜로 붙는다.
   → `main.py:121` `commit()` 을 `parents` 인자를 받도록 일반화하거나, `parents=[self.head_commit(), self.branches[other]]` 로 커밋을 만드는 `merge()` 를 추가하고 `COMMANDS`에 등록. 이걸 붙여야 R5-7의 "최단 경로가 여러 개일 때 사전순 최소" tie-break 코드(`main.py:205-212`)가 **실제 CLI 경로에서 실행 가능**해진다. 현재는 모든 커밋의 부모가 ≤1개라 그래프가 포레스트이고, 두 노드 사이 최단 경로가 항상 유일해서 그 로직이 죽은 코드처럼 남아 있다.

3. **B3 (정렬 성능 비교) 미구현** — 정렬이 머지 정렬 1종뿐이다.
   → 삽입 정렬(또는 버블)을 하나 더 직접 구현하고, `time.perf_counter()` 로 n = 100/1,000/10,000 에서 실행시간을 재 README에 표로 남기면 O(N²) vs O(N log N) 체감까지 포함해 과제 목표 4번(복잡도·안정성 설명)을 강화할 수 있다.

4. **(경미, 명세 외) 저장소 위생** — `.gitignore` 는 2026-09-21 에 추가했다(`__pycache__/`, `*.py[cod]`). 다만 **이미 추적 중인 파일에는 `.gitignore` 가 효력이 없어서**, 컴파일 산출물 `__pycache__/main.cpython-314.pyc` 는 지금도 `git ls-files` 에 남아 있다.
   → 남은 조치는 `git rm -r --cached __pycache__` 한 번(커밋 필요). 그 전까지는 `main.py` 를 고쳐도 낡은 `.pyc` 가 함께 커밋돼 있어, 받는 쪽에서 캐시가 유효 판정되면 검사가 거짓으로 통과할 수 있다.

5. **(경미, 명세 외) 미사용 import** — `main.py:12` `import sys` 는 파일 전체에서 한 번도 쓰이지 않는다(`grep -n 'sys\.' main.py` → 0건). 삭제 권장.

6. **(참고) 회색지대 없음** — `collections.deque`(`main.py:14,182`)를 BFS 큐로 쓰는 것은 명세 💡가 언급한 "기본 자료형 범주"에 해당하며, 금지된 정렬 API·그래프 라이브러리는 실제 grep 결과 전혀 사용되지 않았다. 정렬 금지 우회(`min()`/`heapq`/`dict` 삽입 순서 의존)도 없다.

#### 🧪 실행 검증 기록

> 저장소는 **읽기 전용으로만** 다뤘다. `main.py` 를 스크래치패드(`…/scratchpad/b32run/`)에 복사해 컴파일·실행했고, 저장소 안에서는 어떤 명령도 실행/수정하지 않았다(`git status --porcelain` 결과 clean 확인).

1. `python3 --version` → **Python 3.14.4** (명세 요구 3.10+ 충족)
2. `python3 -m py_compile main.py` (복사본) → **PY_COMPILE_OK** (문법 오류 없음)
3. `grep -nE '\bsorted\(|\.sort\(|heapq|bisect|most_common|functools\.cmp|networkx|igraph|graph_tool' main.py` → **소스 0건**(README 설명문 1줄만 매칭) — R4-1 / 라이브러리 제한 위반 없음
4. **REPL 전 구간 스크립트 실행** (`builtins.input` 을 대체해 `main()` 을 그대로 구동, 커밋 hash는 출력에서 추출해 후속 명령에 주입):
   - `init "Alice Kim"` → `Initialized repository. / Current branch: main / Current user: Alice Kim`
   - `commit "Initial commit"` → `[main 82f1d75] Initial commit`, `branch feature` → `Created branch: feature`, `switch feature` → OK
   - `COMMIT "Add login feature"`(**대문자 명령**) → `[feature afdff43] Add login feature` — R1-1 확인
   - `switch main` 후 `commit "Add payment FEATURE"` → `[main 82856af]` (분기 그래프 생성)
   - `log` → `82f1d75(Initial) → afdff43(login) → 82856af(payment)` — 분기 그래프에서 **부모가 자식보다 먼저** 출력됨 (R5-5)
   - `log --sort-by=date`, `log --sort-by=author` → 정상 출력 (R5-6)
   - `path afdff43 82856af`(형제 브랜치) → `Path: afdff43->82f1d75->82856af` — **무방향 간선 처리 확인** (R5-7)
   - `path 82f1d75 82856af` → `Path: 82f1d75->82856af`
   - `ancestors 82856af` → `82f1d75 …` / `ancestors 82f1d75` → `(no ancestors)` (R5-8)
   - `search LOGIN` → `Found 1 commit:` (대소문자 정규화), `search feature` → `Found 2 commits:` (중복 제거 정상)
   - `search "--author=Alice Kim"` → `Found 3 commits:`, `search --author=Nobody` → `Found 0 commits.` (R5-10)
   - 에러 경로: `path 82f1d75 deadbee`/`ancestors deadbee` → `Unknown commit: deadbee`, `switch nope` → `Unknown branch: nope`, `branch`(인자 없음)·`commit Add login feature`(따옴표 없음)·`log --sort-by=xyz`·`commit "unclosed`(따옴표 미닫힘) → 모두 `Invalid args`, `bogus arg` → `Unknown command: bogus` — **전 케이스에서 REPL이 죽지 않고 계속 동작** (R1-5, R6-2)
   - 분리 그래프: `init Bob` → `branch orphan` → `commit "root A"`(main) → `switch orphan` → `commit "root B"` (부모 없는 두 번째 루트) → `path 6c25f95 6a6454e` → **`No path`** (R5-7 경로 없음 처리)
   - `exit` → 정상 종료 (R6-3)
5. **알고리즘 단위 검증** (합성 diamond 그래프를 `Repository` 에 직접 구성 — merge 커밋이 있다고 가정):
   - `shortest_path('aaaaaa1','ddddd04')` → `aaaaaa1->bbbbbb2->ddddd04` : 동일 길이 후보 2개 중 **사전순 최소** 선택 확인 (R5-7 tie-break)
   - `ancestors('ddddd04')` → `{aaaaaa1, bbbbbb2, ccccc03}` : 다이아몬드에서 **중복 없이 3개** (R5-8)
   - `topological_log()` → `['aaaaaa1','bbbbbb2','ccccc03','ddddd04']`, 전 간선에 대해 `pos[parent] < pos[child]` **True**, 출력 개수 = 커밋 개수 (R5-5)
   - `merge_sort` : 동률 키 입력 `[(3,a),(1,b),(3,c),(2,d),(1,e)]` → `[(1,b),(1,e),(2,d),(3,a),(3,c)]` — **안정성 확인**. 난수 200개 정렬 결과 정렬성·길이 보존 True (R4-1/R4-2)
6. 미실행 항목: 없음. (네트워크·설치가 필요한 검증 항목 자체가 이 과제에는 없다.)

---

## 실행

```
python main.py
```

`mini-git>` 프롬프트가 뜨면 명령을 입력하고, `exit` 또는 `quit`으로 종료합니다.

> Python 3.10+ 필요. 표준 라이브러리만 사용합니다. 데이터는 메모리에만 저장되며 종료 시 사라집니다.

## 테스트

요구사항은 README 의 ✅ 표가 아니라 **실행되는 검사**가 지킨다.
표준 라이브러리 `unittest` 로만 작성돼 있어 설치할 것이 없다.

```
python3 -m unittest discover -s tests
```

`pytest` 가 설치돼 있으면 `pytest -q` 로도 같은 검사가 돈다(`pyproject.toml` 에 설정).

| 파일 | 고정하는 불변식 |
| --- | --- |
| `tests/test_minigit.py` | 위상 정렬(부모가 자식보다 먼저), 최단 경로(간선 수 최소 → 동률이면 사전순 최소), 머지 정렬 **안정성**, 역색인 결과 == 전체 순회 결과 |
| `tests/test_cli.py` | `main.py` 를 인터프리터에 넘기면 REPL 이 실제로 뜨고, 잘못된 입력 12종에도 죽지 않는다 |
| `tests/test_constraints.py` | 0.6 의 금지 사항(정렬 표준 API·라이브러리 화이트리스트)과 구조 요구(R3-1/R7-1/R7-2)를 AST 로 강제 |
| `tests/test_readme_refs.py` | 0.10 이 코드를 가리키는 `main.py:줄번호` 근거가 아직 참인지 |

마지막 항목이 특이해 보이지만 이유가 있다. 0.10 은 판정 근거를 전부 `파일:줄번호` 로 적는데,
**줄번호는 리팩터링에 견디지 못하는 좌표다.** `main.py` 위쪽에 한 줄만 끼워 넣어도 아래 근거 70개가
조용히 거짓이 된다. 이 검사는 README 가 스스로 인용해 둔 코드 조각이 정말 그 줄에 있는지 대조한다
(기댓값을 따로 적지 않으므로 같은 사실이 두 곳에 생기지 않는다).

### 검사가 정말 깨지는지 확인한 기록

깨지지 않는 검사는 검사가 아니다. 도입 시점에 각 불변식을 한 번씩 일부러 부숴
빨간 불을 확인하고 원복했다(2026-09-21).

| 일부러 넣은 결함 | 결과 |
| --- | --- |
| Kahn 의 `indeg[child] == 0` → `>= 0` | **3건 실패** — 위상 정렬 붕괴 |
| 위상 정렬 tie-break 비교 `<` → `>` | **3건 실패** — 결정적 출력 순서 상실 |
| 최단 경로 사전순 비교 `<` → `>` | **5건 실패** |
| 머지 정렬 `<=` → `<` | **3건 실패** — 안정 정렬 아님 |
| 역색인의 `token.lower()` → `token` | **14건 실패** |
| `import heapq` 추가 | **3건 실패** — 제약 위반 + 줄 밀림 감지 |
| `main.py` 맨 앞에 빈 줄 하나 삽입 | **2건 실패** — 0.10 줄번호 근거 밀림 감지 |
| 0.10 의 절 이름 참조를 없는 절로 바꿈 | **1건 실패** |
| 절 이름 참조를 다시 줄번호로 되돌림 | **2건 실패** |
| REPL 종료 조건 `('exit','quit')` 를 없앰 | **2건 실패** — *검수 중 추가된 행* |

> ⚠️ 드릴 도중 한 번, 돌연변이가 아니라 **오래된 `__pycache__` 바이트코드** 때문에 검사가
> 거짓으로 통과한 적이 있다(수정 전후 파일 크기와 mtime 초가 같아 캐시가 유효 판정됨).
> `.gitignore` 에 `__pycache__/` 를 넣은 이유이고, 검사 결과를 의심할 때 먼저 지워볼 곳이다.

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
