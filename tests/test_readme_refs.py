"""README `0.10` 절이 코드를 가리키는 `main.py:줄번호` 근거가 아직 참인지 검사한다.

왜 필요한가. 0.10 은 요구사항 30개의 판정 근거를 전부 `파일:줄번호` 로 적는다.
줄번호는 리팩터링에 견디지 못하는 좌표다 — main.py 위쪽에 한 줄만 끼워 넣어도
아래 근거 70개가 조용히 거짓이 된다. 실제로 이 계열의 사고가 다른 저장소에서
68건 발생했고, 그때 아무 검사도 빨간 불을 내지 않았다.

이 파일은 기댓값을 손으로 적지 않는다. **README 가 스스로 적어 둔 코드 인용문**을
읽어서, 그 문장이 정말 그 줄에 있는지 대조한다. 같은 사실을 두 곳에 두지 않으려는
것이다.

줄번호가 밀어졌을 때 할 일:
  1. `python3 -m unittest discover -s tests` 가 알려주는 줄을 확인한다.
  2. 0.10 표의 근거를 새 줄번호로 고치거나, 더 나은 방법으로
     함수·클래스 이름 같은 안정적 좌표로 바꾼다.
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(REPO_ROOT, 'README.md')
MAIN_PATH = os.path.join(REPO_ROOT, 'main.py')

# 이 정도는 잡혀야 검사가 '아무것도 못 찾아서' 통과하는 일이 없다.
MIN_LINE_REFS = 60
MIN_QUOTED_ANCHORS = 8

LINE_REF = re.compile(r'`main\.py:([\d][\d,\-]*)`')
# `main.py:NNN` — `인용된 코드`   (또는 대시 없이 바로 이어지는 경우)
QUOTED_REF = re.compile(r'`main\.py:(\d+)`\s*(?:—|–|-)?\s*`([^`]+)`')
DECLARED_LENGTH = re.compile(r'`main\.py`\((\d+)줄\)')
# 줄번호 대신 쓰는 안정적 좌표: `README.md 「절 이름」`
SECTION_REF = re.compile(r'`README\.md 「([^」]+)」`')
HEADING = re.compile(r'^#{1,6}\s+(.*?)\s*$', re.MULTILINE)


def read(path):
    with open(path, encoding='utf-8') as handle:
        return handle.read()


def main_lines():
    return read(MAIN_PATH).splitlines()


def normalize(text):
    """들여쓰기·정렬용 공백은 근거의 본질이 아니다."""
    return ' '.join(text.split())


def referenced_line_numbers():
    numbers = []
    for group in LINE_REF.findall(read(README_PATH)):
        for chunk in group.split(','):
            chunk = chunk.strip()
            if not chunk:
                continue
            if '-' in chunk:
                start, _, end = chunk.partition('-')
                numbers.extend([int(start), int(end)])
            else:
                numbers.append(int(chunk))
    return numbers


class ReadmeReferenceTest(unittest.TestCase):
    def test_enough_refs_are_actually_found(self):
        """검사가 공회전하지 않는지부터 확인한다."""
        self.assertGreaterEqual(
            len(referenced_line_numbers()), MIN_LINE_REFS,
            'README 에서 `main.py:줄번호` 근거를 거의 못 찾았다. '
            '표 형식이 바뀌었다면 이 검사의 정규식부터 고쳐라.',
        )
        self.assertGreaterEqual(
            len(QUOTED_REF.findall(read(README_PATH))), MIN_QUOTED_ANCHORS,
            '코드 인용이 붙은 근거가 너무 적다 — 앵커가 사라지면 이 검사는 무력해진다.',
        )

    def test_every_referenced_line_exists(self):
        total = len(main_lines())
        out_of_range = [n for n in referenced_line_numbers() if not 1 <= n <= total]
        self.assertEqual(
            out_of_range, [],
            f'main.py 는 {total}줄인데 README 가 없는 줄을 근거로 든다: {out_of_range}',
        )

    def test_quoted_code_is_really_on_that_line(self):
        """README 가 인용한 코드가 그 줄에 실제로 있는지 — 줄 밀림 감지기."""
        lines = main_lines()
        mismatches = []
        for raw_number, quoted in QUOTED_REF.findall(read(README_PATH)):
            number = int(raw_number)
            actual = normalize(lines[number - 1]) if 1 <= number <= len(lines) else '<범위 밖>'
            expected = normalize(quoted)
            needle = expected[:-2] if expected.endswith('()') else expected
            if needle not in actual:
                mismatches.append(f'main.py:{number} 기대 {needle!r} / 실제 {actual!r}')
        self.assertEqual(mismatches, [], 'README 0.10 의 줄번호 근거가 코드와 어긋난다:\n' +
                         '\n'.join(mismatches))

    def test_section_references_resolve(self):
        """`README.md 「절 이름」` 형태의 자기 참조는 실제 제목을 가리켜야 한다.

        줄번호 근거 하나(`README.md:108`)가 「0. 과제 명세」 삽입으로 435줄 밀려
        엉뚱한 곳을 가리키고 있었다. 절 이름은 문서가 길어져도 밀리지 않고,
        제목이 바뀌면 이 검사가 바로 잡는다.
        """
        text = read(README_PATH)
        refs = SECTION_REF.findall(text)
        self.assertGreaterEqual(len(refs), 2, '절 이름 참조를 찾지 못했다 — 표기가 바뀌었는가?')
        headings = {match.group(1).strip() for match in HEADING.finditer(text)}
        missing = [name for name in refs if name not in headings]
        self.assertEqual(missing, [], f'README 가 없는 절을 가리킨다: {missing}')

    def test_no_bare_readme_line_number_refs(self):
        """README 가 자기 자신을 줄번호로 가리키지 않는지.

        문서 안의 줄번호는 문장 한 줄만 추가돼도 거짓이 된다. 절 이름을 써라.
        """
        stale = re.findall(r'`README\.md:\d[\d,\-]*`', read(README_PATH))
        self.assertEqual(stale, [], f'줄번호로 된 README 자기 참조가 남아 있다: {stale}')

    def test_declared_file_length_matches(self):
        """0.10 머리말의 '`main.py`(N줄)' 은 줄 밀림의 조기 경보다.

        여기서 실패하면 아래 근거 70개도 같이 의심해야 한다.
        """
        declared = DECLARED_LENGTH.search(read(README_PATH))
        self.assertIsNotNone(declared, "0.10 머리말의 '`main.py`(N줄)' 표기가 사라졌다")
        self.assertEqual(
            int(declared.group(1)), len(main_lines()),
            'main.py 의 줄 수가 README 0.10 의 선언과 다르다 — '
            '표의 `main.py:줄번호` 근거가 밀렸을 수 있으니 함께 갱신하라.',
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
