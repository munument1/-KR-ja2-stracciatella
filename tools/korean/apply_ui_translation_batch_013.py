#!/usr/bin/env python3
"""Apply Korean UI translation batch 013.

Focus: stat-change fragments consumed by the Korean-only formatter installed by
apply_korean_stat_message_patch.py.  The Korean formatter emits messages such
as: "Fox: 체력 1포인트 증가".
"""

from __future__ import annotations

import json
from apply_ui_translation_batch_001 import PLACEHOLDER_RE, TARGET, get_value, set_value

RANGES: list[tuple[str, int, list[str]]] = [
    ("sPreStatBuildString", 0, [
        "감소",
        "증가",
        "포인트",
        "포인트",
        "레벨",
        "레벨",
    ]),
    ("sStatGainStrings", 0, [
        "체력",
        "민첩성",
        "손재주",
        "지혜",
        "의술",
        "폭발물",
        "기계",
        "사격술",
        "경험치",
        "힘",
        "통솔력",
    ]),
]


def check_and_set(data: dict, key: str, index: int, korean: str) -> int:
    current = get_value(data, key, index)
    if PLACEHOLDER_RE.findall(current) != PLACEHOLDER_RE.findall(korean):
        raise SystemExit(
            f"Placeholder mismatch at {key}[{index}]: "
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
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    print(f"Applied Korean UI batch 013: {changed}/{total} entries changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
