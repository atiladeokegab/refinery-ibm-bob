# COMP-3 (Packed Decimal) Storage Format Risks

## What is COMP-3
COMP-3 (Computational-3) is IBM's packed decimal binary encoding for numeric fields in COBOL. Each byte stores two decimal digits. A field declared PIC 9(7)V99 COMP-3 occupies 5 bytes on disk and in VSAM file records.

## Risk: VSAM Layout Corruption
Changing a field from COMP-3 to DISPLAY (or vice versa) changes its byte length. If that field is part of a VSAM KSDS or ESDS record layout, ALL programs that READ or WRITE that file must be recompiled and redeployed simultaneously. A mismatch causes silent data corruption — numeric values are read incorrectly without any runtime error.

## Risk: Downstream Program Impact
Any COBOL COPY member (copybook) that defines a COMP-3 field is shared across all programs that COPY it. Changing the PICTURE clause or USAGE in one program without updating the copybook and all copybook users creates a data format mismatch at runtime.

## Risk: Packed Decimal Overflow
COMP-3 fields have a fixed decimal precision defined by the PICTURE clause. AI tools that add ROUNDED clauses or change precision (e.g., from PIC 9(7)V99 to PIC 9(9)V9999) alter the storage size, breaking binary compatibility with existing VSAM records.

## Regulatory Significance
In banking and insurance COBOL systems, COMP-3 fields typically store monetary values (loan balances, interest rates, premium amounts). A silent COMP-3 corruption on a mortgage interest calculation field constitutes a material financial error under FCA SYSC 15A and DORA Article 28.
