# Known Bad Pattern: COMPILE_ERROR — INTEREST-CALC

**Signal:** Refinery FLAGGED  **Date:** 2026-05-16

## What went wrong

At `original`: `` was changed to `/mnt/c/Users/okeat/AppData/Local/Temp/tmp4f_ie55k/orig_ZERO.cob:11: error: INTEREST-COPY: No such file or directory
/mnt/c/Users/okeat/AppData/Local/Temp/tmp4f_ie55k/orig_ZERO.cob:6: error: missing file description for FILE INTEREST-FILE
/mnt/c/Users/okeat/AppData/Local/Temp/tmp4f_ie55k/orig_ZERO.cob:7: error: PROCEDURE DIVISION header missing
/mnt/c/Users/okeat/AppData/Local/Temp/tmp4f_ie55k/orig_ZERO.cob:7: error: syntax error, unexpected Identifier
/mnt/c/Users/okeat/AppData/Local/Temp/tmp4f_` (severity: HIGH).

## Pattern to avoid

Do NOT modify `original` when optimising INTEREST-CALC-style programs. The expression `` must be preserved exactly — changing it alters business logic.
