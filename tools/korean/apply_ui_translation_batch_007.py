#!/usr/bin/env python3
"""Apply Korean UI translation batch 007: common pMessageStrings only.

This array mixes save/load messages, combat feedback, units and several
placeholder-heavy arrival/payment strings, so it is isolated from other UI
batches for easier regression review.
"""

from __future__ import annotations

import json
from apply_ui_translation_batch_001 import PLACEHOLDER_RE, TARGET, get_value, set_value

TRANSLATIONS = [
    "게임을 종료하시겠습니까?",
    "확인",
    "예",
    "아니요",
    "취소",
    "재고용",
    "거짓말",
    "설명 없음",
    "게임을 저장했습니다.",
    "일",
    "용병",
    "빈 슬롯",
    "rpm",
    "분",
    "m",
    "발",
    "kg",
    "lb",
    "홈",
    "USD",
    "해당 없음",
    "한편",
    "%s이(가) %s%s 구역에 도착했습니다",
    "버전",
    "새 저장 파일 만들기",
    "이 슬롯은 전술 및 지도 화면에서 ALT+S로 만든 빠른 저장용입니다.",
    "열림",
    "닫힘",
    "디스크 여유 공간이 부족합니다. 남은 공간은 %sMB이며 Jagged Alliance 2에는 %sMB가 필요합니다.",
    "%s이(가) %s에 걸렸습니다.",
    "%s이(가) 약물을 복용했습니다.",
    "%s은(는) 의술 능력이 없습니다.",
    "게임 데이터의 무결성이 손상되었습니다.",
    "오류: CD-ROM이 꺼내졌습니다.",
    "이곳에서는 발사할 공간이 없습니다.",
    "지금은 자세를 바꿀 수 없습니다.",
    "내려놓기",
    "던지기",
    "건네기",
    "%s이(가) %s에게 건넸습니다.",
    "%s을(를) %s에게 건넬 공간이 없습니다.",
    " 부착됨)",
    "치트 레벨 1 도달",
    "치트 레벨 2 도달",
    "분대 은신 모드 켜짐.",
    "분대 은신 모드 꺼짐.",
    "%s 은신 모드 켜짐.",
    "%s 은신 모드 꺼짐.",
    "추가 와이어프레임 켜짐",
    "추가 와이어프레임 꺼짐",
    "이 층에서는 더 올라갈 수 없습니다...",
    "더 아래 층이 없습니다...",
    "지하 %d층으로 진입 중...",
    "지하에서 나가는 중...",
    "의",
    "추적 모드 꺼짐.",
    "추적 모드 켜짐.",
    "3D 커서 꺼짐.",
    "3D 커서 켜짐.",
    "%d분대 활성화.",
    "%s의 일당 %s을(를) 지불할 돈이 없습니다.",
    "건너뛰기",
    "%s은(는) 혼자 떠날 수 없습니다.",
    "SaveGame99.sav라는 저장 파일을 만들었습니다. 필요하다면 SaveGame01~SaveGame10 중 하나로 이름을 바꾸면 불러오기 화면에서 사용할 수 있습니다.",
    "%s이(가) %s을(를) 마셨습니다.",
    "드라센에 배송 물품이 도착했습니다.",
    "%s은(는) 지정한 투입 지점(%s 구역)에 %d일 약 %s에 도착할 예정입니다.",
    "기록이 갱신되었습니다.",
]


def main() -> int:
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    source = data["pMessageStrings"]
    if len(source) != len(TRANSLATIONS):
        raise SystemExit(f"pMessageStrings length changed: source={len(source)} batch={len(TRANSLATIONS)}")

    changed = 0
    for index, korean in enumerate(TRANSLATIONS):
        current = get_value(data, "pMessageStrings", index)
        if PLACEHOLDER_RE.findall(current) != PLACEHOLDER_RE.findall(korean):
            raise SystemExit(
                f"Placeholder mismatch at pMessageStrings[{index}]: "
                f"{PLACEHOLDER_RE.findall(current)} != {PLACEHOLDER_RE.findall(korean)}"
            )
        if current != korean:
            set_value(data, "pMessageStrings", index, korean)
            changed += 1

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    print(f"Applied Korean UI batch 007: {changed}/{len(TRANSLATIONS)} entries changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
