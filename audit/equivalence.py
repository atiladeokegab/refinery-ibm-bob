from __future__ import annotations
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from audit.models import SemanticChange
from audit.pic_boundary import derive_boundaries


@dataclass
class EquivalenceResult:
    status: str  # "PASS" | "FLAGGED" | "SKIPPED" | "COMPILE_ERROR"
    detail: str = ""
    semantic_changes: list[SemanticChange] = field(default_factory=list)
    divergence_field: str | None = None
    divergence_boundary: str | None = None


def _has_file_section(source: str) -> bool:
    return bool(re.search(r"\bFILE\s+SECTION\b", source, re.IGNORECASE))


def _has_using_clause(source: str) -> bool:
    return bool(re.search(r"\bPROCEDURE\s+DIVISION\s+USING\b", source, re.IGNORECASE))

def _has_linkage_section(source: str) -> bool:
    return bool(re.search(r"\bLINKAGE\s+SECTION\b", source, re.IGNORECASE))


def _cobc_available() -> bool:
    """Return True if cobc is reachable (native or via WSL on Windows)."""
    cmd = ["wsl", "cobc", "--version"] if sys.platform == "win32" else ["cobc", "--version"]
    try:
        return subprocess.run(cmd, capture_output=True).returncode == 0
    except FileNotFoundError:
        return False


def _wsl_path(win_path: Path) -> str:
    """Convert a Windows path to its WSL /mnt/... equivalent."""
    p = str(win_path).replace("\\", "/")
    if len(p) >= 2 and p[1] == ":":
        p = f"/mnt/{p[0].lower()}{p[2:]}"
    return p


