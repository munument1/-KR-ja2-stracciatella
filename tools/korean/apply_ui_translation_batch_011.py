#!/usr/bin/env python3
"""Apply Korean UI translation batch 011.

Focus: vanilla-compatible history log strings. These translations are reused
from the reviewed JA2 r7609/1.13 History.xml corpus after exact English-source
and original-order matching. Stracciatella currently uses entries 1..77;
1.13-only entries 78+ are intentionally not imported.
"""

from __future__ import annotations

import json
from apply_ui_translation_batch_001 import PLACEHOLDER_RE, TARGET, get_value, set_value

HISTORY = [
    "%s을(를) A.I.M.에서 고용함.",
    "%s을(를) M.E.R.C.에서 고용함.",
    "%s 사망.",
    "M.E.R.C. 미지급금 정산.",
    "엔리코 치발도리의 임무를 수락함.",
    "IMP 프로필 생성.",
    "%s의 보험 계약을 구매함.",
    "%s의 보험 계약을 취소함.",
    "%s의 보험금이 지급됨.",
    "%s의 계약을 하루 연장함.",
    "%s의 계약을 1주 연장함.",
    "%s의 계약을 2주 연장함.",
    "%s을(를) 해고함.",
    "%s이(가) 그만둠.",
    "퀘스트 시작.",
    "퀘스트 완료.",
    "%s 광산 책임자와 대화함.",
    "%s 해방.",
    "치트 사용.",
    "내일까지 오메르타에 식량이 도착할 예정.",
    "%s이(가) 대릴 힉스의 아내가 되기 위해 팀을 떠남.",
    "%s의 계약이 만료됨.",
    "%s을(를) 영입함.",
    "엔리코가 진척 부족에 불만을 표함.",
    "전투 승리.",
    "%s 광산의 광석이 고갈되기 시작함.",
    "%s 광산의 광석이 고갈됨.",
    "%s 광산이 폐쇄됨.",
    "%s 광산이 재가동됨.",
    "틱사라는 감옥이 있다는 사실을 알아냄.",
    "오르타라는 비밀 무기 공장이 있다는 소문을 들음.",
    "오르타의 과학자가 다수의 로켓 소총을 기증함.",
    "데이드라나 여왕은 시체를 이용할 곳이 있음.",
    "프랭크가 산모나의 격투 경기에 관해 이야기함.",
    "환자 한 명이 광산에서 무언가를 봤다고 주장함.",
    "폭발물을 파는 데빈이라는 사람을 만남.",
    "유명한 전직 A.I.M. 용병 마이크와 마주침!",
    "무기를 거래하는 토니를 만남.",
    "크로트 병장에게서 로켓 소총을 받음.",
    "카일에게 엔젤의 가죽 상점 권리증서를 건넴.",
    "매드랩이 로봇을 만들어 주겠다고 제안함.",
    "개비는 벌레용 은신 약물을 만들 수 있음.",
    "키스가 폐업함.",
    "하워드가 데이드라나 여왕에게 청산가리를 제공함.",
    "캄브리아의 잡화상 키스를 만남.",
    "발리메에서 의약품을 거래하는 하워드를 만남.",
    "소규모 수리점을 운영하는 페르코를 만남.",
    "철물점을 운영하는 발리메의 샘을 만남.",
    "프란츠는 전자제품과 기타 물품을 거래함.",
    "아놀드는 그룸에서 수리점을 운영함.",
    "프레도는 그룸에서 전자제품을 수리함.",
    "발리메의 부자에게서 기부금을 받음.",
    "제이크라는 폐차장 상인을 만남.",
    "부랑자 한 명이 전자식 키카드를 건넴.",
    "월터에게 뇌물을 주어 지하실 문을 열게 함.",
    "데이브에게 연료가 있으면 무료로 주유해 줌.",
    "파블로에게 뇌물을 줌.",
    "킹핀은 산모나 광산에 돈을 보관함.",
    "%s이(가) 익스트림 파이팅 경기에서 승리함.",
    "%s이(가) 익스트림 파이팅 경기에서 패배함.",
    "%s이(가) 익스트림 파이팅에서 실격됨.",
    "폐광에 숨겨진 거액의 돈을 발견함.",
    "킹핀이 보낸 암살자와 조우함.",
    "구역의 통제권을 잃음.",
    "구역을 방어함.",
    "전투 패배.",
    "치명적인 매복.",
    "적의 매복을 섬멸함.",
    "공격 실패.",
    "공격 성공!",
    "생물들의 공격.",
    "블러드캣에게 살해됨.",
    "블러드캣을 몰살함.",
    "%s이(가) 살해됨.",
    "카르멘에게 테러리스트의 머리를 건넴.",
    "슬레이가 떠남.",
    "%s 처치.",
]


def check_and_set(data: dict, index: int, korean: str) -> int:
    current = get_value(data, "pHistoryStrings", index)
    if PLACEHOLDER_RE.findall(current) != PLACEHOLDER_RE.findall(korean):
        raise SystemExit(
            f"Placeholder mismatch at pHistoryStrings[{index}]: "
            f"{PLACEHOLDER_RE.findall(current)} != {PLACEHOLDER_RE.findall(korean)}"
        )
    if current == korean:
        return 0
    set_value(data, "pHistoryStrings", index, korean)
    return 1


def main() -> int:
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    changed = 0
    for index, korean in enumerate(HISTORY, start=1):
        changed += check_and_set(data, index, korean)
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    print(f"Applied Korean UI batch 011: {changed}/{len(HISTORY)} entries changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
