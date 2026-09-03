#!/usr/bin/env python3
"""Apply Korean UI translation batch 003.

Focus: remaining tactical interface/status strings and pre-battle strategic UI.
ASCII keyboard shortcuts are kept explicitly in parentheses so translating the
visible label does not silently change the game's keyboard contract.
"""

from __future__ import annotations

import json
from apply_ui_translation_batch_001 import PLACEHOLDER_RE, TARGET, get_value, set_value

TACTICAL = [
    "은신 모드 (|Z)",
    "지도 화면 (|M)",
    "완료/턴 종료 (|D)",
    "대화",
    "음소거",
    "자세 올리기 (|P|g|U|p)",
    "커서 높이 (|T|a|b)",
    "오르기 / 뛰어넘기",
    "자세 낮추기 (|P|g|D|n)",
    "조사 (|C|t|r|l)",
    "이전 용병",
    "다음 용병 (|S|p|a|c|e)",
    "옵션 (|O)",
    "점사 모드 (|B)",
    "보기/회전 (|L)",
    "체력: %d/%d\n기력: %d/%d\n사기: %s",
    "응?",
    "계속",
    "%s의 음소거를 해제했습니다.",
    "%s을(를) 음소거했습니다.",
    "체력: %d/%d\n연료: %d/%d",
    "차량에서 내리기",
    "분대 변경 ( |S|h|i|f|t |S|p|a|c|e )",
    "운전",
    "해당 없음",
    "사용 (맨손 전투)",
    "사용 (총기)",
    "사용 (도검)",
    "사용 (폭발물)",
    "사용 (구급상자)",
    "(잡기)",
    "(재장전)",
    "(건네기)",
    "%s이(가) 작동했습니다.",
    "%s이(가) 도착했습니다.",
    "%s의 행동력이 바닥났습니다.",
    "%s은(는) 사용할 수 없습니다.",
    "%s의 응급처치가 모두 끝났습니다.",
    "%s에게 붕대가 없습니다.",
    "구역에 적이 있습니다!",
    "시야에 적이 없습니다.",
    "행동력이 부족합니다.",
    "아무도 원격 조종기를 사용하고 있지 않습니다.",
    "점사로 탄창을 모두 비웠습니다!",
    "병사",
    "크레피투스",
    "민병대",
    "민간인",
    "구역 이탈 중",
    "확인",
    "취소",
    "선택한 용병",
    "분대의 모든 용병",
    "구역으로 이동",
    "지도 화면으로 이동",
    "이쪽 방향으로는 구역을 벗어날 수 없습니다.",
    "%s은(는) 너무 멀리 있습니다.",
    "나무 꼭대기 숨기기",
    "나무 꼭대기 표시",
    "까마귀",
    "목",
    "머리",
    "몸통",
    "다리",
    "여왕이 원하는 정보를 말하시겠습니까?",
    "지문 ID를 획득했습니다",
    "잘못된 지문 ID입니다. 무기가 작동하지 않습니다",
    "표적을 포착했습니다",
    "경로가 막혔습니다",
    "돈 입금/인출",
    "응급처치가 필요한 사람이 없습니다.",
    "총기 걸림.",
    "그곳으로 갈 수 없습니다.",
    "이 사람은 이동을 거부합니다.",
    "%s을(를) 지불하는 데 동의하시겠습니까?",
    "무료 치료를 받으시겠습니까?",
    "대릴과 결혼하는 데 동의하시겠습니까?",
    "열쇠고리 패널",
    "EPC로는 그렇게 할 수 없습니다.",
    "크롯을 살려 두시겠습니까?",
    "무기의 유효 사거리 밖입니다.",
    "광부",
    "차량은 구역 사이로만 이동할 수 있습니다",
    "지금은 자동 응급처치를 할 수 없습니다",
    "%s의 경로가 막혔습니다",
    "데이드라나의 군대에 붙잡힌 용병들이 이곳에 갇혀 있습니다!",
    "자물쇠에 명중",
    "자물쇠 파괴",
    "다른 사람이 이 문을 사용하려 하고 있습니다.",
    "체력: %d/%d\n연료: %d/%d",
    "%s은(는) %s을(를) 볼 수 없습니다.",
]

