#!/usr/bin/env python3
"""Apply Korean UI translation batch 008.

Focus: squad/tactical popup menus, training, financial transactions, update
panels, map mine/town information, web page titles and florist/order UI.
Proper-name-only arrays are intentionally left unchanged.
"""

from __future__ import annotations

import json
from apply_ui_translation_batch_001 import PLACEHOLDER_RE, TARGET, get_value, set_value

RANGES: list[tuple[str, int, list[str]]] = [
    ("pShortAttributeStrings", 0, [
        "민첩", "손재", "힘", "통솔", "지혜", "레벨", "사격", "폭발", "기계", "의술",
    ]),
    ("pShowBookmarkString", 0, ["도움말", "즐겨찾기를 보려면 웹 버튼을 다시 클릭하십시오."]),
    ("pSkyriderText", 0, [
        "스카이라이더에게 $%d을(를) 지불했습니다.",
        "스카이라이더에게 아직 $%d을(를) 지불해야 합니다.",
        "스카이라이더에게 탑승자가 없습니다. 이 구역의 용병을 수송하려면 먼저 차량/헬리콥터 임무에 배치하십시오.",
    ]),
    ("pSquadMenuStrings", 0, [
        "1분대", "2분대", "3분대", "4분대", "5분대", "6분대", "7분대", "8분대", "9분대", "10분대",
        "11분대", "12분대", "13분대", "14분대", "15분대", "16분대", "17분대", "18분대", "19분대", "20분대", "취소",
    ]),
    ("pTacticalPopupButtonStrings", 0, [
        "서기/걷기 (|S)",
        "쭈그리기/쭈그려 이동 (|C)",
        "서서 달리기 (|R)",
        "엎드리기/포복 (|P)",
        "보기 (|L)",
        "행동",
        "대화",
        "조사 (|C|t|r|l)",
        "직접 열기",
        "함정 조사",
        "자물쇠 따기",
        "강제로 열기",
        "함정 해제",
        "잠그기",
        "잠금 해제",
        "문 폭약 사용",
        "쇠지렛대 사용",
        "취소 (|E|s|c)",
        "닫기",
    ]),
    ("pTrainingMenuStrings", 0, ["연습", "민병대", "교관", "훈련생", "취소"]),
    ("pTrainingStrings", 0, ["연습", "민병대", "교관", "훈련생"]),
    ("pTransactionText", 0, [
        "발생 이자",
        "익명 입금",
        "거래 수수료",
        "A.I.M.에서 %s 고용",
        "Bobby Ray 구매",
        "M.E.R.C. 계정 정산",
        "%s의 의료 보증금",
        "I.M.P. 프로파일 분석",
        "%s의 보험 구매",
        "%s의 보험 축소",
        "%s의 보험 연장",
        "%s의 보험 취소",
        "%s의 보험금 청구",
        "%s의 계약을 1일 연장",
        "%s의 계약을 1주 연장",
        "%s의 계약을 2주 연장",
        "광산 수입",
        "",
        "꽃 구매",
        "%s의 의료 보증금 전액 환불",
        "%s의 의료 보증금 일부 환불",
        "%s의 의료 보증금 환불 없음",
        "%s에게 지급",
        "%s에게 자금 이체",
        "%s에게서 자금 이체",
        "%s의 민병대 장비 지급",
        "%s에게서 아이템 구매",
        "%s이(가) 돈을 입금함",
    ]),
    ("pTrashItemText", 0, [
        "버리면 다시는 볼 수 없습니다. 정말 버리시겠습니까?",
        "이 아이템은 정말 중요한 것 같습니다. 정말 정말로 버리시겠습니까?",
    ]),
    ("pUpdateMercStrings", 0, [
        "알림:", "계약 만료 용병:", "임무 완료 용병:", "업무 복귀 용병:", "수면 중인 용병:", "곧 계약 만료:",
    ]),
    ("pUpdatePanelButtons", 0, ["계속", "정지"]),
    ("pUpperLeftMapScreenStrings", 0, ["임무", "체력", "사기", "상태"]),
    ("pVehicleStrings", 0, ["엘도라도", "허머", "아이스크림 트럭", "지프", "탱크", "헬리콥터"]),
    ("pWebPagesTitles", 0, [
        "A.I.M.",
        "A.I.M. 회원",
        "A.I.M. 인물 사진",
        "A.I.M. 정렬",
        "A.I.M.",
        "A.I.M. 전직 용병",
        "A.I.M. 정책",
        "A.I.M. 역사",
        "A.I.M. 링크",
        "M.E.R.C.",
        "M.E.R.C. 계정",
        "M.E.R.C. 등록",
        "M.E.R.C. 인덱스",
        "Bobby Ray's",
        "Bobby Ray's - 총기",
        "Bobby Ray's - 탄약",
        "Bobby Ray's - 방어구",
        "Bobby Ray's - 기타",
        "Bobby Ray's - 중고",
        "Bobby Ray's - 통신판매",
        "I.M.P.",
        "I.M.P.",
        "유나이티드 플로럴 서비스",
        "유나이티드 플로럴 서비스 - 갤러리",
        "유나이티드 플로럴 서비스 - 주문서",
        "유나이티드 플로럴 서비스 - 카드 갤러리",
        "Malleus, Incus & Stapes 보험 중개사",
        "정보",
        "계약",
        "의견",
        "맥길리커티 장례식장",
        "URL을 찾을 수 없습니다.",
        "Bobby Ray's - 최근 배송",
        "",
        "",
    ]),
    ("pwMineStrings", 0, [
        "광산", "은", "금", "일일 생산량", "가능 생산량", "폐광", "가동 중단", "고갈 임박", "생산 중", "상태", "생산율", "광석 종류", "마을 통제", "마을 충성도",
    ]),
    ("pwMiscSectorStrings", 0, ["적 병력", "구역", "아이템 수", "알 수 없음", "통제 중", "예", "아니요"]),
    ("pwTownInfoStrings", 0, ["규모", "통제", "연계 광산", "충성도", "주요 시설", "민간인 훈련", "민병대"]),
    ("sFacilitiesStrings", 0, ["없음", "병원", "산업 시설", "교도소", "군사 시설", "공항", "사격장"]),
    ("sFloristCards", 0, ["원하는 카드를 클릭하십시오", "뒤로"]),
    ("sFloristGalleryText", 0, [
        "이전", "다음", "주문할 꽃을 클릭하십시오.", "시들거나 찌그러진 꽃다발에는 $10의 추가 요금이 붙습니다.", "홈",
    ]),
    ("sFloristText", 0, [
        "갤러리",
        "\"어디든 공중 투하해 드립니다\"",
        "1-555-SCENT-ME",
        "333 NoseGay Dr, Seedy City, CA USA 90210",
        "http://www.scent-me.com",
        "빠르고 정확하게 배달합니다!",
        "전 세계 대부분 지역에 익일 배송을 보장합니다. 일부 제한이 적용됩니다.",
        "세계 최저가를 보장합니다!",
        "광고된 더 낮은 가격을 보여 주시면 장미 한 다발을 무료로 드립니다.",
        "1981년부터 꽃과 식물을 날려 보내고 있습니다.",
        "훈장까지 받은 전직 폭격기 조종사들이 요청 지점 반경 10마일 안에 꽃다발을 공중 투하합니다. 언제든, 매번 확실하게!",
        "당신의 꽃에 대한 환상을 만족시켜 드립니다.",
        "세계적으로 유명한 플로리스트 브루스가 자체 온실에서 가장 신선하고 질 좋은 꽃을 직접 골라 드립니다.",
        "그리고 기억하세요. 없는 꽃도 빠르게 길러 드립니다!",
    ]),
    ("sFuneralString", 0, [
        "맥길리커티 장례식장: 1983년부터 유가족의 슬픔을 함께해 왔습니다.",
        "장례지도사이자 전 A.I.M. 용병인 머레이 \"팝스\" 맥길리커티는 숙련되고 경험 많은 장의사입니다.",
        "평생 죽음과 사별을 가까이해 온 팝스는 그 고통이 얼마나 큰지 잘 압니다.",
        "맥길리커티 장례식장은 위로해 줄 어깨부터 심하게 훼손된 시신의 사후 복원까지 폭넓은 서비스를 제공합니다.",
        "당신과 사랑하는 이가 편히 쉴 수 있도록 맥길리커티 장례식장이 도와드리겠습니다.",
        "꽃 보내기",
        "관 및 유골함",
        "화장 서비스",
        "사전 장례 계획",
        "장례 예절",
        "유감스럽게도 가족의 사망으로 이 사이트의 나머지 부분은 아직 완성되지 않았습니다. 유언장 확인과 유산 분배가 끝나는 대로 최대한 빨리 완성하겠습니다.",
        "힘든 시기를 보내고 계신 여러분께 깊은 위로의 말씀을 드립니다. 다시 방문해 주십시오.",
    ]),
    ("sKeyDescriptionStrings", 0, ["발견 구역:", "발견 일자:"]),
    ("sOrderFormText", 0, [
        "뒤로", "보내기", "지우기", "갤러리", "꽃다발 이름:", "가격:", "주문 번호:", "배송일", "다음 날", "도착하는 대로", "배송 위치", "추가 서비스",
        "찌그러진 꽃다발($10)", "검은 장미($20)", "시든 꽃다발($10)", "과일 케이크(재고 시)($10)", "개인 메시지:",
        "카드 크기 제한으로 메시지는 75자를 넘을 수 없습니다.", "...또는 다음 중 하나를 선택하십시오", "표준 카드", "결제 정보", "이름:",
    ]),
]

SCALARS: list[tuple[str, str]] = [
    ("pSkillAtZeroWarning", "확실합니까? 0은 이 기술을 전혀 사용할 수 없다는 뜻입니다."),
    ("pWebTitle", "sir-FER 4.0"),
    ("sMapLevelString", "지하층:"),
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
    print(f"Applied Korean UI batch 008: {changed}/{total} entries changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
