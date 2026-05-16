#!/usr/bin/env python3
"""SMF Phase II diagnostic — run SMFTEST job and dump Phase II output."""
import os, sys, tempfile
from emulator.real_runner import RealHerculesRunner

MVS_PATH = r"C:\Users\okeat\z-optima-rl\emulator\mvs\mvs-tk5"

cobol = (
    "       IDENTIFICATION DIVISION.\n"
    "       PROGRAM-ID. SMFTEST.\n"
    "       DATA DIVISION.\n"
    "       WORKING-STORAGE SECTION.\n"
    "       01 WS-COUNT PIC 9(4) VALUE ZEROS.\n"
    "       PROCEDURE DIVISION.\n"
    "           ADD 1 TO WS-COUNT.\n"
    "           ADD 1 TO WS-COUNT.\n"
    "           STOP RUN.\n"
)

with tempfile.NamedTemporaryFile(suffix=".cob", mode="w", delete=False) as f:
    f.write(cobol)
    cbl = f.name

print("=== Booting TK5 ===", flush=True)
runner = RealHerculesRunner.from_mvs_path(MVS_PATH)
print("=== Running SMFTEST ===", flush=True)
result = runner.run(cbl)
print(f"=== Result: {result} ===", flush=True)
runner._pool.__exit__(None, None, None)
os.unlink(cbl)