STRATEGIC = [
    "%s이(가) %s 구역에서 탐지되었으며 다른 분대 하나가 곧 도착합니다.",
    "%s이(가) %s 구역에서 탐지되었으며 다른 분대들이 곧 도착합니다.",
    "동시에 도착하도록 시간을 맞추시겠습니까?",
    "적이 항복할 기회를 제안합니다.",
    "적이 남아 있던 의식 불명의 용병들을 포로로 잡았습니다.",
    "후퇴",
    "완료",
    "방어 중",
    "공격 중",
    "조우",
    "구역",
    "승리!",
    "패배!",
    "항복함!",
    "포로가 됨!",
    "후퇴함!",
    "민병대",
    "정예병",
    "일반병",
    "관리병",
    "괴물",
    "경과 시간",
    "후퇴 완료",
    "후퇴 중",
    "후퇴",
    "자동 전투",
    "구역으로 이동",
    "용병 후퇴",
    "적과 조우",
    "적의 침공",
    "적의 매복",
    "적 구역 진입",
    "괴물의 공격",
    "블러드캣의 매복",
    "블러드캣 소굴 진입",
    "위치",
    "적",
    "용병",
    "민병대",
    "괴물",
    "블러드캣",
    "구역",
    "없음",
    "해당 없음",
    "일",
    "시간",
    "초기화",
    "분산",
    "집결",
    "완료",
    "용병 배치를 모두 초기화하고\n직접 다시 배치할 수 있습니다. (|C)",
    "누를 때마다 용병들을 무작위로\n분산 배치합니다. (|S)",
    "용병들을 집결시킬 위치를\n선택할 수 있습니다. (|G)",
    "용병 배치를 마쳤으면 이 버튼을\n누르십시오. (|E|n|t|e|r)",
    "전투를 시작하기 전에 모든 용병을\n배치해야 합니다.",
    "구역",
    "진입 위치 선택",
    "그곳은 진입할 수 없는 위치입니다. 다른 곳을 선택하십시오.",
    "지도에서 강조 표시된 영역에 용병을 배치하십시오.",
    "지도를 불러오지 않고 전투를\n자동으로 해결합니다. (|A)",
    "플레이어가 공격 중일 때는\n자동 전투를 사용할 수 없습니다.",
    "구역에 진입해 적과 교전합니다. (|E)",
    "분대를 이전 구역으로 후퇴시킵니다. (|R)",
    "모든 분대를 이전 구역으로 후퇴시킵니다. (|R)",
    "적이 %s 구역의 민병대를 공격합니다.",
    "괴물이 %s 구역의 민병대를 공격합니다.",
    "괴물의 공격으로 민간인 %d명이 사망했습니다. 위치는 %s 구역입니다.",
    "적이 %s 구역의 용병들을 공격합니다. 싸울 수 있는 용병이 한 명도 없습니다!",
    "괴물이 %s 구역의 용병들을 공격합니다. 싸울 수 있는 용병이 한 명도 없습니다!",
]

assert len(TACTICAL) == 91
assert len(STRATEGIC) == 69


def apply_range(data: dict, key: str, start: int, translations: list[str]) -> int:
    changed = 0
    for offset, korean in enumerate(translations):
        index = start + offset
        current = get_value(data, key, index)
        if PLACEHOLDER_RE.findall(current) != PLACEHOLDER_RE.findall(korean):
            raise SystemExit(
                f"Placeholder mismatch at {key}[{index}]: "
                f"{PLACEHOLDER_RE.findall(current)} != {PLACEHOLDER_RE.findall(korean)}"
            )
        if current != korean:
            set_value(data, key, index, korean)
            changed += 1
    return changed


def main() -> int:
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    changed = apply_range(data, "TacticalStr", 46, TACTICAL)
    changed += apply_range(data, "gpStrategicString", 0, STRATEGIC)
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    print(f"Applied Korean UI batch 003: {changed}/{len(TACTICAL) + len(STRATEGIC)} entries changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
