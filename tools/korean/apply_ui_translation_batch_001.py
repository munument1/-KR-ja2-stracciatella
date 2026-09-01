#!/usr/bin/env python3
"""Apply the first reviewed Korean UI translation batch.

This batch targets the most visible laptop/store/mercenary interface strings.
It updates entries by exact top-level key + array index instead of global text
replacement, so duplicated English strings can keep context-specific Korean.

The script also verifies printf/format placeholders before writing.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

TARGET = Path("assets/externalized/strings/translation-kor.json")
PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[a-zA-Z]|\{[^{}]*\}")

# (top-level key, index-or-None, Korean translation)
BATCH: list[tuple[str, int | None, str]] = [
    # A.I.M.
    ("AimAlumniText", 0, "1페이지"),
    ("AimAlumniText", 1, "2페이지"),
    ("AimAlumniText", 2, "3페이지"),
    ("AimAlumniText", 3, "A.I.M. 전직 용병"),
    ("AimAlumniText", 4, "완료"),
    ("AimBottomMenuText", 0, "홈"),
    ("AimBottomMenuText", 1, "회원"),
    ("AimBottomMenuText", 2, "전직 용병"),
    ("AimBottomMenuText", 3, "정책"),
    ("AimBottomMenuText", 4, "역사"),
    ("AimBottomMenuText", 5, "링크"),
    ("AimFiText", 0, "비용"),
    ("AimFiText", 1, "경험"),
    ("AimFiText", 2, "사격술"),
    ("AimFiText", 3, "의술"),
    ("AimFiText", 4, "폭발물"),
    ("AimFiText", 5, "기계"),
    ("AimFiText", 6, "%s 기준 오름차순으로 A.I.M. 용병 정렬"),
    ("AimFiText", 7, "%s 기준 내림차순으로 A.I.M. 용병 정렬"),
    ("AimFiText", 8, "왼쪽 클릭"),
    ("AimFiText", 9, "용병 선택"),
    ("AimFiText", 10, "오른쪽 클릭"),
    ("AimFiText", 11, "정렬 옵션"),
    ("AimFiText", 12, "사망"),
    ("AimFiText", 13, "임무 중"),
    ("AimHistoryText", 0, "A.I.M. 역사"),
    ("AimHistoryText", 1, "이전 페이지"),
    ("AimHistoryText", 2, "홈"),
    ("AimHistoryText", 3, "A.I.M. 전직 용병"),
    ("AimHistoryText", 4, "다음 페이지"),
    ("AimLinkText", None, "A.I.M. 링크"),
    ("AimMemberText", 0, "왼쪽 클릭"),
    ("AimMemberText", 1, "용병에게 연락"),
    ("AimMemberText", 2, "오른쪽 클릭"),
    ("AimMemberText", 3, "인물 사진 목록"),
    ("AimPolicyText", 0, "이전 페이지"),
    ("AimPolicyText", 1, "A.I.M. 홈페이지"),
    ("AimPolicyText", 2, "정책 목록"),
    ("AimPolicyText", 3, "다음 페이지"),
    ("AimPolicyText", 4, "동의 안 함"),
    ("AimPolicyText", 5, "동의"),
    ("AimPopUpText", 0, "전자 자금 이체 성공"),
    ("AimPopUpText", 1, "이체를 처리할 수 없음"),
    ("AimPopUpText", 2, "잔액 부족"),
    ("AimPopUpText", 3, "임무 중"),
    ("AimPopUpText", 4, "메시지를 남겨 주십시오"),
    ("AimPopUpText", 5, "사망"),
    ("AimPopUpText", 6, "이미 18명으로 팀이 가득 찼습니다."),
    ("AimPopUpText", 7, "사전 녹음 메시지"),
    ("AimPopUpText", 8, "메시지 녹음 완료"),
    ("AimScreenText", 0, "A.I.M.과 A.I.M. 로고는 대부분의 국가에서 등록 상표입니다."),
    ("AimScreenText", 1, "그러니 우리를 흉내 낼 생각은 하지 마십시오."),
    ("AimScreenText", 2, "Copyright 1998-1999 A.I.M., Ltd.  모든 권리 보유."),
    ("AimScreenText", 3, "유나이티드 플로럴 서비스"),
    ("AimScreenText", 4, "\"어디든 공중 투하해 드립니다\""),
    ("AimScreenText", 5, "제대로 하세요"),
    ("AimScreenText", 6, "... 처음부터"),
    ("AimScreenText", 7, "총과 온갖 물건. 우리가 안 팔면 당신에게 필요 없는 겁니다."),
    ("AimSortText", 0, "A.I.M. 용병"),
    ("AimSortText", 1, "정렬 기준:"),
    ("AimSortText", 2, "용병 인물 사진 목록 보기"),
    ("AimSortText", 3, "개별 용병 파일 보기"),
    ("AimSortText", 4, "A.I.M. 전직 용병 갤러리 보기"),

    # Bobby Ray's
    ("BobbyROrderFormText", 0, "주문서"),
    ("BobbyROrderFormText", 1, "수량"),
    ("BobbyROrderFormText", 2, "중량 (%s)"),
    ("BobbyROrderFormText", 3, "품목명"),
    ("BobbyROrderFormText", 4, "단가"),
    ("BobbyROrderFormText", 5, "합계"),
    ("BobbyROrderFormText", 6, "소계"),
    ("BobbyROrderFormText", 7, "배송비 (배송지 참조)"),
    ("BobbyROrderFormText", 8, "총합계"),
    ("BobbyROrderFormText", 9, "배송지"),
    ("BobbyROrderFormText", 10, "배송 속도"),
    ("BobbyROrderFormText", 11, "비용 (%s당)"),
    ("BobbyROrderFormText", 12, "익일 특급"),
    ("BobbyROrderFormText", 13, "영업일 기준 2일"),
    ("BobbyROrderFormText", 14, "일반 배송"),
    ("BobbyROrderFormText", 15, "주문 비우기"),
    ("BobbyROrderFormText", 16, "주문 확정"),
    ("BobbyROrderFormText", 17, "뒤로"),
    ("BobbyROrderFormText", 18, "홈"),
    ("BobbyROrderFormText", 19, "* 중고품 표시"),
    ("BobbyROrderFormText", 20, "이 주문을 결제할 돈이 부족합니다."),
    ("BobbyROrderFormText", 21, "<없음>"),
    ("BobbyROrderFormText", 22, "정말 이 주문을 %s(으)로 보내시겠습니까?"),
    ("BobbyROrderFormText", 23, "화물 중량**"),
    ("BobbyROrderFormText", 24, "** 최소 중량"),
    ("BobbyROrderFormText", 25, "배송 물품"),
    ("BobbyRText", 0, "주문 방법"),
    ("BobbyRText", 1, "품목을 클릭하십시오. 여러 개를 사려면 계속 클릭하고, 수량을 줄이려면 오른쪽 클릭하십시오. 원하는 물건을 모두 골랐다면 주문서로 이동하십시오."),
    ("BobbyRText", 2, "이전 품목"),
    ("BobbyRText", 3, "총기"),
    ("BobbyRText", 4, "탄약"),
    ("BobbyRText", 5, "방어구"),
    ("BobbyRText", 6, "기타"),
    ("BobbyRText", 7, "중고"),
    ("BobbyRText", 8, "다음 품목"),
    ("BobbyRText", 9, "주문서"),
    ("BobbyRText", 10, "홈"),
    ("BobbyRText", 11, "중량:"),
    ("BobbyRText", 12, "구경:"),
    ("BobbyRText", 13, "탄창:"),
    ("BobbyRText", 14, "사거리:"),
    ("BobbyRText", 15, "피해:"),
    ("BobbyRText", 16, "연사율:"),
    ("BobbyRText", 17, "가격:"),
    ("BobbyRText", 18, "재고:"),
    ("BobbyRText", 19, "주문 수량:"),
    ("BobbyRText", 20, "손상"),
    ("BobbyRText", 21, "소계:"),
    ("BobbyRText", 22, "* 기능 상태 %"),
    ("BobbyRText", 23, "젠장! 이 온라인 주문서는 한 번에 10개 품목만 주문할 수 있습니다. 더 주문하고 싶다면(그러길 바랍니다) 별도의 주문을 넣어 주십시오. 불편을 드려 죄송합니다."),
    ("BobbyRText", 24, "죄송합니다. 현재 이 물건의 재고가 더 없습니다. 나중에 다시 확인해 주십시오."),
    ("BobbyRText", 25, "죄송합니다. 현재 이 종류의 모든 물품이 품절입니다."),
    ("BobbyRaysFrontText", 0, "최신·최고의 무기와 군수품을 찾는다면 바로 이곳입니다"),
    ("BobbyRaysFrontText", 1, "어떤 폭발물 수요에도 완벽한 해결책을 찾아드립니다"),
    ("BobbyRaysFrontText", 2, "중고 및 정비 완료 물품"),
    ("BobbyRaysFrontText", 3, "기타"),
    ("BobbyRaysFrontText", 4, "총기"),
    ("BobbyRaysFrontText", 5, "탄약"),
    ("BobbyRaysFrontText", 6, "방어구"),
    ("BobbyRaysFrontText", 7, "우리가 안 팔면 어디서도 못 삽니다!"),
    ("BobbyRaysFrontText", 8, "공사 중"),
    ("BrokenLinkText", 0, "오류 404"),
    ("BrokenLinkText", 1, "사이트를 찾을 수 없습니다."),

    # A.I.M. character/insurance screens
    ("CharacterInfo", 0, "비용"),
    ("CharacterInfo", 1, "계약"),
    ("CharacterInfo", 2, "1일"),
    ("CharacterInfo", 3, "1주"),
    ("CharacterInfo", 4, "2주"),
    ("CharacterInfo", 5, "이전"),
    ("CharacterInfo", 6, "연락"),
    ("CharacterInfo", 7, "다음"),
    ("CharacterInfo", 8, "추가 정보"),
    ("CharacterInfo", 9, "활동 중인 회원"),
    ("CharacterInfo", 10, "선택 장비:"),
    ("CharacterInfo", 11, "의료 보증금 필요"),
    ("InsContractText", 0, "이전"),
    ("InsContractText", 1, "다음"),
    ("InsContractText", 2, "승인"),
    ("InsContractText", 3, "초기화"),
    ("InsInfoText", 0, "이전"),
    ("InsInfoText", 1, "다음"),
    ("ItemPickupHelpPopup", 0, "확인"),
    ("ItemPickupHelpPopup", 1, "위로 스크롤"),
    ("ItemPickupHelpPopup", 2, "모두 선택"),
    ("ItemPickupHelpPopup", 3, "아래로 스크롤"),
    ("ItemPickupHelpPopup", 4, "취소"),
    ("LargeTacticalStr", 0, "이 구역에서 패배했습니다!"),
    ("LargeTacticalStr", 1, "적은 팀의 영혼에 자비를 베풀지 않고 여러분 모두를 집어삼켰습니다!"),
    ("LargeTacticalStr", 2, "의식을 잃은 팀원들이 포로로 붙잡혔습니다!"),
    ("LargeTacticalStr", 3, "팀원들이 적에게 포로로 잡혔습니다."),

    # M.E.R.C.
    ("MercAccountText", 0, "승인"),
    ("MercAccountText", 1, "홈"),
    ("MercAccountText", 2, "계정 번호:"),
    ("MercAccountText", 3, "용병"),
    ("MercAccountText", 4, "일수"),
    ("MercAccountText", 5, "일당"),
    ("MercAccountText", 6, "청구액"),
    ("MercAccountText", 7, "합계:"),
    ("MercAccountText", 8, "정말 %s의 지급을 승인하시겠습니까?"),
    ("MercHomePageText", 0, "설립자 겸 소유주 스펙 T. 클라인"),
    ("MercHomePageText", 1, "계정을 개설하려면 여기를 누르십시오"),
    ("MercHomePageText", 2, "계정을 보려면 여기를 누르십시오"),
    ("MercHomePageText", 3, "파일을 보려면 여기를 누르십시오"),
    ("MercHomePageText", 4, "Speck Com v3.2"),
    ("MercInfo", 0, "이전"),
    ("MercInfo", 1, "고용"),
    ("MercInfo", 2, "다음"),
    ("MercInfo", 3, "추가 정보"),
    ("MercInfo", 4, "홈"),
    ("MercInfo", 5, "고용됨"),
    ("MercInfo", 6, "급여:"),
    ("MercInfo", 7, "일당"),
    ("MercInfo", 8, "사망"),
    ("MercInfo", 9, "용병을 너무 많이 고용하려는 것 같습니다. 최대 인원은 18명입니다."),
    ("MercInfo", 10, "고용 불가"),
    ("MercNoAccountText", 0, "계정 개설"),
    ("MercNoAccountText", 1, "취소"),
    ("MercNoAccountText", 2, "계정이 없습니다. 계정을 개설하시겠습니까?"),
]


def get_value(data: dict, key: str, index: int | None) -> str:
    if key not in data:
        raise KeyError(f"Missing translation key: {key}")
    value = data[key]
    if index is None:
        if not isinstance(value, str):
            raise TypeError(f"{key} is not a string")
        return value
    if not isinstance(value, list):
        raise TypeError(f"{key} is not a list")
    if index >= len(value):
        raise IndexError(f"{key}[{index}] out of range (len={len(value)})")
    if not isinstance(value[index], str):
        raise TypeError(f"{key}[{index}] is not a string")
    return value[index]


def set_value(data: dict, key: str, index: int | None, value: str) -> None:
    if index is None:
        data[key] = value
    else:
        data[key][index] = value


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

    TARGET.write_text(
        json.dumps(data, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
    )
    print(f"Applied Korean UI batch 001: {changed}/{len(BATCH)} entries changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
