#!/usr/bin/env python3
"""Apply Korean UI translation batch 005.

Focus: assignments, contracts, laptop/email/finance, helicopter travel and IMP UI.
Long history-event prose is intentionally deferred to a separate batch.
"""

from __future__ import annotations

import json
from apply_ui_translation_batch_001 import PLACEHOLDER_RE, TARGET, get_value, set_value

RANGES: list[tuple[str, int, list[str]]] = [
    ("pAssignmentStrings", 0, [
        "1분대", "2분대", "3분대", "4분대", "5분대", "6분대", "7분대", "8분대", "9분대", "10분대",
        "11분대", "12분대", "13분대", "14분대", "15분대", "16분대", "17분대", "18분대", "19분대", "20분대",
        "근무", "의사", "환자", "차량", "이동 중", "수리", "연습", "민병대", "교관", "훈련생",
        "사망", "전투 불능", "포로", "병원", "비어 있음",
    ]),
    ("pAttributeMenuStrings", 0, [
        "힘", "손재주", "민첩성", "체력", "사격술", "의술", "기계", "통솔력", "폭발물", "취소",
    ]),
    ("pBookMarkStrings", 0, [
        "A.I.M.", "Bobby Ray's", "I.M.P", "M.E.R.C.", "장례식장", "꽃집", "보험", "취소",
    ]),
    ("pBullseyeStrings", 0, [
        "용병들이 대신 도착할 구역을 클릭하십시오.",
        "확인. 도착하는 용병들은 %s에 투입됩니다.",
        "그곳은 영공이 확보되지 않아 용병을 비행기로 보낼 수 없습니다!",
        "취소되었습니다. 도착 구역은 변경되지 않았습니다.",
        "%s 상공이 더 이상 안전하지 않습니다! 도착 구역을 %s(으)로 옮겼습니다.",
    ]),
    ("pConditionStrings", 0, [
        "최상", "양호", "보통", "부상", "피로", "출혈", "의식 불명", "빈사", "사망",
    ]),
    ("pContractStrings", 0, [
        "계약 옵션:", "", "1일 연장 제안", "1주 연장 제안", "2주 연장 제안", "해고", "취소",
    ]),
    ("pDeleteMailStrings", 0, ["메일을 삭제하시겠습니까?", "읽지 않은 메일을 삭제하시겠습니까?"]),
    ("pDirectionStr", 0, [
        "북동쪽", "동쪽", "남동쪽", "남쪽", "남서쪽", "서쪽", "북서쪽", "북쪽",
    ]),
    ("pDoctorWarningString", 0, [
        "%s은(는) 치료하기에 충분히 가까이 있지 않습니다.",
        "의료진이 모두에게 붕대를 완전히 감아 주지 못했습니다.",
    ]),
    ("pDoorTrapStrings", 0, [
        "함정 없음", "폭발 함정", "전기 함정", "사이렌 함정", "무음 경보 함정",
    ]),
    ("pDownloadString", 0, ["다운로드 중", "다시 불러오는 중"]),
    ("pEmailHeaders", 0, ["보낸 사람:", "제목:", "일자:"]),
    ("pEpcMenuStrings", 0, ["근무", "환자", "차량", "호위 해제", "취소"]),
    ("pExitingSectorHelpText", 0, [
        "선택하면 인접 구역을 즉시 불러옵니다.",
        "선택하면 용병의 이동에 시간이 걸리므로\n자동으로 지도 화면으로 이동합니다.",
        "이 구역은 적이 점령 중이므로 용병을 남겨 둘 수 없습니다.\n다른 구역을 불러오기 전에 이 상황을 해결해야 합니다.",
        "남은 용병들을 이 구역 밖으로 이동시키면\n인접 구역을 즉시 불러옵니다.",
        "남은 용병들을 이 구역 밖으로 이동시키면\n이동에 시간이 걸리므로 자동으로 지도 화면으로 이동합니다.",
        "%s은(는) 용병의 호위가 필요하므로 혼자 이 구역을 떠날 수 없습니다.",
        "%s은(는) %s을(를) 호위 중이므로 혼자 이 구역을 떠날 수 없습니다.",
        "%s은(는) %s을(를) 호위 중이므로 혼자 이 구역을 떠날 수 없습니다.",
        "%s은(는) 여러 인물을 호위 중이므로 혼자 이 구역을 떠날 수 없습니다.",
        "%s은(는) 여러 인물을 호위 중이므로 혼자 이 구역을 떠날 수 없습니다.",
        "분대가 이동하려면 모든 용병이\n주변에 모여 있어야 합니다.",
        "선택하면 %s은(는) 혼자 이동하며\n자동으로 별도의 분대에 재배치됩니다.",
        "선택하면 현재 선택한 분대가\n이 구역을 떠나 이동합니다.",
        "%s은(는) 용병들의 호위를 받고 있어 혼자 이 구역을 떠날 수 없습니다. 떠나려면 다른 용병들도 근처에 있어야 합니다.",
    ]),
    ("pExtraIMPStrings", 0, [
        "실제 프로파일링을 시작하려면 성격을 선택하십시오.",
        "성격 선택을 마쳤습니다. 이제 능력치를 선택하십시오.",
        "능력치 배분을 마쳤습니다. 이제 초상화를 선택할 수 있습니다.",
        "마지막으로 자신에게 가장 잘 맞는 음성 샘플을 선택하십시오.",
    ]),
    ("pFilesSenderList", 0, [
        "정찰 보고서", "감청 #1", "감청 #2", "감청 #3", "감청 #4", "감청 #5", "감청 #6",
    ]),
    ("pFinanceHeaders", 0, ["일자", "수입", "지출", "거래", "잔액", "페이지", "일수"]),
    ("pFinanceSummary", 0, [
        "수입:", "지출:", "어제 실제 수입:", "어제 기타 입금:", "어제 지출:", "어제 마감 잔액:",
        "오늘 실제 수입:", "오늘 기타 입금:", "오늘 지출:", "현재 잔액:", "예상 수입:", "예상 잔액:",
    ]),
    ("pHelicopterEtaStrings", 0, [
        "총 거리:  ", " 안전:  ", " 위험:", "총 비용: ", "도착 예정:  ",
        "헬기의 연료가 부족하여 적대 지역에 착륙해야 합니다!", "탑승자: ",
        "스카이라이더와 도착 투입 지점 중 어디를 선택하시겠습니까?", "스카이라이더", "도착 지점",
    ]),
    ("pHistoryHeaders", 0, ["일자", "페이지", "일자", "위치", "사건"]),
    ("pImpButtonText", 0, [
        "소개", "시작", "성격", "능력치", "초상화", "음성 %d", "완료", "처음부터",
        "예, 강조된 답을 선택합니다.", "예", "아니요", "완료", "이전", "다음",
        "예, 맞습니다.", "아니요, 처음부터 다시 하겠습니다.", "예, 선택합니다.", "아니요", "뒤로", "취소",
        "예, 확실합니다.", "아니요, 다시 살펴보겠습니다.", "등록", "분석 중", "확인", "음성", "특기",
    ]),
    ("pImpPopUpStrings", 0, [
        "잘못된 인증 코드입니다.",
        "전체 프로파일링 과정을 처음부터 다시 시작하려 합니다. 확실합니까?",
        "올바른 이름과 성별을 입력하십시오.",
        "재정 상태를 예비 분석한 결과 프로파일 분석 비용을 지불할 수 없습니다.",
        "현재는 선택할 수 없는 항목입니다.",
        "정확한 프로파일을 완성하려면 팀에 최소 한 명을 더 받을 공간이 있어야 합니다.",
        "프로파일 작성이 이미 완료되었습니다.",
    ]),
    ("pInvPanelTitleStrings", 0, ["방어구", "중량", "위장"]),
    ("pLaptopIcons", 0, ["이메일", "웹", "재정", "인사", "기록", "파일", "종료", "sir-FER 4.0"]),
    ("pLaptopTitles", 0, ["메일함", "파일 뷰어", "인사", "회계 장부", "기록"]),
    ("pLongAssignmentStrings", 0, [
        "1분대", "2분대", "3분대", "4분대", "5분대", "6분대", "7분대", "8분대", "9분대", "10분대",
        "11분대", "12분대", "13분대", "14분대", "15분대", "16분대", "17분대", "18분대", "19분대", "20분대",
        "근무", "의사", "환자", "차량", "이동 중", "수리", "연습", "민병대 훈련", "동료 훈련", "훈련생",
        "사망", "전투 불능", "포로", "병원", "비어 있음",
    ]),
]

SCALARS: list[tuple[str, str]] = [
    ("pContractButtonString", "계약"),
    ("pDayStrings", "일"),
    ("pEmailTitleText", "메일함"),
    ("pErrorStrings", "호스트 연결이 불안정합니다. 전송 시간이 더 길어질 수 있습니다."),
    ("pEtaString", "도착 예정:"),
    ("pFilesTitle", "파일 뷰어"),
    ("pFinanceTitle", "회계 장부"),
    ("pHistoryLocations", "해당 없음"),
    ("pHistoryTitle", "기록"),
    ("pIMPBeginScreenStrings", "( 최대 8자 )"),
    ("pIMPFinishButtonText", "분석 중"),
    ("pIMPFinishStrings", "감사합니다, %s"),
    ("pIMPVoicesStrings", "음성"),
    ("pLandMarkInSectorString", "%d분대가 %s 구역에서 누군가를 발견했습니다"),
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
    print(f"Applied Korean UI batch 005: {changed}/{total} entries changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
