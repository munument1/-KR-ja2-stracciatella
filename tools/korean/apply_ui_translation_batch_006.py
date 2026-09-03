#!/usr/bin/env python3
"""Apply Korean UI translation batch 006.

Focus: map movement/inventory UI, militia, noise, pause/personnel and repair
screens. Common pMessageStrings are kept for the next batch so their mixed
placeholder-heavy messages can be reviewed separately.
"""

from __future__ import annotations

import json
from apply_ui_translation_batch_001 import PLACEHOLDER_RE, TARGET, get_value, set_value

RANGES: list[tuple[str, int, list[str]]] = [
    ("pMapErrorString", 0, [
        "잠든 용병이 있는 분대는 이동할 수 없습니다.",
        "먼저 분대를 지상으로 이동시키십시오.",
        "이동 명령을 내릴 수 없습니다. 적대 구역입니다!",
        "이동하려면 용병을 분대나 차량에 배치해야 합니다.",
        "아직 팀원이 없습니다.",
        "용병이 명령을 수행할 수 없습니다.",
        "%s은(는) 이동하려면 호위가 필요합니다. 호위 가능한 용병이 있는 분대에 배치하십시오.",
        "%s은(는) 이동하려면 호위가 필요합니다. 호위 가능한 용병이 있는 분대에 배치하십시오.",
        "용병이 아직 아룰코에 도착하지 않았습니다!",
        "먼저 계약 협상을 해결해야 할 것 같습니다.",
        "",
        "이동 명령을 내릴 수 없습니다. 전투가 진행 중입니다!",
        "%s 구역에서 블러드캣의 매복을 당했습니다!",
        "I16 구역의 블러드캣 소굴로 보이는 곳에 들어왔습니다!",
        "",
        "%s의 SAM 기지가 점령당했습니다.",
        "%s의 광산이 점령당했습니다. 일일 수입이 하루 %s(으)로 감소했습니다.",
        "적이 %s 구역을 저항 없이 점령했습니다.",
        "한 명 이상의 용병을 이 임무에 배치할 수 없었습니다.",
        "%s은(는) %s이(가) 이미 가득 차 합류할 수 없습니다.",
        "%s은(는) 너무 멀리 있어 %s에 합류할 수 없습니다.",
        "%s의 광산이 데이드라나의 군대에 점령당했습니다!",
        "데이드라나의 군대가 %s의 SAM 기지를 침공했습니다.",
        "데이드라나의 군대가 %s을(를) 침공했습니다.",
        "데이드라나의 군대가 %s에서 발견되었습니다.",
        "데이드라나의 군대가 %s을(를) 점령했습니다.",
        "한 명 이상의 용병을 재울 수 없었습니다.",
        "한 명 이상의 용병을 깨울 수 없었습니다.",
        "민병대는 훈련이 끝나기 전까지 나타나지 않습니다.",
        "%s에게는 지금 이동 명령을 내릴 수 없습니다.",
        "마을 경계 밖의 민병대는 다른 구역으로 이동시킬 수 없습니다.",
        "%s에는 민병대를 배치할 수 없습니다.",
        "빈 차량은 이동할 수 없습니다!",
        "%s은(는) 부상이 너무 심해 이동할 수 없습니다!",
        "먼저 박물관을 나가야 합니다!",
        "%s은(는) 사망했습니다!",
        "%s은(는) 이동 중이라 %s(으)로 전환할 수 없습니다.",
        "%s은(는) 그 방향으로 차량에 탑승할 수 없습니다.",
        "%s은(는) %s에 합류할 수 없습니다.",
        "새 용병을 고용하기 전에는 시간을 빠르게 돌릴 수 없습니다!",
        "이 차량은 도로를 통해서만 이동할 수 있습니다!",
        "이동 중인 용병은 재배치할 수 없습니다.",
        "차량의 연료가 바닥났습니다!",
        "%s은(는) 너무 지쳐 이동할 수 없습니다.",
        "탑승자 중 차량을 운전할 수 있는 사람이 없습니다.",
        "이 분대의 한 명 이상이 지금 이동할 수 없습니다.",
        "다른 용병 중 한 명 이상이 지금 이동할 수 없습니다.",
        "차량이 너무 심하게 손상되었습니다!",
        "각 구역에서 민병대를 훈련할 수 있는 용병은 두 명뿐입니다.",
        "로봇은 조종자 없이 이동할 수 없습니다. 같은 분대에 함께 배치하십시오.",
    ]),
    ("pMapInventoryErrorString", 0, [
        "그 용병은 선택할 수 없습니다.",
        "%s은(는) 그 아이템을 가져갈 수 있는 구역에 없습니다.",
        "전투 중에는 아이템을 직접 주워야 합니다.",
        "전투 중에는 아이템을 직접 내려놓아야 합니다.",
        "%s은(는) 그 아이템을 내려놓을 수 있는 구역에 없습니다.",
    ]),
    ("pMapInventoryStrings", 0, ["위치", "총 아이템 수"]),
    ("pMapPlotStrings", 0, [
        "최종 경로를 확정하려면 목적지를 다시 클릭하거나, 다른 구역을 클릭해 경유지를 더 지정하십시오.",
        "이동 경로가 확정되었습니다.",
        "목적지는 변경되지 않았습니다.",
        "이동 경로가 취소되었습니다.",
        "이동 경로가 단축되었습니다.",
    ]),
    ("pMapPopUpInventoryText", 0, ["인벤토리", "나가기"]),
    ("pMapScreenBorderButtonHelpText", 0, [
        "마을 표시 (|W)", "광산 표시 (|M)", "팀과 적 표시 (|T)", "영공 표시 (|A)", "아이템 표시 (|I)", "민병대와 적 표시 (|Z)",
    ]),
    ("pMapScreenBottomFastHelp", 0, [
        "노트북 (|L)", "전술 화면 (|E|s|c)", "옵션 (|O)", "시간 가속 (|+)", "시간 감속 (|-)",
        "이전 메시지 (|U|p)\n이전 페이지 (|P|g|U|p)",
        "다음 메시지 (|D|o|w|n)\n다음 페이지 (|P|g|D|n)",
        "시간 시작/정지 (|S|p|a|c|e)",
    ]),
    ("pMapScreenMouseRegionHelpText", 0, [
        "인물 선택", "용병 임무 배정", "이동 경로 설정", "용병 계약", "용병 제거", "수면",
    ]),
    ("pMapScreenPrevNextCharButtonHelpText", 0, ["이전 용병 (|L|e|f|t)", "다음 용병 (|R|i|g|h|t)"]),
    ("pMapScreenStatusStrings", 0, ["체력", "기력", "사기", "상태", "연료"]),
    ("pMilitiaButtonString", 0, ["자동", "완료"]),
    ("pMilitiaButtonsHelpText", 0, [
        "신병 민병대 집기(오른쪽 클릭)/놓기(왼쪽 클릭)",
        "일반 민병대 집기(오른쪽 클릭)/놓기(왼쪽 클릭)",
        "정예 민병대 집기(오른쪽 클릭)/놓기(왼쪽 클릭)",
        "가용 민병대를 모든 구역에 균등하게 분배",
    ]),
    ("pMilitiaConfirmStrings", 0, [
        "마을 민병대 한 분대를 훈련하는 비용은 $", "비용을 승인하시겠습니까?", "비용을 감당할 수 없습니다.",
        "%s에서 민병대 훈련을 계속하시겠습니까? (%s %d)", "비용 $", "( Y/N )",
        "%d개 구역의 마을 민병대 훈련 비용은 $ %d입니다. %s",
        "이곳에서 민병대를 훈련하는 데 필요한 $%d을(를) 감당할 수 없습니다.",
        "%s의 충성도가 %d%% 이상이어야 민병대 훈련을 계속할 수 있습니다.",
        "%s에서는 더 이상 민병대를 훈련할 수 없습니다.",
    ]),
    ("pMilitiaString", 0, ["민병대", "미배치", "지역에 적대 행위가 진행 중일 때는 민병대를 재배치할 수 없습니다!"]),
    ("pMiscMapScreenMouseRegionHelpText", 0, ["인벤토리 열기 (|E|n|t|e|r)", "아이템 버리기", "인벤토리 닫기 (|E|n|t|e|r)"]),
    ("pMoralStrings", 0, ["최고", "좋음", "안정", "저조", "공황", "나쁨"]),
    ("pMovementMenuStrings", 0, ["%s 구역의 용병 이동", "이동 경로 설정", "취소", "기타"]),
    ("pNewNoiseStr", 0, [
        "%s이(가) %s 소리가 %s에서 나는 것을 들었습니다.",
        "%s이(가) %s 크기의 움직이는 소리를 %s에서 들었습니다.",
        "%s이(가) %s 크기의 삐걱거리는 소리를 %s에서 들었습니다.",
        "%s이(가) %s 크기의 물 튀는 소리를 %s에서 들었습니다.",
        "%s이(가) %s 크기의 충격음을 %s에서 들었습니다.",
        "%s이(가) %s 크기의 폭발음을 %s 쪽에서 들었습니다.",
        "%s이(가) %s 크기의 비명을 %s 쪽에서 들었습니다.",
        "%s이(가) %s 크기의 충격음을 %s 쪽에서 들었습니다.",
        "%s이(가) %s 크기의 충격음을 %s 쪽에서 들었습니다.",
        "%s이(가) %s 크기의 깨지는 소리를 %s에서 들었습니다.",
        "%s이(가) %s 크기의 부서지는 소리를 %s에서 들었습니다.",
    ]),
    ("pNoiseTypeStr", 0, [
        "알 수 없는 소리", "움직이는 소리", "삐걱거림", "물 튀는 소리", "충격음", "총성", "폭발음", "비명", "충격음", "충격음", "깨지는 소리", "부서지는 소리",
    ]),
    ("pNoiseVolStr", 0, ["희미한", "분명한", "큰", "매우 큰"]),
    ("pPOWStrings", 0, ["포로", "??"]),
    ("pPausedGameText", 0, ["게임 일시정지", "게임 재개 (|P|a|u|s|e)", "게임 일시정지 (|P|a|u|s|e)"]),
    ("pPersonelTeamStrings", 0, [
        "현재 팀", "이탈자", "일일 비용:", "최고 비용:", "최저 비용:", "전사:", "해고:", "기타:",
    ]),
    ("pPersonnelCurrentTeamStatsStrings", 0, ["최저", "평균", "최고"]),
    ("pPersonnelDepartedStateStrings", 0, ["전사", "해고", "결혼", "계약 만료", "퇴사"]),
    ("pPersonnelScreenStrings", 0, [
        "의료 보증금:", "남은 계약 기간:", "처치", "지원", "일일 비용:", "현재까지 총비용:", "계약:",
        "현재까지 복무 기간:", "미지급 급여:", "명중률:", "전투 횟수", "부상 횟수", "특기:", "특기 없음",
    ]),
    ("pPersonnelTeamStatsStrings", 0, ["체력", "민첩", "손재주", "힘", "통솔", "지혜", "레벨", "사격", "기계", "폭발", "의술"]),
    ("pRemoveMercStrings", 0, ["용병 제거", "취소"]),
    ("pRepairStrings", 0, ["아이템", "SAM 기지", "취소", "로봇"]),
]

SCALARS: list[tuple[str, str]] = [
    ("pMapScreenBottomText", "현재 잔액"),
    ("pMapScreenJustStartedHelpText", "A.I.M.에서 용병을 고용하십시오. (*힌트* 노트북에 있습니다.)"),
    ("pMercDeadString", "%s은(는) 사망했습니다."),
    ("pNewMailStrings", "새 메일이 도착했습니다..."),
    ("pPersTitleText", "인사 관리"),
    ("pPersonnelString", "용병:"),
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
    print(f"Applied Korean UI batch 006: {changed}/{total} entries changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
