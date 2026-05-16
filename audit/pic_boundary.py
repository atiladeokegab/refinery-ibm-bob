from __future__ import annotations
import re
from dataclasses import dataclass


@dataclass
class PICBoundary:
    pic: str           # normalised PIC string
    max_val: str       # largest valid value as injectable MOVE string
    min_val: str       # "0" for unsigned; negative max for signed
    overflow_val: str  # one beyond max (triggers ON SIZE ERROR)
    nominal_val: str   # safe mid-range for isolation baseline


def derive_boundaries(pic_str: str, usage: str = "") -> PICBoundary:
    """Derive boundary test values from a COBOL PIC string.

    Never raises — returns a safe fallback for unrecognised patterns.
    usage: USAGE clause value if captured separately ("COMP", "COMP-3", "COMP-4", or "").
    """
    pic = _normalise_pic(pic_str)
    usage_upper = usage.upper().strip()

    if not pic:
        return _fallback(pic_str)

    if pic.startswith("X") or pic.startswith("A"):
        return PICBoundary(pic=pic, max_val="SPACES", min_val="SPACES",
                           overflow_val="SPACES", nominal_val="SPACES")

    if "COMP-3" in usage_upper or "COMP3" in usage_upper:
        return _display_boundary(pic)

    if "COMP" in usage_upper:
        return _comp_binary_boundary(pic)

    return _display_boundary(pic)


def _fallback(pic: str) -> PICBoundary:
    return PICBoundary(pic=pic, max_val="1", min_val="0",
                       overflow_val="2", nominal_val="1")


def _normalise_pic(pic: str) -> str:
    """Uppercase, strip, expand shorthand runs (999 -> 9(3), XX -> X(2)), and
    expand lone bare chars not already in N(k) form (9 -> 9(1), X -> X(1))."""
    pic = pic.upper().strip()
    # Expand runs first: 999 -> 9(3), XX -> X(2)
    pic = re.sub(
        r"([9XA])\1+",
        lambda m: f"{m.group(1)}({len(m.group(0))})",
        pic,
    )
    # Expand remaining lone chars not already in N(k) form: 9 -> 9(1), X -> X(1)
    # Use negative lookbehind (?<!\() to avoid touching digits inside existing (N) counts.
    pic = re.sub(r"(?<!\()([9XA])(?!\()", lambda m: f"{m.group(1)}(1)", pic)
    return pic


def _parse_display(pic: str) -> tuple[int, int, bool]:
    """Return (int_digits, dec_digits, is_signed). Returns (0,0,False) if unparseable."""
    is_signed = pic.startswith("S")
    core = pic[1:] if is_signed else pic
    m = re.fullmatch(r"9\((\d+)\)(?:V9\((\d+)\))?", core)
    if not m:
        return 0, 0, is_signed
    return int(m.group(1)), int(m.group(2) or 0), is_signed


def _display_boundary(pic: str) -> PICBoundary:
    int_d, dec_d, signed = _parse_display(pic)
    if int_d == 0:
        return _fallback(pic)

    max_int = 10 ** int_d - 1
    nom_int = max_int // 2

    if dec_d:
        nines = "9" * dec_d
        zeros = "0" * dec_d
        max_val = f"{max_int}.{nines}"
        overflow_val = f"{max_int + 1}.{zeros}"
        nominal_val = f"{nom_int}.{zeros}"
        min_val = f"-{max_val}" if signed else "0"
    else:
        max_val = str(max_int)
        overflow_val = str(max_int + 1)
        nominal_val = str(nom_int)
        min_val = f"-{max_int}" if signed else "0"

    return PICBoundary(pic=pic, max_val=max_val, min_val=min_val,
                       overflow_val=overflow_val, nominal_val=nominal_val)


def _comp_binary_boundary(pic: str) -> PICBoundary:
    int_d, dec_d, signed = _parse_display(pic)
    if int_d == 0:
        return _fallback(pic)

    if int_d <= 4:
        max_int = 32_767
        min_int = -32_768
    elif int_d <= 9:
        max_int = 2_147_483_647
        min_int = -2_147_483_648
    else:
        max_int = 9_223_372_036_854_775_807
        min_int = -9_223_372_036_854_775_808

    max_val = str(max_int)
    overflow_val = str(max_int + 1)
    nominal_val = str(max_int // 2)
    min_val = str(min_int) if signed else "0"

    return PICBoundary(pic=pic, max_val=max_val, min_val=min_val,
                       overflow_val=overflow_val, nominal_val=nominal_val)
