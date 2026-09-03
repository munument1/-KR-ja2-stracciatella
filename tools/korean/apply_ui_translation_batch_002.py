#!/usr/bin/env python3
"""Apply Korean UI translation batch 002.

Focus: tactical messages, dealer UI, turn labels, video hiring, weapon/money stats.
"""

from __future__ import annotations

import json
from apply_ui_translation_batch_001 import (
    PLACEHOLDER_RE,
    TARGET,
    get_value,
    set_value,
)

BATCH: list[tuple[str, int | None, str]] = [
    # Combat/status messages
    ("Message", 0, "%s이(가) 머리에 맞아 지혜가 1 감소했습니다!"),
    ("Message", 1, "%s이(가) 어깨에 맞아 민첩성이 1 감소했습니다!"),
    ("Message", 2, "%s이(가) 가슴에 맞아 힘이 1 감소했습니다!"),
    ("Message", 3, "%s이(가) 다리에 맞아 기민성이 1 감소했습니다!"),
    ("Message", 4, "%s은(는) 죽어가고 있으며 최대 체력이 영구적으로 1 감소했습니다!"),
    ("Message", 5, "%s이(가) 머리에 맞아 지혜가 %d 감소했습니다!"),
    ("Message", 6, "%s이(가) 어깨에 맞아 민첩성이 %d 감소했습니다!"),
    ("Message", 7, "%s이(가) 가슴에 맞아 힘이 %d 감소했습니다!"),
    ("Message", 8, "%s이(가) 다리에 맞아 기민성이 %d 감소했습니다!"),
    ("Message", 9, "인터럽트!"),
    ("Message", 10, "지원군이 도착했습니다!"),
    ("Message", 11, "%s이(가) 재장전합니다."),
    ("Message", 12, "%s의 행동력이 부족합니다!"),
    ("Message", 13, "신뢰성 높음"),
    ("Message", 14, "신뢰성 낮음"),
    ("Message", 15, "수리 쉬움"),
    ("Message", 16, "수리 어려움"),
    ("Message", 17, "높은 피해량"),
    ("Message", 18, "낮은 피해량"),
    ("Message", 19, "빠른 발사"),
    ("Message", 20, "느린 발사"),
    ("Message", 21, "긴 사거리"),
    ("Message", 22, "짧은 사거리"),
    ("Message", 23, "가벼움"),
    ("Message", 24, "무거움"),
    ("Message", 25, "작음"),
    ("Message", 26, "빠른 점사"),
    ("Message", 27, "점사 불가"),
    ("Message", 28, "대용량 탄창"),
    ("Message", 29, "소용량 탄창"),
    ("Message", 30, "%s의 위장 효과가 사라졌습니다."),
    ("Message", 31, "%s의 위장 효과가 씻겨 나갔습니다."),
    ("Message", 32, "두 번째 무기의 탄약이 없습니다!"),
    ("Message", 33, "%s이(가) %s을(를) 훔쳤습니다."),
    ("Message", 34, "%s의 무기는 점사가 불가능합니다."),
    ("Message", 35, "이미 같은 부착물이 장착되어 있습니다."),
    ("Message", 36, "아이템을 합치시겠습니까?"),
    ("Message", 37, "%s을(를) %s에 부착할 수 없습니다."),
    ("Message", 38, "없음"),
    ("Message", 39, "탄약 빼기"),
    ("Message", 40, "부착물"),
    ("Message", 41, "%s와(과) %s을(를) 동시에 사용할 수 없습니다."),
    ("Message", 42, "커서에 든 아이템은 네 개의 부착물 슬롯 중 하나에 놓아 특정 아이템에 부착할 수 있습니다."),
    ("Message", 43, "커서에 든 아이템은 네 개의 부착물 슬롯 중 하나에 놓아 특정 아이템에 부착할 수 있습니다. (하지만 이 경우에는 서로 호환되지 않습니다.)"),
    ("Message", 44, "이 구역의 적이 아직 모두 제거되지 않았습니다!"),
    ("Message", 45, "아직 %s에게 %s을(를) 줘야 합니다"),
    ("Message", 46, "%s이(가) 머리에 맞았습니다!"),
    ("Message", 47, "전투를 포기하시겠습니까?"),
    ("Message", 48, "이 부착은 영구적입니다. 계속하시겠습니까?"),
    ("Message", 49, "%s이(가) 더 활력을 느낍니다!"),
    ("Message", 50, "%s이(가) 구슬을 밟고 미끄러졌습니다!"),
    ("Message", 51, "%s이(가) %s을(를) 붙잡지 못했습니다!"),
    ("Message", 52, "%s이(가) %s을(를) 수리했습니다"),
    ("Message", 53, "인터럽트 대상 "),
    ("Message", 54, "항복하시겠습니까?"),
    ("Message", 55, "이 사람은 당신의 도움을 거부합니다."),
    ("Message", 56, "그럴 리 없지!"),
    ("Message", 57, "스카이라이더의 헬기를 이용하려면 먼저 용병의 임무를 차량/헬리콥터로 지정해야 합니다."),
    ("Message", 58, "%s은(는) 총 한 자루만 재장전할 시간이 있었습니다"),
    ("Message", 59, "블러드캣의 턴"),

    # Shopkeeper interface
    ("SKI_Text", 0, "보유 상품"),
    ("SKI_Text", 1, "페이지"),
    ("SKI_Text", 2, "총 비용"),
    ("SKI_Text", 3, "총 가치"),
    ("SKI_Text", 4, "감정"),
    ("SKI_Text", 5, "거래"),
    ("SKI_Text", 6, "완료"),
    ("SKI_Text", 7, "수리 비용"),
    ("SKI_Text", 8, "1시간"),
    ("SKI_Text", 9, "%d시간"),
    ("SKI_Text", 10, "수리 완료"),
    ("SKI_Text", 11, "제안 영역에 공간이 부족합니다."),
    ("SKI_Text", 12, "%d분"),
    ("SKI_Text", 13, "아이템을 바닥에 놓기"),
    ("SkiMessageBoxText", 0, "차액을 메우기 위해 주 계좌에서 %s을(를) 차감하시겠습니까?"),
    ("SkiMessageBoxText", 1, "자금이 부족합니다. %s이(가) 모자랍니다"),
    ("SkiMessageBoxText", 2, "비용을 지불하기 위해 주 계좌에서 %s을(를) 차감하시겠습니까?"),
    ("SkiMessageBoxText", 3, "상인에게 거래 시작 요청"),
    ("SkiMessageBoxText", 4, "상인에게 선택한 물품 수리 요청"),
    ("SkiMessageBoxText", 5, "대화 종료"),
    ("SkiMessageBoxText", 6, "현재 잔액"),

    # Tactical prompts before the hotkey-labelled controls
    ("TacticalStr", 0, "공습"),
    ("TacticalStr", 1, "응급처치를 자동으로 실시하시겠습니까?"),
    ("TacticalStr", 2, "%s이(가) 배송 물품이 사라진 것을 알아챘습니다."),
    ("TacticalStr", 3, "자물쇠가 %s 상태입니다."),
    ("TacticalStr", 4, "자물쇠가 없습니다."),
    ("TacticalStr", 5, "자물쇠에 함정이 없습니다."),
    ("TacticalStr", 6, "%s에게 맞는 열쇠가 없습니다."),
    ("TacticalStr", 7, "자물쇠에 함정이 없습니다."),
    ("TacticalStr", 8, "잠겼습니다."),
    ("TacticalStr", 9, "문"),
    ("TacticalStr", 10, "함정"),
    ("TacticalStr", 11, "잠김"),
    ("TacticalStr", 12, "잠금 해제"),
    ("TacticalStr", 13, "파손됨"),
    ("TacticalStr", 14, "여기에 스위치가 있습니다. 작동시키시겠습니까?"),
    ("TacticalStr", 15, "함정을 해제하시겠습니까?"),
    ("TacticalStr", 16, "더 보기..."),
    ("TacticalStr", 17, "%s이(가) 바닥에 놓였습니다."),
    ("TacticalStr", 18, "%s이(가) %s에게 전달되었습니다."),
    ("TacticalStr", 19, "%s에게 전액 지급했습니다."),
    ("TacticalStr", 20, "%s에게 아직 %d을(를) 지급해야 합니다."),
    ("TacticalStr", 21, "폭발 주파수 선택:"),
    ("TacticalStr", 22, "폭발까지 남은 턴 수:"),
    ("TacticalStr", 23, "원격 기폭기 주파수 설정:"),
    ("TacticalStr", 24, "부비트랩을 해제하시겠습니까?"),
    ("TacticalStr", 25, "파란 깃발을 제거하시겠습니까?"),
    ("TacticalStr", 26, "여기에 파란 깃발을 설치하시겠습니까?"),
    ("TacticalStr", 27, "턴 종료 중"),
    ("TacticalStr", 28, "정말 %s을(를) 공격하시겠습니까?"),
    ("TacticalStr", 29, "차량은 자세를 바꿀 수 없습니다."),
    ("TacticalStr", 30, "로봇은 자세를 바꿀 수 없습니다."),
    ("TacticalStr", 31, "%s은(는) 여기서 그 자세로 바꿀 수 없습니다."),
    ("TacticalStr", 32, "%s은(는) 여기서 응급처치를 받을 수 없습니다."),
    ("TacticalStr", 33, "%s은(는) 응급처치가 필요하지 않습니다."),
    ("TacticalStr", 34, "그곳으로 이동할 수 없습니다."),
    ("TacticalStr", 35, "팀이 가득 찼습니다. 새 인원을 받을 자리가 없습니다."),
    ("TacticalStr", 36, "%s이(가) 합류했습니다."),
    ("TacticalStr", 37, "%s에게 $%d을(를) 지급해야 합니다."),
    ("TacticalStr", 38, "%s을(를) 호위하시겠습니까?"),
    ("TacticalStr", 39, "%s을(를) 하루 %s에 고용하시겠습니까?"),
    ("TacticalStr", 40, "싸우시겠습니까?"),
    ("TacticalStr", 41, "%s을(를) %s에 구입하시겠습니까?"),
    ("TacticalStr", 42, "%s은(는) %d분대에서 호위 중입니다."),
    ("TacticalStr", 43, "걸림"),
    ("TacticalStr", 44, "로봇에는 %s 구경 탄약이 필요합니다."),
    ("TacticalStr", 45, "그곳으로 던질 수 없습니다."),

    # Turn labels and hiring/video UI
    ("TeamTurnString", 0, "플레이어 턴"),
    ("TeamTurnString", 1, "적 턴"),
    ("TeamTurnString", 2, "괴물 턴"),
    ("TeamTurnString", 3, "민병대 턴"),
    ("TeamTurnString", 4, "민간인 턴"),
    ("VideoConfercingText", 0, "계약 비용:"),
    ("VideoConfercingText", 1, "1일"),
    ("VideoConfercingText", 2, "1주"),
    ("VideoConfercingText", 3, "2주"),
    ("VideoConfercingText", 4, "장비 없음"),
    ("VideoConfercingText", 5, "장비 구매"),
    ("VideoConfercingText", 6, "자금 이체"),
    ("VideoConfercingText", 7, "취소"),
    ("VideoConfercingText", 8, "고용"),
    ("VideoConfercingText", 9, "통화 종료"),
    ("VideoConfercingText", 10, "확인"),
    ("VideoConfercingText", 11, "메시지 남기기"),
    ("VideoConfercingText", 12, "화상 회의 상대"),
    ("VideoConfercingText", 13, "연결 중. . ."),
    ("VideoConfercingText", 14, "의료 보증금 포함"),

    # Item/weapon/money panel labels
    ("WeaponType", 0, "기타"),
    ("WeaponType", 1, "권총"),
    ("WeaponType", 2, "기관권총"),
    ("WeaponType", 3, "기관단총"),
    ("WeaponType", 4, "소총"),
    ("WeaponType", 5, "저격소총"),
    ("WeaponType", 6, "돌격소총"),
    ("WeaponType", 7, "경기관총"),
    ("WeaponType", 8, "산탄총"),
    ("gMoneyStatsDesc", 0, "금액"),
    ("gMoneyStatsDesc", 1, "남은 금액:"),
    ("gMoneyStatsDesc", 2, "금액"),
    ("gMoneyStatsDesc", 3, "나눌 금액:"),
    ("gMoneyStatsDesc", 4, "현재"),
    ("gMoneyStatsDesc", 5, "잔액"),
    ("gMoneyStatsDesc", 6, "인출"),
    ("gMoneyStatsDesc", 7, "금액"),
    ("gWeaponStatsDesc", 0, "중량 (%s):"),
    ("gWeaponStatsDesc", 1, "상태:"),
    ("gWeaponStatsDesc", 2, "수량:"),
    ("gWeaponStatsDesc", 3, "사거리:"),
    ("gWeaponStatsDesc", 4, "피해:"),
    ("gWeaponStatsDesc", 5, "행동력:"),
    ("gWeaponStatsDesc", 6, "="),
    ("gpGameClockString", None, "일"),
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
    print(f"Applied Korean UI batch 002: {changed}/{len(BATCH)} entries changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