def _compile(source_path: Path, out_path: Path, copybook_dirs: list[Path] | None = None) -> tuple[bool, str]:
    if sys.platform == "win32":
        wsl_src = _wsl_path(source_path)
        wsl_out = _wsl_path(out_path.parent) + "/" + out_path.name
        cmd = ["wsl", "cobc", "-x", wsl_src, "-o", wsl_out]
        for d in (copybook_dirs or []):
            cmd += ["-I", _wsl_path(d)]
    else:
        cmd = ["cobc", "-x", str(source_path), "-o", str(out_path)]
        for d in (copybook_dirs or []):
            cmd += ["-I", str(d)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr


def _find_ws_numeric_inputs(source: str) -> list[tuple[str, str, str]]:
    """Return (field_name, pic, usage) for 01-level WORKING-STORAGE numeric fields.

    usage is the USAGE clause value if present: "COMP", "COMP-3", "COMP-4", or "".
    """
    ws_match = re.search(
        r"WORKING-STORAGE\s+SECTION\s*\.(.*?)(?=\bPROCEDURE\s+DIVISION\b)",
        source, re.IGNORECASE | re.DOTALL,
    )
    if not ws_match:
        return []
    ws = ws_match.group(1)
    fields = []
    for m in re.finditer(
        r"\b01\s+([\w-]+)\s+PIC(?:TURE)?(?:\s+IS)?\s+([S9V()\d]+)",
        ws, re.IGNORECASE,
    ):
        rest = ws[m.end():m.end() + 80]
        if re.search(r"\bVALUE\b", rest, re.IGNORECASE):
            continue
        # Look for USAGE clause in surrounding field context
        field_start = ws.rfind("\n", 0, m.start())
        context = ws[max(0, field_start):m.end() + 80]
        usage = ""
        usage_m = re.search(r"\b(COMP-3|COMP-4|COMP)\b", context, re.IGNORECASE)
        if usage_m:
            usage = usage_m.group(1).upper()
        fields.append((m.group(1), m.group(2).upper(), usage))
    return fields


def _inject_test_values(source: str, field_values: dict[str, str]) -> str:
    """Insert MOVE statements at the start of the first paragraph body."""
    if not field_values:
        return source
    moves = "\n".join(
        f"           MOVE {v} TO {name}" for name, v in field_values.items()
    )
    proc_pos = re.search(r"\bPROCEDURE\s+DIVISION\b", source, re.IGNORECASE)
    if not proc_pos:
        return source
    after_proc = source[proc_pos.end():]
    para_m = re.search(r"\n(\s{4,11}[\w-]+\.\s*\n)", after_proc)
    if not para_m:
        return source
    insert_at = proc_pos.end() + para_m.end()
    return source[:insert_at] + moves + "\n" + source[insert_at:]


def _run_binary(binary_path: Path) -> tuple[str, int]:
    try:
        if sys.platform == "win32":
            wsl_bin = _wsl_path(binary_path)
            cmd = ["wsl", wsl_bin]
        else:
            cmd = [str(binary_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.stdout, result.returncode
    except subprocess.TimeoutExpired:
        return "", -1


_BOUNDARY_ROUNDS = [
    ("ZERO",     lambda b: "0"),
    ("MIN",      lambda b: b.min_val),
    ("MAX",      lambda b: b.max_val),
    ("OVERFLOW", lambda b: b.overflow_val),
]

# Uniform safe values injected into every field simultaneously.
# These mid-range values pass typical validation guards (non-zero, within normal
# business ranges) where PIC-derived boundary values (0, max, overflow) would not.
_SAFE_ROUNDS = [("1",), ("50",), ("99",)]


def _run_round(
    orig_src: str,
    mod_src: str,
    field_values: dict[str, str],
    label: str,
    tmp: Path,
    copybook_dirs: list[Path] | None = None,
) -> EquivalenceResult | None:
    """Compile, run, and compare one round. Returns None if equivalent."""
    orig_patched = _inject_test_values(orig_src, field_values)
    mod_patched = _inject_test_values(mod_src, field_values)

    orig_src_path = tmp / f"orig_{label}.cob"
    mod_src_path = tmp / f"mod_{label}.cob"
    orig_bin = tmp / f"orig_bin_{label}"
    mod_bin = tmp / f"mod_bin_{label}"

    orig_src_path.write_text(orig_patched, encoding="utf-8")
    mod_src_path.write_text(mod_patched, encoding="utf-8")

    ok, err = _compile(orig_src_path, orig_bin, copybook_dirs)
    if not ok:
        return EquivalenceResult(
            status="COMPILE_ERROR",
            detail=f"Original failed to compile (round={label}):\n{err}",
            semantic_changes=[SemanticChange(
                change_type="COMPILE_ERROR", location="original",
                original="", modified=err[:500], severity="HIGH",
            )],
        )

    ok, err = _compile(mod_src_path, mod_bin, copybook_dirs)
    if not ok:
        return EquivalenceResult(
            status="COMPILE_ERROR",
            detail=f"Modified failed to compile (round={label}):\n{err}",
            semantic_changes=[SemanticChange(
                change_type="COMPILE_ERROR", location="modified",
                original="", modified=err[:500], severity="HIGH",
            )],
        )

    orig_out, _ = _run_binary(orig_bin)
    mod_out, _ = _run_binary(mod_bin)

    if orig_out == mod_out:
        return None

    orig_lines = orig_out.splitlines()
    mod_lines = mod_out.splitlines()
    diff_lines = [f"input={label}"]
    for i, (o, m) in enumerate(zip(orig_lines, mod_lines)):
        if o != m:
            diff_lines.append(f"  Line {i+1}: original={repr(o)}  modified={repr(m)}")
    if len(orig_lines) != len(mod_lines):
        diff_lines.append(
            f"  Output length: original={len(orig_lines)} lines, "
            f"modified={len(mod_lines)} lines"
        )
    return EquivalenceResult(
        status="FLAGGED",
        detail="\n".join(diff_lines),
        semantic_changes=[SemanticChange(
            change_type="OUTPUT_DIVERGENCE",
            location="PROGRAM",
            original=orig_out[:300],
            modified=mod_out[:300],
            severity="HIGH",
        )],
    )


_COPYBOOK_DIR_NAMES = {"COPYBOOK", "COPYBOOKS", "COPY", "COPYLIB", "COPYLIB-MVS", "CPY", "cpy", "copy", "copybooks"}


def _find_copybook_dirs(repo_root: Path) -> list[Path]:
    """Walk repo_root and return all directories whose name looks like a copybook store."""
    found = []
    for d in repo_root.rglob("*"):
        if d.is_dir() and d.name in _COPYBOOK_DIR_NAMES:
            found.append(d)
    return found


def check_equivalence(
    original: Path,
    modified: Path,
    repo_root: Path | None = None,
    copybook_dirs: list[Path] | None = None,
) -> EquivalenceResult:
    if not _cobc_available():
        return EquivalenceResult(
            status="SKIPPED", detail="GnuCOBOL (cobc) not available"
        )

    orig_src = Path(original).read_text(encoding="utf-8")
    mod_src  = Path(modified).read_text(encoding="utf-8")

    if _has_file_section(orig_src) or _has_file_section(mod_src):
        return EquivalenceResult(
            status="SKIPPED",
            detail="FILE SECTION programs not supported — equivalence check skipped",
        )

    if _has_using_clause(orig_src) or _has_using_clause(mod_src) \
            or _has_linkage_section(orig_src) or _has_linkage_section(mod_src):
        return EquivalenceResult(
            status="SKIPPED",
            detail="Subprogram (LINKAGE SECTION / PROCEDURE DIVISION USING) — equivalence check skipped",
        )


    # Build copybook search path: caller-supplied dirs + auto-detected from repo_root
    cb_dirs: list[Path] = list(copybook_dirs or [])
    if repo_root is not None:
        cb_dirs += _find_copybook_dirs(Path(repo_root))

    ws_fields = _find_ws_numeric_inputs(orig_src)
    boundaries = {name: derive_boundaries(pic, usage) for name, pic, usage in ws_fields}

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Pass 1: PIC-aware boundary rounds + uniform safe rounds.
        # Boundary rounds (ZERO/MIN/MAX/OVERFLOW) target field-type extremes.
        # Safe rounds use mid-range uniform values that pass typical validation
        # guards the boundary values cannot reach (e.g. annual-rate ≤ 99.9999).
        pass1_result: EquivalenceResult | None = None
        all_pass1: list[tuple[str, dict[str, str]]] = []
        for round_name, val_fn in _BOUNDARY_ROUNDS:
            all_pass1.append((round_name, {name: val_fn(b) for name, b in boundaries.items()}))
        for (safe_val,) in _SAFE_ROUNDS:
            all_pass1.append((safe_val, {name: safe_val for name in boundaries}))

        for round_name, field_values in all_pass1:
            result = _run_round(orig_src, mod_src, field_values, round_name, tmp, cb_dirs)
            if result is not None:
                if result.status == "COMPILE_ERROR":
                    return result
                pass1_result = result
                break

        if pass1_result is None:
            return EquivalenceResult(status="PASS")

        # Pass 2: per-field isolation — find which field at which boundary diverges
        for field_name, boundary in boundaries.items():
            for round_name, val_fn in _BOUNDARY_ROUNDS:
                test_val = val_fn(boundary)
                field_values = {
                    n: (test_val if n == field_name else boundaries[n].nominal_val)
                    for n in boundaries
                }
                result = _run_round(
                    orig_src, mod_src, field_values,
                    f"iso_{field_name}_{round_name}", tmp, cb_dirs,
                )
                if result is not None and result.status != "COMPILE_ERROR":
                    result.divergence_field = field_name
                    result.divergence_boundary = round_name
                    return result

        # Pass 1 diverged but isolation could not pinpoint a single field
        pass1_result.detail += "\n[isolation: could not pinpoint divergence to a single field]"
        return pass1_result
