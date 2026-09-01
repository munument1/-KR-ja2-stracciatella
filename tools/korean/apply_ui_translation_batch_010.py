#!/usr/bin/env python3
"""Apply Korean UI translation batch 010.

Focus: repair completion, stat/time labels, AIM sorting, Iron Man/Dead Is
Dead warnings, departing-merc equipment messages and map sorting.
`sPreStatBuildString` is intentionally deferred because it is an English
sentence-fragment composition API and needs call-site-aware Korean grammar.
"""

from __future__ import annotations

import json
from apply_ui_translation_batch_001 import PLACEHOLDER_RE, TARGET, get_value, set_value

RANGES: list[tuple[str, int, list[str]]] = [
    ("sRepairsDoneString", 0, [
        "%s이(가) 자신의 아이템 수리를 마쳤습니다.",
        "%s이(가) 모두의 총기와 방어구 수리를 마쳤습니다.",
        "%s이(가) 모두의 장착 아이템 수리를 마쳤습니다.",
        "%s이(가) 모두의 휴대 아이템 수리를 마쳤습니다.",
    ]),
    ("sStatGainStrings", 0, [
        "체력.", "민첩성.", "손재주.", "지혜.", "의술.", "폭발물.", "기계.", "사격술.", "경험치.", "힘.", "통솔력.",
    ]),
    ("sTimeStrings", 0, ["일시정지", "보통", "5분", "30분", "60분", "6시간"]),
    ("str_aim_sort_list", 0, [
        "가격", "경험", "사격술", "의술", "폭발물", "기계", "오름차순", "내림차순",
    ]),
    ("str_stat_list", 0, [
        "체력", "민첩성", "손재주", "힘", "통솔력", "지혜", "경험 레벨", "사격술", "기계", "폭발물", "의술",
    ]),
    ("wMapScreenSortButtonHelpText", 0, [
        "이름순 정렬 (|F|1)",
        "임무순 정렬 (|F|2)",
        "수면 상태순 정렬 (|F|3)",
        "위치순 정렬 (|F|4)",
        "목적지순 정렬 (|F|5)",
        "출발 시간순 정렬 (|F|6)",
    ]),
]

SCALARS: list[tuple[str, str]] = [
    ("str_aim_sort_ascending", "오름차순"),
    ("str_aim_sort_descending", "내림차순"),
    ("str_aim_sort_experience", "경험"),
    ("str_aim_sort_explosives", "폭발물"),
    ("str_aim_sort_marksmanship", "사격술"),
    ("str_aim_sort_mechanical", "기계"),
    ("str_aim_sort_medical", "의술"),
    ("str_aim_sort_price", "가격"),
    ("str_arrival_rerouted", "예정 투입 지점인 %s 구역이 적에게 점령되어 신병의 도착 지점을 %s 구역으로 변경합니다."),
    ("str_bobbyr_guns_num_guns_that_use_ammo", "팀에 이 탄약을 사용하는 무기가 %d정 있습니다."),
    ("str_ceramic_plates_smashed", "%s의 세라믹 방탄판이 산산조각 났습니다!"),
    ("str_dead_is_dead_mode_enter_name", "이제 저장 화면으로 이동합니다. 저장 슬롯을 하나 선택하고 게임 이름을 정하십시오. 이 슬롯은 이번 게임에 고정되며 변경할 수 없습니다!"),
    ("str_dead_is_dead_mode_warning", "영구 사망 모드를 선택했습니다. 실수하더라도 이전 저장 파일을 불러올 수 없어 게임이 훨씬 어려워집니다. 나갈 때 자동으로 저장됩니다. 이 설정은 게임 전체에 영향을 줍니다. 영구 사망 모드로 플레이하시겠습니까?"),
    ("str_he_leaves_drops_equipment", "%s은(는) 곧 떠나며 장비를 %s에 두고 갑니다."),
    ("str_he_leaves_where_drop_equipment", "%s의 장비를 현재 위치(%s)에 두시겠습니까, 아니면 아룰코를 떠나는 비행기를 타기 전 %s(%s)에 두게 하시겠습니까?"),
    ("str_iron_man_mode_warning", "철인 모드를 선택했습니다. 적이 점령한 구역에서는 게임을 저장할 수 없어 난이도가 크게 올라갑니다. 이 설정은 게임 전체에 영향을 줍니다. 철인 모드로 플레이하시겠습니까?"),
    ("str_left_equipment", "%s의 장비를 이제 %s(%s)에서 사용할 수 있습니다."),
    ("str_she_leaves_drops_equipment", "%s은(는) 곧 떠나며 장비를 %s에 두고 갑니다."),
    ("str_she_leaves_where_drop_equipment", "%s의 장비를 현재 위치(%s)에 두시겠습니까, 아니면 아룰코를 떠나는 비행기를 타기 전 %s(%s)에 두게 하시겠습니까?"),
    ("str_stat_agility", "민첩성"),
    ("str_stat_dexterity", "손재주"),
    ("str_stat_exp_level", "경험 레벨"),
    ("str_stat_explosive", "폭발물"),
    ("str_stat_health", "체력"),
    ("str_stat_leadership", "통솔력"),
    ("str_stat_marksmanship", "사격술"),
    ("str_stat_mechanical", "기계"),
    ("str_stat_medical", "의술"),
    ("str_stat_strength", "힘"),
    ("str_stat_wisdom", "지혜"),
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
    for key, korean in SCALARS:
        changed += check_and_set(data, key, None, korean)
        total += 1
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    print(f"Applied Korean UI batch 010: {changed}/{total} entries changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
