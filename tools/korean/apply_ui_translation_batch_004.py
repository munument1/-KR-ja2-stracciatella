#!/usr/bin/env python3
"""Apply Korean UI translation batch 004.

Focus: game settings, IMP traits, laptop help, late tactical/strategic messages,
pre-battle interface, assignment menu and common compact labels.
"""

from __future__ import annotations

import json
from apply_ui_translation_batch_001 import PLACEHOLDER_RE, TARGET, get_value, set_value

BATCH: list[tuple[str, int | None, str]] = [
    ("gsAtmStartButtonText", 0, "능력치"),
    ("gsAtmStartButtonText", 1, "인벤토리"),
    ("gsAtmStartButtonText", 2, "고용 정보"),
    ("gsLoyalString", None, "충성도 %d%%"),
    ("gsTimeStrings", 0, "시"),
    ("gsTimeStrings", 1, "분"),
    ("gsTimeStrings", 2, "초"),
    ("gsTimeStrings", 3, "일"),
    ("gsUndergroundString", None, "지하에서는 이동 명령을 내릴 수 없습니다."),
    ("gs_dead_is_dead_mode_tab_name", 0, "일반"),
    ("gs_dead_is_dead_mode_tab_name", 1, "영구 사망"),
    ("gzBobbyRShipmentText", 0, "최근 배송"),
    ("gzBobbyRShipmentText", 1, "주문 번호"),
    ("gzBobbyRShipmentText", 2, "품목 수"),
    ("gzBobbyRShipmentText", 3, "주문일"),
    ("gzConsLabel", None, "단점:"),

    # Initial game options
    ("gzGIOScreenText", 0, "초기 게임 설정"),
    ("gzGIOScreenText", 1, "게임 스타일"),
    ("gzGIOScreenText", 2, "현실적"),
    ("gzGIOScreenText", 3, "SF"),
    ("gzGIOScreenText", 4, "총기 옵션"),
    ("gzGIOScreenText", 5, "다양한 총기"),
    ("gzGIOScreenText", 6, "일반"),
    ("gzGIOScreenText", 7, "난이도"),
    ("gzGIOScreenText", 8, "초보"),
    ("gzGIOScreenText", 9, "숙련"),
    ("gzGIOScreenText", 10, "전문가"),
    ("gzGIOScreenText", 11, "확인"),
    ("gzGIOScreenText", 12, "취소"),
    ("gzGIOScreenText", 13, "추가 난이도 설정"),
    ("gzGIOScreenText", 14, "언제든 저장"),
    ("gzGIOScreenText", 15, "철인 모드"),
    ("gzGIOScreenText", 16, "영구 사망"),
    ("gzHelpScreenText", None, "도움말 화면 닫기"),

    # IMP traits
    ("gzIMPSkillTraitsText", 0, "자물쇠 따기"),
    ("gzIMPSkillTraitsText", 1, "맨손 전투"),
    ("gzIMPSkillTraitsText", 2, "전자공학"),
    ("gzIMPSkillTraitsText", 3, "야간 작전"),
    ("gzIMPSkillTraitsText", 4, "투척"),
    ("gzIMPSkillTraitsText", 5, "교육"),
    ("gzIMPSkillTraitsText", 6, "중화기"),
    ("gzIMPSkillTraitsText", 7, "자동화기"),
    ("gzIMPSkillTraitsText", 8, "은신"),
    ("gzIMPSkillTraitsText", 9, "양손잡이"),
    ("gzIMPSkillTraitsText", 10, "칼 사용"),
    ("gzIMPSkillTraitsText", 11, "옥상 저격"),
    ("gzIMPSkillTraitsText", 12, "위장"),
    ("gzIMPSkillTraitsText", 13, "무술"),
    ("gzIMPSkillTraitsText", 14, "없음"),
    ("gzIMPSkillTraitsText", 15, "I.M.P. 특기"),
    ("gzIntroScreen", None, "인트로 영상을 찾을 수 없습니다"),

    # Laptop help
    ("gzLaptopHelpText", 0, "이메일 보기"),
    ("gzLaptopHelpText", 1, "여러 웹사이트 둘러보기"),
    ("gzLaptopHelpText", 2, "파일과 이메일 첨부 파일 보기"),
    ("gzLaptopHelpText", 3, "사건 기록 보기"),
    ("gzLaptopHelpText", 4, "팀 정보 보기"),
    ("gzLaptopHelpText", 5, "재정 요약 및 내역 보기"),
    ("gzLaptopHelpText", 6, "노트북 닫기"),
    ("gzLaptopHelpText", 7, "새 메일이 있습니다"),
    ("gzLaptopHelpText", 8, "새 파일이 있습니다"),
    ("gzLaptopHelpText", 9, "국제 용병 협회 A.I.M."),
    ("gzLaptopHelpText", 10, "Bobby Ray 온라인 무기 통신판매"),
    ("gzLaptopHelpText", 11, "용병 프로파일링 연구소 I.M.P."),
    ("gzLaptopHelpText", 12, "저비용 용병 모집 센터 M.E.R.C."),
    ("gzLaptopHelpText", 13, "맥길리커티 장례식장"),
    ("gzLaptopHelpText", 14, "유나이티드 플로럴 서비스"),
    ("gzLaptopHelpText", 15, "A.I.M. 계약 보험 중개사"),

    # Late localized runtime messages
    ("gzLateLocalizedString", 0, "아무도 조종기를 사용하지 않으면 로봇은 이 구역을 벗어날 수 없습니다."),
    ("gzLateLocalizedString", 1, "지금은 시간을 빠르게 돌릴 수 없습니다. 불꽃놀이가 끝날 때까지 기다리십시오!"),
    ("gzLateLocalizedString", 2, "%s은(는) 이동을 거부합니다."),
    ("gzLateLocalizedString", 3, "%s은(는) 자세를 바꿀 기력이 부족합니다."),
    ("gzLateLocalizedString", 4, "{}의 연료가 바닥나 {}에 멈춰 섰습니다."),
    ("gzLateLocalizedString", 5, "위"),
    ("gzLateLocalizedString", 6, "아래"),
    ("gzLateLocalizedString", 7, "의료 능력을 가진 용병이 없습니다."),
    ("gzLateLocalizedString", 8, "응급처치에 필요한 의료 물자가 없습니다."),
    ("gzLateLocalizedString", 9, "모두를 응급처치하기에는 의료 물자가 부족했습니다."),
    ("gzLateLocalizedString", 10, "응급처치가 필요한 용병이 없습니다."),
    ("gzLateLocalizedString", 11, "용병들을 자동으로 응급처치합니다."),
    ("gzLateLocalizedString", 12, "모든 용병의 응급처치가 끝났습니다."),
    ("gzLateLocalizedString", 13, "아룰코"),
    ("gzLateLocalizedString", 14, "(옥상)"),
    ("gzLateLocalizedString", 15, "체력: %d/%d"),
    ("gzLateLocalizedString", 16, "%d 대 %d"),
    ("gzLateLocalizedString", 17, "%s이(가) 가득 찼습니다!"),
    ("gzLateLocalizedString", 18, "%s은(는) 즉각적인 응급처치나 붕대 처치는 필요하지 않지만 더 전문적인 치료 및/또는 휴식이 필요합니다."),
    ("gzLateLocalizedString", 19, "%s이(가) 다리에 맞아 쓰러졌습니다!"),
    ("gzLateLocalizedString", 20, "%s은(는) 지금 말할 수 없습니다."),
    ("gzLateLocalizedString", 21, "신병 민병대 %d명이 정예 민병대로 승급했습니다."),
    ("gzLateLocalizedString", 22, "신병 민병대 %d명이 일반 민병대로 승급했습니다."),
    ("gzLateLocalizedString", 23, "일반 민병대 %d명이 정예 민병대로 승급했습니다."),
    ("gzLateLocalizedString", 24, "스위치"),
    ("gzLateLocalizedString", 25, "%s이(가) 광폭해졌습니다!"),
    ("gzLateLocalizedString", 26, "%s 구역에 용병이 있어 지금은 시간 압축이 안전하지 않습니다."),
    ("gzLateLocalizedString", 27, "용병이 괴물에게 점령된 광산에 있을 때는 시간 압축이 안전하지 않습니다."),
    ("gzLateLocalizedString", 28, "신병 민병대 1명이 정예 민병대로 승급했습니다."),
    ("gzLateLocalizedString", 29, "신병 민병대 1명이 일반 민병대로 승급했습니다."),
    ("gzLateLocalizedString", 30, "일반 민병대 1명이 정예 민병대로 승급했습니다."),
    ("gzLateLocalizedString", 31, "%s은(는) 아무 말도 하지 않습니다."),
    ("gzLateLocalizedString", 32, "지상으로 이동하시겠습니까?"),
    ("gzLateLocalizedString", 33, "(%d분대)"),
    ("gzLateLocalizedString", 34, "%s이(가) %s의 %s을(를) 수리했습니다"),
    ("gzLateLocalizedString", 35, "블러드캣"),
    ("gzLateLocalizedString", 36, "%s이(가) 발이 걸려 넘어졌습니다"),
    ("gzLateLocalizedString", 37, "이 위치에서는 이 아이템을 주울 수 없습니다."),
    ("gzLateLocalizedString", 38, "남아 있는 용병 중 싸울 수 있는 사람이 없습니다. 민병대가 괴물과 단독으로 싸웁니다."),
    ("gzLateLocalizedString", 39, "%s의 의료 키트가 바닥났습니다!"),
    ("gzLateLocalizedString", 40, "%s은(는) 다른 사람을 치료할 능력이 부족합니다!"),
    ("gzLateLocalizedString", 41, "%s의 공구 키트가 바닥났습니다!"),
    ("gzLateLocalizedString", 42, "%s은(는) 물건을 수리할 능력이 부족합니다!"),
    ("gzLateLocalizedString", 43, "수리 시간"),
    ("gzLateLocalizedString", 44, "%s은(는) 이 사람을 볼 수 없습니다."),
    ("gzLateLocalizedString", 45, "%s의 총열 연장 장치가 떨어졌습니다!"),
    ("gzLateLocalizedString", 46, "한 구역에는 민병대 교관을 %d명까지만 배치할 수 있습니다."),
    ("gzLateLocalizedString", 47, "정말 진행하시겠습니까?"),
    ("gzLateLocalizedString", 48, "시간 압축"),
    ("gzLateLocalizedString", 49, "차량의 연료 탱크가 가득 찼습니다."),
    ("gzLateLocalizedString", 50, "시간 압축 계속 (|S|p|a|c|e)"),
    ("gzLateLocalizedString", 51, "시간 압축 중지 (|E|s|c)"),
    ("gzLateLocalizedString", 52, "%s이(가) %s의 총기 걸림을 해결했습니다"),
    ("gzLateLocalizedString", 53, "%s이(가) %s의 %s 걸림을 해결했습니다"),
    ("gzLateLocalizedString", 54, "구역 인벤토리를 보는 동안에는 시간 압축을 사용할 수 없습니다."),
    ("gzLateLocalizedString", 55, "현재/최대 진행도: %d%%/%d%%"),
    ("gzLateLocalizedString", 56, "존과 메리를 호위하시겠습니까?"),
    ("gzLateLocalizedString", 57, "스위치가 작동했습니다."),

    # Merc skill labels
    ("gzMercSkillText", 0, "특기 없음"),
    ("gzMercSkillText", 1, "자물쇠 따기"),
    ("gzMercSkillText", 2, "맨손 전투"),
    ("gzMercSkillText", 3, "전자공학"),
    ("gzMercSkillText", 4, "야간 작전"),
    ("gzMercSkillText", 5, "투척"),
    ("gzMercSkillText", 6, "교육"),
    ("gzMercSkillText", 7, "중화기"),
    ("gzMercSkillText", 8, "자동화기"),
    ("gzMercSkillText", 9, "은신"),
    ("gzMercSkillText", 10, "양손잡이"),
    ("gzMercSkillText", 11, "도둑"),
    ("gzMercSkillText", 12, "무술"),
    ("gzMercSkillText", 13, "칼 사용"),
    ("gzMercSkillText", 14, "옥상 명중 보너스"),
    ("gzMercSkillText", 15, "위장"),
    ("gzMercSkillText", 16, "(전문가)"),

    ("gzMiscString", 0, "용병의 도움 없이 민병대가 계속 전투합니다..."),
    ("gzMiscString", 1, "차량에는 지금 연료가 더 필요하지 않습니다."),
    ("gzMiscString", 2, "연료 탱크가 %d%% 차 있습니다."),
    ("gzMiscString", 3, "데이드라나의 군대가 %s을(를) 완전히 되찾았습니다."),
    ("gzMiscString", 4, "급유 지점을 잃었습니다."),
    ("gzMoneyAmounts", 0, "$1000"),
    ("gzMoneyAmounts", 1, "$100"),
    ("gzMoneyAmounts", 2, "$10"),
    ("gzMoneyAmounts", 3, "완료"),
    ("gzMoneyAmounts", 4, "분리"),
    ("gzMoneyAmounts", 5, "인출"),
    ("gzMoneyWithdrawMessageText", 0, "한 번에 최대 $20,000까지만 인출할 수 있습니다."),
    ("gzMoneyWithdrawMessageText", 1, "%s을(를) 계좌에 입금하시겠습니까?"),

    # Pre-battle interface
    ("gzNonPersistantPBIText", 0, "전투가 진행 중입니다. 전술 화면에서만 후퇴할 수 있습니다."),
    ("gzNonPersistantPBIText", 1, "구역에 진입하여 진행 중인 전투를 계속합니다. (|E)"),
    ("gzNonPersistantPBIText", 2, "진행 중인 전투를 자동으로 해결합니다. (|A)"),
    ("gzNonPersistantPBIText", 3, "공격 중인 전투는 자동으로 해결할 수 없습니다."),
    ("gzNonPersistantPBIText", 4, "매복당한 전투는 자동으로 해결할 수 없습니다."),
    ("gzNonPersistantPBIText", 5, "광산에서 괴물과 싸우는 전투는 자동으로 해결할 수 없습니다."),
    ("gzNonPersistantPBIText", 6, "적대적인 민간인이 있는 전투는 자동으로 해결할 수 없습니다."),
    ("gzNonPersistantPBIText", 7, "블러드캣이 있는 전투는 자동으로 해결할 수 없습니다."),
    ("gzNonPersistantPBIText", 8, "전투 진행 중"),
    ("gzNonPersistantPBIText", 9, "지금은 후퇴할 수 없습니다."),
    ("gzProsLabel", None, "장점:"),
    ("pAntiHackerString", None, "오류: 파일이 없거나 손상되었습니다. 게임을 종료합니다."),
    ("pAssignMenuStrings", 0, "근무"),
    ("pAssignMenuStrings", 1, "의사"),
    ("pAssignMenuStrings", 2, "환자"),
    ("pAssignMenuStrings", 3, "차량"),
    ("pAssignMenuStrings", 4, "수리"),
    ("pAssignMenuStrings", 5, "훈련"),
    ("pAssignMenuStrings", 6, "취소"),
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
    print(f"Applied Korean UI batch 004: {changed}/{len(BATCH)} entries changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
