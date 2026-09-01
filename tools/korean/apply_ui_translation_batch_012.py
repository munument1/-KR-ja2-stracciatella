#!/usr/bin/env python3
"""Apply Korean UI translation batch 012.

Focus: credits text and generic vehicle labels. Personal names, company/site
brand names, coordinates, currency amounts, URLs and technical units remain
unchanged intentionally.
"""

from __future__ import annotations

import json
from apply_ui_translation_batch_001 import PLACEHOLDER_RE, TARGET, get_value, set_value

RANGES: list[tuple[str, int, list[str]]] = [
    ("gzCreditNameTitle", 0, [
        "게임 내부 시스템 프로그래머",
        "공동 디자이너/작가",
        "전략 시스템/에디터 프로그래머",
        "프로듀서/공동 디자이너",
        "공동 디자이너/맵 디자이너",
        "아티스트",
        "베타 테스트 코디네이터/지원",
        "특급 아티스트",
        "사운드 전문가",
        "화면 디자이너/아티스트",
        "수석 아티스트/애니메이터",
        "수석 프로그래머",
        "프로그래머",
        "전략 시스템/게임 밸런스 프로그래머",
        "초상화 아티스트",
    ]),
    ("pShortVehicleStrings", 0, [
        "엘도.", "험머", "트럭", "지프", "탱크", "헬기",
    ]),
    ("zVehicleName", 0, [
        "엘도라도", "험머", "트럭", "지프", "탱크", "헬기",
    ]),
]

INDEXED: list[tuple[str, int, str]] = [
    ("gzCreditNameFunny", 1, "(구두점은 아직 배우는 중)"),
    ("gzCreditNameFunny", 2, "(\"다 끝났어. 그냥 고치는 중이야\")"),
    ("gzCreditNameFunny", 3, "(이런 거 하기엔 너무 늙어 가는 중)"),
    ("gzCreditNameFunny", 4, "(그리고 Wizardry 8도 작업 중)"),
    ("gzCreditNameFunny", 5, "(총으로 협박받아 QA까지 맡음)"),
    ("gzCreditNameFunny", 6, "(우리를 버리고 CFSA로 감 - 이해가 안 되네...)"),
    ("gzCreditNameFunny", 9, "(데드헤드이자 재즈 애호가)"),
    ("gzCreditNameFunny", 10, "(본명은 로버트)"),
    ("gzCreditNameFunny", 11, "(유일하게 책임감 있는 사람)"),
    ("gzCreditNameFunny", 12, "(이제 모터크로스로 돌아갈 수 있음)"),
    ("gzCreditNameFunny", 13, "(Wizardry 8에서 훔쳐 옴)"),
    ("gzCreditNameFunny", 14, "(아이템과 로딩 화면도 작업함!)"),
]

SCALARS: list[tuple[str, str]] = [
    ("gzCopyrightText", "Copyright (C) 1999 Sir-tech Canada Ltd. 모든 권리 보유."),
]


def check_and_set(data: dict, key: str, index: int | None, korean: str) -> int:
    current = get_value(data, key, index)
    if PLACEHOLDER_RE.findall(current) != PLACEHOLDER_RE.findall(korean):
        where = key if index is None else f"{key}[{index}]"
        raise SystemExit(
            f"Placeholder mismatch at {where}: "
            f"{PLACEHOLDER_RE.findall(current)} != {PLACEHOLDER_RE.findall(korean)}"
        )
    if current == korean:
        return 0
    set_value(data, key, index, korean)
    return 1


def main() -> int:
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    changed = 0
    total = 0
    for key, start, translations in RANGES:
        for offset, korean in enumerate(translations):
            changed += check_and_set(data, key, start + offset, korean)
            total += 1
    for key, index, korean in INDEXED:
        changed += check_and_set(data, key, index, korean)
        total += 1
    for key, korean in SCALARS:
        changed += check_and_set(data, key, None, korean)
        total += 1
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    print(f"Applied Korean UI batch 012: {changed}/{total} entries changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
