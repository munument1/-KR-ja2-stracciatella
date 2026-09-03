#!/usr/bin/env python3
"""Import vanilla-compatible Korean BinaryData/NPCData from the legacy patch.

The Simplified Chinese localization bundled with Stracciatella is used only as a
vanilla layout reference (filename + exact byte size).  Only files from
`Patch/Data` in the legacy Korean repository are considered.  `Patch/Data-1.13`
is never read by this tool.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def index_files(root: Path) -> dict[str, Path]:
    return {
        p.name.lower(): p
        for p in root.iterdir()
        if p.is_file() and p.suffix.lower() == ".edt"
    }


def import_group(
    *,
    group: str,
    reference_dir: Path,
    legacy_dir: Path,
    output_dir: Path,
) -> dict:
    if not reference_dir.is_dir():
        raise SystemExit(f"Missing Stracciatella reference directory: {reference_dir}")
    if not legacy_dir.is_dir():
        raise SystemExit(f"Missing legacy Korean directory: {legacy_dir}")

    reference = index_files(reference_dir)
    legacy = index_files(legacy_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    imported: list[dict] = []
    missing_legacy: list[str] = []
    size_mismatch: list[dict] = []

    for key, ref in sorted(reference.items()):
        old = legacy.get(key)
        if old is None:
            missing_legacy.append(ref.name)
            continue

        ref_size = ref.stat().st_size
        old_size = old.stat().st_size
        if ref_size != old_size:
            size_mismatch.append(
                {
                    "file": ref.name,
                    "reference_size": ref_size,
                    "legacy_size": old_size,
                }
            )
            continue

        dest = output_dir / ref.name
        shutil.copyfile(old, dest)
        if dest.stat().st_size != ref_size or sha256(dest) != sha256(old):
            raise SystemExit(f"Copy verification failed for {old} -> {dest}")

        imported.append(
            {
                "file": ref.name,
                "size": ref_size,
                "sha256": sha256(dest),
            }
        )

    legacy_only = sorted(p.name for k, p in legacy.items() if k not in reference)

    print(f"[{group}] reference EDT files: {len(reference)}")
    print(f"[{group}] legacy EDT files: {len(legacy)}")
    print(f"[{group}] imported exact matches: {len(imported)}")
    print(f"[{group}] missing in legacy: {len(missing_legacy)}")
    print(f"[{group}] size mismatches skipped: {len(size_mismatch)}")
    print(f"[{group}] legacy-only files excluded: {len(legacy_only)}")
    for item in size_mismatch:
        print(
            f"  SKIP SIZE {item['file']}: legacy={item['legacy_size']} "
            f"vanilla-reference={item['reference_size']}"
        )
    for name in legacy_only:
        print(f"  EXCLUDE LEGACY-ONLY {name}")

    return {
        "group": group,
        "reference_count": len(reference),
        "legacy_count": len(legacy),
        "imported_count": len(imported),
        "imported": imported,
        "missing_legacy": missing_legacy,
        "size_mismatch": size_mismatch,
        "legacy_only": legacy_only,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy-root", type=Path, required=True)
    parser.add_argument(
        "--reference-root",
        type=Path,
        default=Path("assets/mods/simplified-chinese-localization/data"),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("assets/mods/korean-localization/data"),
    )
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    # Deliberately use only Patch/Data.  Never fall back to Data-1.13.
    legacy_data = args.legacy_root / "Patch" / "Data"

    reports = [
        import_group(
            group="BinaryData",
            reference_dir=args.reference_root / "BinaryData",
            legacy_dir=legacy_data / "BinaryData",
            output_dir=args.output_root / "BinaryData",
        ),
        import_group(
            group="NPCData",
            reference_dir=args.reference_root / "npcdata",
            legacy_dir=legacy_data / "NPCData",
            output_dir=args.output_root / "NPCData",
        ),
    ]

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps({"groups": reports}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    if not any(r["imported_count"] for r in reports):
        raise SystemExit("No vanilla-compatible Korean EDT resources were imported")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
