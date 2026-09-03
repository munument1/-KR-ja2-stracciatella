#!/usr/bin/env python3
"""Patch Korean-only stat-change sentence order.

The vanilla formatter composes English fragments as:
  <name> <lost/gained> <number> <point(s)/level(s)> <stat>

That word order cannot produce natural Korean.  This script adds a tiny
isKoreanVersion() helper and a Korean-only formatter while leaving every other
language on the original code path.  It is idempotent so CI can run it on every
translation batch.
"""

from __future__ import annotations

from pathlib import Path


def replace_once_or_verify(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        print(f"OK already patched: {label}")
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one {label} target in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"Patched: {label}")


def main() -> int:
    game_res_h = Path("src/game/GameRes.h")
    game_res_cc = Path("src/game/GameRes.cc")
    campaign_cc = Path("src/game/Tactical/Campaign.cc")

    replace_once_or_verify(
        game_res_h,
        """/** Check if this is Chinese version of the game. */
bool isChineseVersion();

/** Get major map version. */
""",
        """/** Check if this is Chinese version of the game. */
bool isChineseVersion();

/** Check if this is Korean version of the game. */
bool isKoreanVersion();

/** Get major map version. */
""",
        "GameRes.h Korean version declaration",
    )

    replace_once_or_verify(
        game_res_cc,
        """/** Check if this is Chinese version of the game. */
bool isChineseVersion()
{
\treturn s_gameVersion == GameVersion::SIMPLIFIED_CHINESE;
}

/** Get major map version. */
""",
        """/** Check if this is Chinese version of the game. */
bool isChineseVersion()
{
\treturn s_gameVersion == GameVersion::SIMPLIFIED_CHINESE;
}

/** Check if this is Korean version of the game. */
bool isKoreanVersion()
{
\treturn s_gameVersion == GameVersion::KOREAN;
}

/** Get major map version. */
""",
        "GameRes.cc Korean version helper",
    )

    replace_once_or_verify(
        campaign_cc,
        """#include \"GameSettings.h\"
#include \"Assignments.h\"
""",
        """#include \"GameSettings.h\"
#include \"GameRes.h\"
#include \"Assignments.h\"
""",
        "Campaign.cc GameRes include",
    )

    replace_once_or_verify(
        campaign_cc,
        """\treturn ST::format(\"{} {} {} {} {}\", name,
\t\t\tsPreStatBuildString[fIncrease ? 1 : 0], absPointsChanged,
\t\t\tsPreStatBuildString[ubStringIndex],
\t\t\tsStatGainStrings[ubStat - FIRST_CHANGEABLE_STAT]);
""",
        """\tif (isKoreanVersion())
\t{
\t\treturn ST::format(\"{}: {} {}{} {}\", name,
\t\t\tsStatGainStrings[ubStat - FIRST_CHANGEABLE_STAT], absPointsChanged,
\t\t\tsPreStatBuildString[ubStringIndex],
\t\t\tsPreStatBuildString[fIncrease ? 1 : 0]);
\t}

\treturn ST::format(\"{} {} {} {} {}\", name,
\t\t\tsPreStatBuildString[fIncrease ? 1 : 0], absPointsChanged,
\t\t\tsPreStatBuildString[ubStringIndex],
\t\t\tsStatGainStrings[ubStat - FIRST_CHANGEABLE_STAT]);
""",
        "Campaign.cc Korean stat-change formatter",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
