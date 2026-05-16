"""JCLBuilder — applies JCL parameter actions (A15-A24) to a JCL string."""

import re

_REGION_STEPS = ["128M", "256M", "512M", "1024M", "2048M", "4096M"]
_CLASS_CYCLE = ["A", "B", "C"]


class JCLBuilder:
    """Transforms a JCL string by applying a single parameter action."""

    def apply(self, jcl: str, action_id: int) -> str:
        handlers = {
            15: self._region_increase,
            16: self._region_decrease,
            17: self._time_nolimit,
            18: self._sortwork_increase,
            19: self._class_change,
            20: self._dfsms_compress,
            21: self._bufno_tune,
            22: self._hiperspace_enable,
            23: self._sortwork_disp_reuse,
            24: lambda j: j,  # ROLLBACK_JCL — handled at env level
        }
        handler = handlers.get(action_id)
        if handler is None:
            raise ValueError(f"action_id {action_id} is not a JCL parameter action (expected 15-24)")
        return handler(jcl)

    # ── A15: REGION_INCREASE ──────────────────────────────────────────────────

    def _region_increase(self, jcl: str) -> str:
        def bump_up(m: re.Match) -> str:
            val = m.group(1)
            try:
                idx = _REGION_STEPS.index(val)
            except ValueError:
                return m.group(0)
            new_val = _REGION_STEPS[min(idx + 1, len(_REGION_STEPS) - 1)]
            return f"REGION={new_val}"

        result = re.sub(r"REGION=(\d+M)", bump_up, jcl, flags=re.IGNORECASE)
        if result == jcl:
            # No REGION found — inject on first EXEC stmt
            result = re.sub(
                r"(//\w+\s+EXEC\s+\S+)",
                r"\1,REGION=1024M",
                jcl,
                count=1,
            )
        return result

    # ── A16: REGION_DECREASE ──────────────────────────────────────────────────

    def _region_decrease(self, jcl: str) -> str:
        def bump_down(m: re.Match) -> str:
            val = m.group(1)
            try:
                idx = _REGION_STEPS.index(val)
            except ValueError:
                return m.group(0)
            new_val = _REGION_STEPS[max(idx - 1, 0)]
            return f"REGION={new_val}"

        return re.sub(r"REGION=(\d+M)", bump_down, jcl, flags=re.IGNORECASE)

    # ── A17: TIME_NOLIMIT ─────────────────────────────────────────────────────

    def _time_nolimit(self, jcl: str) -> str:
        result = re.sub(r"TIME=\S+", "TIME=NOLIMIT", jcl, flags=re.IGNORECASE)
        if result == jcl:
            result = re.sub(
                r"(//\w+\s+EXEC\s+\S+)",
                r"\1,TIME=NOLIMIT",
                jcl,
                count=1,
            )
        return result

    # ── A18: SORTWORK_INCREASE ────────────────────────────────────────────────

    def _sortwork_increase(self, jcl: str) -> str:
        def bump_space(m: re.Match) -> str:
            unit = m.group(1)
            pri = int(m.group(2))
            sec = int(m.group(3))
            return f"SPACE=({unit},({pri * 2},{sec * 2}))"

        if re.search(r"SORTW", jcl, re.IGNORECASE):
            return re.sub(
                r"SPACE=\((\w+),\((\d+),(\d+)\)\)",
                bump_space,
                jcl,
                flags=re.IGNORECASE,
            )
        # No SORTWORK DD — append one before //GO step
        sortwork_dd = "//SORTWK01 DD UNIT=SYSDA,SPACE=(CYL,(20,10))\n"
        return re.sub(r"(//GO\s+EXEC)", sortwork_dd + r"\1", jcl, count=1)

    # ── A19: CLASS_CHANGE ─────────────────────────────────────────────────────

    def _class_change(self, jcl: str) -> str:
        def cycle_class(m: re.Match) -> str:
            current = m.group(1).upper()
            try:
                idx = _CLASS_CYCLE.index(current)
            except ValueError:
                return m.group(0)
            return f"CLASS={_CLASS_CYCLE[(idx + 1) % len(_CLASS_CYCLE)]}"

        return re.sub(r"CLASS=([A-Z])\b", cycle_class, jcl, flags=re.IGNORECASE)

    # ── A20: DFSMS_COMPRESS ───────────────────────────────────────────────────

    def _dfsms_compress(self, jcl: str) -> str:
        # Add DATACLAS=COMPRESS to the first output DD with a DSN
        def add_dataclas(m: re.Match) -> str:
            line = m.group(0)
            if "DATACLAS=" not in line.upper():
                line = line.rstrip() + ",DATACLAS=COMPRESS\n"
            return line

        return re.sub(
            r"//\w+\s+DD\s+DSN=[^,\n]+.*\n",
            add_dataclas,
            jcl,
            count=2,
        )

    # ── A21: BUFNO_TUNE ───────────────────────────────────────────────────────

    def _bufno_tune(self, jcl: str) -> str:
        # Add DCB=(BUFNO=20) to sequential DDs that have DSN= but no BUFNO yet
        def add_bufno(m: re.Match) -> str:
            line = m.group(0)
            if "BUFNO" in line.upper():
                return line
            # Append DCB override
            return line.rstrip() + ",DCB=(BUFNO=20)\n"

        return re.sub(
            r"//\w+\s+DD\s+DSN=[^,\n]+,DISP=SHR.*\n",
            add_bufno,
            jcl,
        )

    # ── A22: HIPERSPACE_ENABLE ────────────────────────────────────────────────

    def _hiperspace_enable(self, jcl: str) -> str:
        if "HIPERSPACE" in jcl.upper():
            return jcl
        hiperspace_dd = "//HIPERSPC DD SPACE=(CYL,(1,1)),UNIT=SYSDA\n"
        # Insert after the last //GO EXEC or at end of file
        result = re.sub(
            r"(//GO\s+EXEC\s+PGM=\w+\n)",
            r"\1" + hiperspace_dd,
            jcl,
            count=1,
        )
        if result == jcl:
            result = jcl.rstrip() + "\n" + hiperspace_dd
        return result

    # ── A23: SORTWORK_DISP_REUSE ──────────────────────────────────────────────

    def _sortwork_disp_reuse(self, jcl: str) -> str:
        # On any SORTW* DD, replace or add DISP=(NEW,DELETE) for temp reuse
        lines = []
        for line in jcl.splitlines(keepends=True):
            if re.match(r"//SORTW", line, re.IGNORECASE):
                line = re.sub(r"DISP=\([^)]+\)", "DISP=(NEW,DELETE)", line)
                line = re.sub(r"DISP=\w+", "DISP=(NEW,DELETE)", line)
                if "DISP=" not in line.upper():
                    line = line.rstrip() + ",DISP=(NEW,DELETE)\n"
            lines.append(line)
        return "".join(lines)
