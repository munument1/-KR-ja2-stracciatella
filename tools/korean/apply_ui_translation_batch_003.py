#!/usr/bin/env python3
"""Apply Korean UI translation batch 003.

Focus: remaining tactical interface/status strings and pre-battle strategic UI.
ASCII keyboard shortcuts are kept explicitly in parentheses so translating the
visible label does not silently change the game's keyboard contract.
"""

from __future__ import annotations

import json
from apply_ui_translation_batch_001 import PLACEHOLDER_RE, TARGET, get_value, set_value

BATCH: list[tuple[str, int | None, str]] = [
    # TacticalStr[46..136]
    ("TacticalStr", 46, "은신 모드 (|Z)"),
    ("TacticalStr", 47, "지도 화면 (|M)"),
    ("TacticalStr", 48, "완료/턴 종료 (|D)"),
    ("TacticalStr", 49, "대화"),
    ("TacticalStr", 50, "음소거"),
    ("TacticalStr", 51, "자세 올리기 (|P|g|U|p)"),
    ("TacticalStr", 52, "커서 높이 (|T|a|b)"),
    ("TacticalStr", 53, "오르기 / 뛰어넘기"),
    ("TacticalStr", 54, "자세 낮추기 (|P|g|D|n)"),
    ("TacticalStr", 55, "조사 (|C|t|r|l)"),
    ("TacticalStr", 56, "이전 용병"),
    ("TacticalStr", 57, "다음 용병 (|S|p|a|c|e)"),
    ("TacticalStr", 58, "옵션 (|O)"),
    ("TacticalStr", 59, "점사 모드 (|B)"),
    ("TacticalStr", 60, "보기/회전 (|L)"),
    ("TacticalStr", 61, "체력: %d/%d\n기력: %d/%d\n사기: %s"),
    ("TacticalStr", 62, "응?"),
    ("TacticalStr", 63, "계속"),
    ("TacticalStr", 64, "%s의 음소거를 해제했습니다."),
    ("TacticalStr", 65, "%s을(를) 음소거했습니다."),
    ("TacticalStr", 66, "체력: %d/%d\n연료: %d/%d"),
    ("TacticalStr", 67, "차량에서 내리기"),
    ("TacticalStr", 68, "분대 변경 ( |S|h|i|f|t |S|p|a|c|e )"),
    ("TacticalStr", 69, "운전"),
    ("TacticalStr", 70, "해당 없음"),
    ("TacticalStr", 71, "사용 (맨손 전투)"),
    ("TacticalStr", 72, "사용 (총기)"),
    ("TacticalStr", 73, "사용 (도검)"),
    ("TacticalStr", 74, "사용 (폭발물)"),
    ("TacticalStr", 75, "사용 (구급상자)"),
    ("TacticalStr", 76, "(잡기)"),
    ("TacticalStr", 77, "(재장전)"),
    ("TacticalStr", 78, "(건네기)"),
    ("TacticalStr", 79, "%s이(가) 작동했습니다."),
    ("TacticalStr", 80, "%s이(가) 도착했습니다."),
    ("TacticalStr", 81, "%s의 행동력이 바닥났습니다."),
    ("TacticalStr", 82, "%s은(는) 사용할 수 없습니다."),
    ("TacticalStr", 83, "%s의 응급처치가 모두 끝났습니다."),
    ("TacticalStr", 84, "%s에게 붕대가 없습니다."),
    ("TacticalStr", 85, "구역에 적이 있습니다!"),
    ("TacticalStr", 86, "시야에 적이 없습니다."),
    ("TacticalStr", 87, "행동력이 부족합니다."),
    ("TacticalStr", 88, "아무도 원격 조종기를 사용하고 있지 않습니다."),
    ("TacticalStr", 89, "점사로 탄창을 모두 비웠습니다!"),
    ("TacticalStr", 90, "병사"),
    ("TacticalStr", 91, "크레피투스"),
    ("TacticalStr", 92, "민병대"),
    ("TacticalStr", 93, "민간인"),
    ("TacticalStr", 94, "구역 이탈 중"),
    ("TacticalStr", 95, "확인"),
    ("TacticalStr", 96, "취소"),
    ("TacticalStr", 97, "선택한 용병"),
    ("TacticalStr", 98, "분대의 모든 용병"),
    ("TacticalStr", 99, "구역으로 이동"),
    ("TacticalStr", 100, "지도 화면으로 이동"),
    ("TacticalStr", 101, "이쪽 방향으로는 구역을 벗어날 수 없습니다."),
    ("TacticalStr", 102, "%s은(는) 너무 멀리 있습니다."),
    ("TacticalStr", 103, "나무 꼭대기 숨기기"),
    ("TacticalStr", 104, "나무 꼭대기 표시"),
    ("TacticalStr", 105, "까마귀"),
    ("TacticalStr", 106, "목"),
    ("TacticalStr", 107, "머리"),
    ("TacticalStr", 108, "몸통"),
    ("TacticalStr", 109, "다리"),
    ("TacticalStr", 110, "여왕이 원하는 정보를 말하시겠습니까?"),
    ("TacticalStr", 111, "지문 ID를 획득했습니다"),
    ("TacticalStr", 112, "잘못된 지문 ID입니다. 무기가 작동하지 않습니다"),
    ("TacticalStr", 113, "표적을 포착했습니다"),
    ("TacticalStr", 114, "경로가 막혔습니다"),
    ("TacticalStr", 115, "돈 입금/인출"),
    ("TacticalStr", 116, "응급처치가 필요한 사람이 없습니다."),
    ("TacticalStr", 117, "총기 걸림."),
    ("TacticalStr", 118, "그곳으로 갈 수 없습니다."),
    ("TacticalStr", 119, "이 사람은 이동을 거부합니다."),
    ("TacticalStr", 120, "%s을(를) 지불하는 데 동의하시겠습니까?"),
    ("TacticalStr", 121, "무료 치료를 받으시겠습니까?"),
    ("TacticalStr", 122, "대릴과 결혼하는 데 동의하시겠습니까?"),
    ("TacticalStr", 123, "열쇠고리 패널"),
    ("TacticalStr", 124, "EPC로는 그렇게 할 수 없습니다."),
    ("TacticalStr", 125, "크롯을 살려 두시겠습니까?"),
    ("TacticalStr", 126, "무기의 유효 사거리 밖입니다."),
    ("TacticalStr", 127, "광부"),
    ("TacticalStr", 128, "차량은 구역 사이로만 이동할 수 있습니다"),
    ("TacticalStr", 129, "지금은 자동 응급처치를 할 수 없습니다"),
    ("TacticalStr", 130, "%s의 경로가 막혔습니다"),
    ("TacticalStr", 131, "데이드라나의 군대에 붙잡힌 용병들이 이곳에 갇혀 있습니다!"),
    ("TacticalStr", 132, "자물쇠에 명중"),
    ("TacticalStr", 133, "자물쇠 파괴"),
    ("TacticalStr", 134, "다른 사람이 이 문을 사용하려 하고 있습니다."),
    ("TacticalStr", 135, "체력: %d/%d\n연료: %d/%d"),
    ("TacticalStr", 136, "%s은(는) %s을(를) 볼 수 없습니다."),

    # gpStrategicString[0..68]
    ("gpStrategicString", 0, "%s이(가) %s 구역에서 탐지되었으며 다른 분대 하나가 곧 도착합니다."),
    ("gpStrategicString", 1, "%s이(가) %s 구역에서 탐지되었으며 다른 분대들이 곧 도착합니다."),
    ("gpStrategicString", 2, "동시에 도착하도록 시간을 맞추시겠습니까?"),
    ("gpStrategicString", 3, "적이 항복할 기회를 제안합니다."),
    ("gpStrategicString", 4, "적이 남아 있던 의식 불명의 용병들을 포로로 잡았습니다."),
    ("gpStrategicString", 5, "후퇴"),
    ("gpStrategicString", 6, "완료"),
    ("gpStrategicString", 7, "방어 중"),
    ("gpStrategicString", 8, "공격 중"),
    ("gpStrategicString", 9, "조우"),
    ("gpStrategicString", 10, "구역"),
    ("gpStrategicString", 11, "승리!"),
    ("gpStrategicString", 12, "패배!"),
    ("gpStrategicString", 13, "항복함!"),
    ("gpStrategicString", 14, "포로가 됨!"),
    ("gpStrategicString", 15, "후퇴함!"),
    ("gpStrategicString", 16, "민병대"),
    ("gpStrategicString", 17, "정예병"),
    ("gpStrategicString", 18, "일반병"),
    ("gpStrategicString", 19, "관리병"),
    ("gpStrategicString", 20, "괴물"),
    ("gpStrategicString", 21, "경과 시간"),
    ("gpStrategicString", 22, "후퇴 완료"),
    ("gpStrategicString", 23, "후퇴 중"),
    ("gpStrategicString", 24, "후퇴"),
    ("gpStrategicString", 25, "자동 전투"),
    ("gpStrategicString", 26, "구역으로 이동"),
    ("gpStrategicString", 27, "용병 후퇴"),
    ("gpStrategicString", 28, "적과 조우"),
    ("gpStrategicString", 29, "적의 침공"),
    ("gpStrategicString", 30, "적의 매복"),
    ("gpStrategicString", 31, "적 구역 진입"),
    ("gpStrategicString", 32, "괴물의 공격"),
    ("gpStrategicString", 33, "블러드캣의 매복"),
    ("gpStrategicString", 34, "블러드캣 소굴 진입"),
    ("gpStrategicString", 35, "위치"),
    ("gpStrategicString", 36, "적"),
    ("gpStrategicString", 37, "용병"),
    ("gpStrategicString", 38, "민병대"),
    ("gpStrategicString", 39, "괴물"),
    ("gpStrategicString", 40, "블러드캣"),
    ("gpStrategicString", 41, "구역"),
    ("gpStrategicString", 42, "없음"),
    ("gpStrategicString", 43, "해당 없음"),
    ("gpStrategicString", 44, "일"),
    ("gpStrategicString", 45, "시간"),
    ("gpStrategicString", 46, "초기화"),
    ("gpStrategicString", 47, "분산"),
    ("gpStrategicString", 48, "집결"),
    ("gpStrategicString", 49, "완료"),
    ("gpStrategicString", 50, "용병 배치를 모두 초기화하고\n직접 다시 배치할 수 있습니다. (|C)"),
    ("gpStrategicString", 51, "누를 때마다 용병들을 무작위로\n분산 배치합니다. (|S)"),
    ("gpStrategicString", 52, "용병들을 집결시킬 위치를\n선택할 수 있습니다. (|G)"),
    ("gpStrategicString", 53, "용병 배치를 마쳤으면 이 버튼을\n누르십시오. (|E|n|t|e|r)"),
    ("gpStrategicString", 54, "전투를 시작하기 전에 모든 용병을\n배치해야 합니다."),
    ("gpStrategicString", 55, "구역"),
    ("gpStrategicString", 56, "진입 위치 선택"),
    ("gpStrategicString", 57, "그곳은 진입할 수 없는 위치입니다. 다른 곳을 선택하십시오."),
    ("gpStrategicString", 58, "지도에서 강조 표시된 영역에 용병을 배치하십시오."),
    ("gpStrategicString", 59, "지도를 불러오지 않고 전투를\n자동으로 해결합니다. (|A)"),
    ("gpStrategicString", 60, "플레이어가 공격 중일 때는\n자동 전투를 사용할 수 없습니다."),
    ("gpStrategicString", 61, "구역에 진입해 적과 교전합니다. (|E)"),
    ("gpStrategicString", 62, "분대를 이전 구역으로 후퇴시킵니다. (|R)"),
    ("gpStrategicString", 63, "모든 분대를 이전 구역으로 후퇴시킵니다. (|R)"),
    ("gpStrategicString", 64, "적이 %s 구역의 민병대를 공격합니다."),
    ("gpStrategicString", 65, "괴물이 %s 구역의 민병대를 공격합니다."),
    ("gpStrategicString", 66, "괴물이 %s 구역을 공격해 민간인 %d명을 죽였습니다."),
    ("gpStrategicString", 67, "적이 %s 구역의 용병들을 공격합니다. 싸울 수 있는 용병이 한 명도 없습니다!"),
    ("gpStrategicString", 68, "괴물이 %s 구역의 용병들을 공격합니다. 싸울 수 있는 용병이 한 명도 없습니다!"),
]


def main() -> int:
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    changed = 0
    for key, index, korean in BATCH:
        current = get_value(data, key, index)
        if PLACEHOLDER_RE.findall(current) != PLACEHOLDER_RE.findall(korean):
            where = key if index is None else f"{key}[{index}]"
            raise SystemExit(
                f"Placeholder mismatch at {where}: "
                f"{PLACEHOLDER_RE.findall(current)} != {PLACEHOLDER_RE.findall(korean)}"
            )
        if current != korean:
            set_value(data, key, index, korean)
            changed += 1
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    print(f"Applied Korean UI batch 003: {changed}/{len(BATCH)} entries changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
