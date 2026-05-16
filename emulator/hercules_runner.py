import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

HERCULES_BIN = "hercules"  # must be on PATH; override via subclass or env var


@dataclass
class HerculesResult:
    instruction_count: int
    elapsed_cycles: float
    memory_pages_touched: int
    exit_code: int
    raw_output: str


class HerculesRunner:
    def __init__(
        self,
        conf_template: Path | str,
        jcl_template: Path | str,
        timeout: int = 60,
    ):
        self.conf_template = Path(conf_template)
        self.jcl_template = Path(jcl_template)
        self.timeout = timeout

    def run(self, cobol_program: Path | str) -> dict:
        cobol_program = Path(cobol_program)
        workdir = Path(tempfile.mkdtemp(prefix="herc_"))
        try:
            result = self._execute(cobol_program, workdir)
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
        return {
            "instruction_count": result.instruction_count,
            "elapsed_cycles": result.elapsed_cycles,
            "memory_pages_touched": result.memory_pages_touched,
            "exit_code": result.exit_code,
        }

    def _execute(self, cobol_program: Path, workdir: Path) -> HerculesResult:
        conf_path = self._prepare_conf(workdir)
        jcl_path = self._prepare_jcl(workdir, cobol_program)

        try:
            proc = subprocess.run(
                [HERCULES_BIN, "-f", str(conf_path)],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=workdir,
            )
        except subprocess.TimeoutExpired:
            return HerculesResult(0, 0.0, 0, -1, "TIMEOUT")
        except FileNotFoundError:
            return HerculesResult(0, 0.0, 0, -2, "HERCULES_NOT_FOUND")

        return self._parse_output(proc.stdout + proc.stderr, proc.returncode)

    def _prepare_conf(self, workdir: Path) -> Path:
        text = self.conf_template.read_text()
        text = text.replace("{{WORKDIR}}", str(workdir))
        path = workdir / "hercules.conf"
        path.write_text(text)
        return path

    def _prepare_jcl(self, workdir: Path, cobol_program: Path) -> Path:
        text = self.jcl_template.read_text()
        text = text.replace("{{PROGRAM}}", str(cobol_program))
        path = workdir / "job.jcl"
        path.write_text(text)
        return path

    def _parse_output(self, output: str, returncode: int) -> HerculesResult:
        # Expected HERCULES counter lines in stdout:
        #   INSTCOUNT: 482930
        #   ELAPSED:   0.342
        #   PAGES:     128
        instruction_count = 0
        elapsed_cycles = 0.0
        memory_pages = 0

        for line in output.splitlines():
            stripped = line.strip()
            if stripped.startswith("INSTCOUNT:"):
                try:
                    instruction_count = int(stripped.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif stripped.startswith("ELAPSED:"):
                try:
                    elapsed_cycles = float(stripped.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif stripped.startswith("PAGES:"):
                try:
                    memory_pages = int(stripped.split(":", 1)[1].strip())
                except ValueError:
                    pass

        return HerculesResult(
            instruction_count=instruction_count,
            elapsed_cycles=elapsed_cycles,
            memory_pages_touched=memory_pages,
            exit_code=returncode,
            raw_output=output,
        )
