# COBOL Arithmetic and Rounding Risk

## ROUNDED Clause
Adding ROUNDED to a COMPUTE or ADD statement changes how the result is stored when truncation would occur. Without ROUNDED, excess digits are truncated. With ROUNDED, the last retained digit is incremented if the first dropped digit is >= 5. For financial calculations (interest, amortisation, premium), this changes output values and can cause cumulative rounding differences across millions of transactions.

## ON SIZE ERROR
Adding or removing ON SIZE ERROR handling changes program behaviour on overflow. Without it, overflow silently wraps or truncates. With it, the program branches to an error handler. AI tools that add ON SIZE ERROR where none existed change the execution path for edge cases.

## Precision Changes
Changing PIC 9(7)V99 to PIC 9(9)V9999 increases decimal precision. This changes the byte length of COMP-3 fields and may produce different results in downstream aggregation programs that expect two decimal places.

## Regulatory Significance
FCA COBS 14 and PRA SS2/21 require that retail financial calculations (mortgage interest, insurance premium) are computed consistently and accurately. A ROUNDED change that produces different interest figures on existing loan accounts is a reportable calculation error.
