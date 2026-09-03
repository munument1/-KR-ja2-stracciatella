#!/usr/bin/env python3
"""Apply Korean UI translation batch 009.

Focus: dealer UI, difficulty confirmation, map status, tactical Iron Man
messages, options, save/load and talk menus.
"""

from __future__ import annotations

import json
from apply_ui_translation_batch_001 import PLACEHOLDER_RE, TARGET, get_value, set_value

RANGES: list[tuple[str, int, list[str]]] = [
    ("zDealerStrings", 0, ["구매/판매", "구매", "판매", "수리"]),
    ("zGioDifConfirmText", 0, [
        "초보 난이도를 선택했습니다. Jagged Alliance를 처음 접하거나 전략 게임 자체가 익숙하지 않은 분, 또는 전투를 좀 더 짧게 즐기고 싶은 분께 적합합니다. 이 선택은 게임 전체에 영향을 미치므로 신중히 결정하십시오. 초보 난이도로 플레이하시겠습니까?",
        "숙련 난이도를 선택했습니다. Jagged Alliance나 비슷한 게임에 이미 익숙한 분께 적합합니다. 이 선택은 게임 전체에 영향을 미치므로 신중히 결정하십시오. 숙련 난이도로 플레이하시겠습니까?",
        "전문가 난이도를 선택했습니다. 경고했습니다. 시체 가방에 실려 돌아오더라도 우리 탓은 하지 마십시오. 이 선택은 게임 전체에 영향을 미치므로 신중히 결정하십시오. 전문가 난이도로 플레이하시겠습니까?",
    ]),
    ("zHealthStr", 0, ["빈사", "위독", "불량", "부상", "건강", "튼튼", "최상"]),
    ("zMarksMapScreenText", 0, [
        "지도 층",
        "민병대가 없습니다. 마을 민병대를 확보하려면 주민을 훈련해야 합니다.",
        "일일 수입",
        "용병이 생명보험에 가입되어 있습니다.",
        "%s은(는) 피곤하지 않습니다.",
        "%s은(는) 이동 중이라 잠들 수 없습니다.",
        "%s은(는) 너무 피곤합니다. 조금 뒤에 다시 시도하십시오.",
        "%s은(는) 운전 중입니다.",
        "잠든 용병이 있는 분대는 이동할 수 없습니다.",
        "계약 비용은 지불할 수 있지만 이 용병의 생명보험료까지 낼 돈은 없습니다.",
        "%s의 보험료는 %s이며 추가 기간은 %d일입니다. 지불하시겠습니까?",
        "구역 인벤토리",
        "용병에게 의료 보증금이 있습니다.",
        "의료진",
        "환자",
        "완료",
        "정지",
        "%s에게 수리 키트가 없습니다.",
        "%s에게 의료 키트가 없습니다.",
        "현재 훈련받으려는 사람이 충분하지 않습니다.",
        "%s의 민병대가 가득 찼습니다.",
        "용병의 계약 기간이 정해져 있습니다.",
        "용병의 계약에 보험이 없습니다.",
    ]),
    ("zNewTacticalMessages", 0, [
        "표적까지 거리: %d칸",
        "총기 사거리: %d칸, 표적까지 거리: %d칸",
        "엄폐 표시",
        "시야",
        "철인 모드에서는 적이 주변에 있을 때 저장할 수 없습니다.",
        "(전투 중 저장할 수 없음)",
        "(이전 저장 파일을 불러올 수 없음)",
    ]),
    ("zOptionsScreenHelpText", 0, [
        "인물 대사를 들으려면 이 옵션을 켜 두십시오.",
        "인물의 음성 확인 대사를 켜거나 끕니다.",
        "대화 내용을 화면 자막으로 표시할지 설정합니다.",
        "자막을 켰다면 NPC 대사를 천천히 읽을 수 있도록 이 옵션도 켜십시오.",
        "연기 애니메이션 때문에 프레임이 떨어진다면 이 옵션을 끄십시오.",
        "피 표현이 불편하다면 이 옵션을 끄십시오.",
        "팝업 확인 창이 나타날 때 마우스가 자동으로 이동하는 것을 원하지 않으면 이 옵션을 끄십시오.",
        "이 옵션을 켜면 이전 JAGGED ALLIANCE 게임과 같은 방식으로 인물을 선택합니다. 기본 방식과는 반대입니다.",
        "실시간 모드에서 이동 경로를 항상 표시하려면 켜십시오. 끈 상태에서는 SHIFT 키로 필요할 때만 표시할 수 있습니다.",
        "사격이 빗나갔을 때 총알이 어디에 떨어졌는지 표시하려면 켜십시오.",
        "켜면 실시간 이동 시 추가 안전 확인 클릭이 필요합니다.",
        "켜면 임무 중인 용병이 잠들거나 업무에 복귀할 때 알림을 표시합니다.",
        "켜면 미터법을 사용하고, 끄면 야드파운드법을 사용합니다.",
        "켜면 용병이 걸을 때 주변 바닥을 비춥니다. 프레임 향상을 원하면 끄십시오.",
        "켜면 커서를 용병 근처로 옮겼을 때 자동으로 해당 용병을 강조합니다.",
        "켜면 커서를 문 근처로 옮겼을 때 자동으로 문 위에 맞춥니다.",
        "켜면 아이템이 계속 빛납니다. (|I)",
        "켜면 나무 꼭대기를 표시합니다. (|T)",
        "켜면 가려진 벽의 와이어프레임을 표시합니다. (|W)",
        "켜면 이동 커서를 3D로 표시합니다. (|H|o|m|e)",
        "켜면 어두운 곳에서 용병 주변에 조명을 표시합니다. (|G)",
        "켜면 총알을 표시하지 않습니다.",
        "켜면 전투 모드에서 카메라가 선택한 용병을 계속 따라갑니다.",
    ]),
    ("zOptionsText", 0, [
        "게임 저장", "게임 불러오기", "종료", "완료", "효과음", "음성", "음악",
        "게임을 종료하고 메인 메뉴로 돌아가시겠습니까?",
        "음성 또는 자막 옵션 중 하나는 반드시 켜져 있어야 합니다.",
    ]),
    ("zOptionsToggleText", 0, [
        "음성",
        "확인 대사 음소거",
        "자막",
        "텍스트 대화 일시정지",
        "연기 애니메이션",
        "피와 고어 표현",
        "마우스 자동 이동 금지",
        "기존 선택 방식",
        "이동 경로 표시",
        "빗나간 탄환 표시",
        "실시간 이동 확인",
        "수면/각성 알림 표시",
        "미터법 사용",
        "이동 중 용병 조명",
        "커서를 용병에 맞춤",
        "커서를 문에 맞춤",
        "아이템 빛나기",
        "나무 꼭대기 표시",
        "와이어프레임 표시",
        "3D 커서 표시",
        "용병 아래 조명 표시",
        "탄환 숨기기",
        "추적 모드",
    ]),
    ("zSaveLoadText", 0, [
        "게임 저장",
        "게임 불러오기",
        "취소",
        "선택한 슬롯에 저장",
        "선택한 슬롯 불러오기",
        "게임을 성공적으로 저장했습니다.",
        "게임 저장 중 오류가 발생했습니다!",
        "게임을 성공적으로 불러왔습니다.",
        "게임 불러오기 오류: \"%s\"",
        "저장 파일의 게임 버전이 현재 버전과 다릅니다. 대부분의 경우 계속 진행해도 안전합니다.",
        "\"%s\" 저장 파일을 삭제하시겠습니까?",
        "주의:",
        "이전 버전의 저장 파일을 불러오려 합니다. 계속하면 저장 파일이 자동으로 현재 버전으로 갱신됩니다.",
        "이 저장 파일은 현재와 다른 모드 또는 모드 로드 순서로 저장되었습니다. 모드가 올바르게 작동하지 않을 수 있습니다.",
        "계속하시겠습니까?",
        "\"%s\" 저장 파일을 덮어쓰시겠습니까?",
        "저장 중...",
        "일반 총기",
        "다양한 총기",
        "현실적",
        "SF",
        "난이도",
        "활성화된 모드 없음",
        "모드:",
    ]),
    ("zTalkMenuStrings", 0, ["다시 말씀해 주시겠습니까?", "친근하게", "직접적으로", "위협", "주기", "영입"]),
]

SCALARS: list[tuple[str, str]] = [
    ("zDialogActions", "완료"),
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
    print(f"Applied Korean UI batch 009: {changed}/{total} entries changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
