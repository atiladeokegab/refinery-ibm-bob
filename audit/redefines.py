from __future__ import annotations

import re
from dataclasses import dataclass

from audit.models import SemanticChange

_FIELD_RE = re.compile(
    r"^\s*(\d{2})\s+([\w-]+)(.*?)$",
    re.IGNORECASE | re.MULTILINE,
)
_REDEFINES_RE = re.compile(r"\bREDEFINES\s+([\w-]+)", re.IGNORECASE)
_PIC_RE = re.compile(r"\bPIC(?:TURE)?\s+(?:IS\s+)?([S9XAV()\d\/]+)", re.IGNORECASE)
_COMP3_RE = re.compile(r"\bCOMP-3\b", re.IGNORECASE)
_COMP_RE = re.compile(r"\bCOMP\b(?![-\d])", re.IGNORECASE)


@dataclass
class FieldInfo:
    name: str
    level: int
    offset: int
    length: int
    redefines_target: str | None = None


def _pic_byte_length(pic: str, is_comp3: bool = False, is_comp: bool = False) -> int:
    upper = pic.upper()
    expanded = re.sub(
        r"([X9AS])\((\d+)\)", lambda m: m.group(1) * int(m.group(2)), upper
    )
    digits = len(re.findall(r"9", expanded))
    alpha = len(re.findall(r"[XA]", expanded))
    if is_comp3:
        return max(1, (digits + 2) // 2)
    if is_comp:
        if digits <= 4:
            return 2
        if digits <= 9:
            return 4
        return 8
    return max(1, digits + alpha)


def build_offset_map(source: str) -> dict[str, FieldInfo]:
    ws_match = re.search(
        r"WORKING-STORAGE\s+SECTION\s*\.(.*?)"
        r"(?=\b(?:FILE|LINKAGE|LOCAL-STORAGE|PROCEDURE)\s+(?:SECTION|DIVISION)\b|\Z)",
        source,
        re.IGNORECASE | re.DOTALL,
    )
    if not ws_match:
        return {}

    ws_text = ws_match.group(1)
    fields: dict[str, FieldInfo] = {}
    running_offset = 0

    for m in _FIELD_RE.finditer(ws_text):
        level = int(m.group(1))
        name = m.group(2).upper()
        rest = m.group(3)

        if level == 88:
            continue

        pic_m = _PIC_RE.search(rest)
        if not pic_m:
            continue  # group item (no PIC) — group-level REDEFINES excluded by design in v1

        pic = pic_m.group(1)
        is_comp3 = bool(_COMP3_RE.search(rest))
        is_comp = bool(_COMP_RE.search(rest)) and not is_comp3
        length = _pic_byte_length(pic, is_comp3, is_comp)

        redefines_m = _REDEFINES_RE.search(rest)
        redefines_target = redefines_m.group(1).upper() if redefines_m else None

        if redefines_target and redefines_target in fields:
            offset = fields[redefines_target].offset
        else:
            offset = running_offset
            running_offset += length

        fields[name] = FieldInfo(
            name=name,
            level=level,
            offset=offset,
            length=length,
            redefines_target=redefines_target,
        )

    return fields


def check_redefines(orig_src: str, mod_src: str) -> list[SemanticChange]:
    orig_map = build_offset_map(orig_src)
    mod_map = build_offset_map(mod_src)
    changes: list[SemanticChange] = []

    for name, orig_info in orig_map.items():
        if orig_info.redefines_target is None:
            continue
        if name not in mod_map:
            changes.append(SemanticChange(
                change_type="REDEFINES_REMOVED",
                location=name,
                original=name,
                modified="(removed)",
                severity="HIGH",
            ))
            continue
        mod_info = mod_map[name]
        if orig_info.offset != mod_info.offset or orig_info.length != mod_info.length:
            changes.append(SemanticChange(
                change_type="REDEFINES_OFFSET",
                location=name,
                original=f"offset={orig_info.offset} len={orig_info.length}",
                modified=f"offset={mod_info.offset} len={mod_info.length}",
                severity="HIGH",
            ))

    return changes
