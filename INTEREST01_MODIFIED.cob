       IDENTIFICATION DIVISION.
       PROGRAM-ID. INTEREST01.
       AUTHOR. FNB-RISK-ANALYTICS.
       DATE-WRITTEN. 2019-09-03.
      *----------------------------------------------------------------
      * PROGRAMME:  INTEREST01
      * PURPOSE:    COMPOUND INTEREST AND LOAN AMORTISATION ENGINE
      *             COMPUTES MONTHLY REPAYMENT, TOTAL INTEREST PAID,
      *             EFFECTIVE ANNUAL RATE AND AFFORDABILITY METRICS.
      *             USED BY RETAIL CREDIT ASSESSMENT BATCH.
      * NOTE:       PURE COMPUTATION MODULE - NO FILE I/O
      *             INPUTS VIA WORKING-STORAGE; OUTPUT VIA DISPLAY
      *----------------------------------------------------------------
       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SOURCE-COMPUTER. IBM-ZOS.
       OBJECT-COMPUTER. IBM-ZOS.

       DATA DIVISION.
       WORKING-STORAGE SECTION.

      *--- LOAN INPUT PARAMETERS ---
       01  WS-PRINCIPAL         PIC 9(9)V99    VALUE 250000.00.
       01  WS-ANNUAL-RATE       PIC 9V9999     VALUE 0.0425.
       01  WS-TERM-YEARS        PIC 9(2)       VALUE 25.
       01  WS-TERM-MONTHS       PIC 9(3)       VALUE ZEROS.
       01  WS-MONTHLY-RATE      PIC 9V999999   VALUE ZEROS.

      *--- AMORTISATION ACCUMULATORS - OPTIMISED WITH COMP-3 ---
       01  WS-TOTAL-INTEREST    PIC 9(11)V99 COMP-3 VALUE ZEROS.
       01  WS-TOTAL-REPAID      PIC 9(11)V99 COMP-3 VALUE ZEROS.
       01  WS-RUNNING-BALANCE   PIC 9(9)V99  COMP-3 VALUE ZEROS.
       01  WS-INTEREST-PORTION  PIC 9(9)V99  COMP-3 VALUE ZEROS.
       01  WS-PRINCIPAL-PORTION PIC 9(9)V99  COMP-3 VALUE ZEROS.
       01  WS-CUMUL-INTEREST    PIC 9(11)V99 COMP-3 VALUE ZEROS.
       01  WS-CUMUL-PRINCIPAL   PIC 9(11)V99 COMP-3 VALUE ZEROS.

      *--- PAYMENT CALCULATION WORK FIELDS ---
       01  WS-MONTHLY-PAYMENT   PIC 9(7)V99    VALUE ZEROS.
       01  WS-POWER-FACTOR      PIC 9V999999   VALUE ZEROS.
       01  WS-RATE-PLUS-ONE     PIC 9V999999   VALUE ZEROS.
       01  WS-NUMERATOR         PIC 9(9)V999999 VALUE ZEROS.
       01  WS-DENOMINATOR       PIC 9V999999   VALUE ZEROS.
       01  WS-WORK-A            PIC 9(9)V999999 VALUE ZEROS.
       01  WS-WORK-B            PIC 9(9)V999999 VALUE ZEROS.

      *--- AFFORDABILITY METRICS ---
       01  WS-EFFECTIVE-RATE    PIC 9V9999     VALUE ZEROS.
       01  WS-DEBT-RATIO        PIC 9V9999     VALUE ZEROS.
       01  WS-MONTHLY-INCOME    PIC 9(7)V99    VALUE 6500.00.
       01  WS-MAX-AFFORDABLE    PIC 9(7)V99    VALUE ZEROS.
       01  WS-STRESS-RATE       PIC 9V9999     VALUE 0.0725.
       01  WS-STRESS-MONTHLY-RT PIC 9V999999   VALUE ZEROS.
       01  WS-STRESS-PAYMENT    PIC 9(7)V99    VALUE ZEROS.
       01  WS-STRESS-POWER      PIC 9V999999   VALUE ZEROS.
       01  WS-STRESS-NUMER      PIC 9(9)V999999 VALUE ZEROS.
       01  WS-STRESS-DENOM      PIC 9V999999   VALUE ZEROS.
       01  WS-AFFORDABLE-FLAG   PIC X(1)       VALUE 'N'.
           88  IS-AFFORDABLE    VALUE 'Y'.
           88  NOT-AFFORDABLE   VALUE 'N'.

      *--- LOOP CONTROL ---
       01  WS-MONTH-IDX         PIC 9(3)       VALUE ZEROS.
       01  WS-BREAK-YEAR        PIC 9(2)       VALUE ZEROS.

      *--- RATE TABLE FOR BAND LOOKUP ---
       01  WS-LTV-TABLE.
           05  WS-LTV-ENTRY OCCURS 5 TIMES
               ASCENDING KEY IS WS-LTV-BAND
               INDEXED BY WS-LTV-IDX.
               10  WS-LTV-BAND      PIC 9V99.
               10  WS-LTV-PREMIUM   PIC 9V9999.
       01  WS-LTV-RATIO         PIC 9V99       VALUE ZEROS.
       01  WS-LTV-APPLIED  PIC 9V9999     VALUE ZEROS.
       01  WS-LTV-FOUND         PIC X(1)       VALUE 'N'.
       01  WS-PROPERTY-VALUE    PIC 9(9)V99    VALUE 310000.00.

      *--- OUTPUT DISPLAY WORK ---
       01  WS-DISPLAY-PAYMENT   PIC Z,ZZZ,ZZ9.99.
       01  WS-DISPLAY-INTEREST  PIC ZZ,ZZZ,ZZZ.99.
       01  WS-DISPLAY-TOTAL     PIC ZZZ,ZZZ,ZZZ.99.
       01  WS-DISPLAY-RATE      PIC Z9.99.

       PROCEDURE DIVISION.
      *----------------------------------------------------------------
       MAIN-LOGIC.
           PERFORM LOAD-LTV-TABLE
           PERFORM COMPUTE-TERM-MONTHS
           PERFORM COMPUTE-MONTHLY-RATE
           PERFORM COMPUTE-MONTHLY-PAYMENT
           PERFORM COMPUTE-STRESS-PAYMENT
           PERFORM COMPUTE-EFFECTIVE-RATE
           PERFORM COMPUTE-LTV-PREMIUM
           PERFORM AMORTISE-LOAN
           PERFORM COMPUTE-AFFORDABILITY
           PERFORM DISPLAY-RESULTS
           STOP RUN.

      *----------------------------------------------------------------
       LOAD-LTV-TABLE.
           MOVE 0.60 TO WS-LTV-BAND(1)
           MOVE 0.0000 TO WS-LTV-PREMIUM(1)
           MOVE 0.75 TO WS-LTV-BAND(2)
           MOVE 0.0025 TO WS-LTV-PREMIUM(2)
           MOVE 0.80 TO WS-LTV-BAND(3)
           MOVE 0.0050 TO WS-LTV-PREMIUM(3)
           MOVE 0.90 TO WS-LTV-BAND(4)
           MOVE 0.0100 TO WS-LTV-PREMIUM(4)
           MOVE 0.95 TO WS-LTV-BAND(5)
           MOVE 0.0150 TO WS-LTV-PREMIUM(5).

      *----------------------------------------------------------------
       COMPUTE-TERM-MONTHS.
           COMPUTE WS-TERM-MONTHS = WS-TERM-YEARS * 12.

      *----------------------------------------------------------------
       COMPUTE-MONTHLY-RATE.
           COMPUTE WS-MONTHLY-RATE = WS-ANNUAL-RATE / 12.

      *----------------------------------------------------------------
       COMPUTE-MONTHLY-PAYMENT.
           COMPUTE WS-RATE-PLUS-ONE = 1 + WS-MONTHLY-RATE
           COMPUTE WS-POWER-FACTOR =
               FUNCTION INTEGER(WS-RATE-PLUS-ONE ** WS-TERM-MONTHS)
           COMPUTE WS-NUMERATOR =
               WS-PRINCIPAL * WS-MONTHLY-RATE * WS-POWER-FACTOR
           COMPUTE WS-DENOMINATOR = WS-POWER-FACTOR - 1
           IF WS-DENOMINATOR > ZEROS
               COMPUTE WS-MONTHLY-PAYMENT =
                   WS-NUMERATOR / WS-DENOMINATOR
           ELSE
               COMPUTE WS-MONTHLY-PAYMENT =
                   WS-PRINCIPAL / WS-TERM-MONTHS
           END-IF.

      *----------------------------------------------------------------
       COMPUTE-STRESS-PAYMENT.
           COMPUTE WS-STRESS-MONTHLY-RT = WS-STRESS-RATE / 12
           COMPUTE WS-STRESS-POWER =
               FUNCTION INTEGER(
                   (1 + WS-STRESS-MONTHLY-RT) ** WS-TERM-MONTHS)
           COMPUTE WS-STRESS-NUMER =
               WS-PRINCIPAL * WS-STRESS-MONTHLY-RT * WS-STRESS-POWER
           COMPUTE WS-STRESS-DENOM = WS-STRESS-POWER - 1
           IF WS-STRESS-DENOM > ZEROS
               COMPUTE WS-STRESS-PAYMENT =
                   WS-STRESS-NUMER / WS-STRESS-DENOM
           ELSE
               COMPUTE WS-STRESS-PAYMENT =
                   WS-PRINCIPAL / WS-TERM-MONTHS
           END-IF.

      *----------------------------------------------------------------
       COMPUTE-EFFECTIVE-RATE.
           COMPUTE WS-EFFECTIVE-RATE =
               (1 + WS-MONTHLY-RATE) ** 12 - 1.

      *----------------------------------------------------------------
       COMPUTE-LTV-PREMIUM.
           COMPUTE WS-LTV-RATIO =
               WS-PRINCIPAL / WS-PROPERTY-VALUE
           MOVE 'N' TO WS-LTV-FOUND
           SET WS-LTV-IDX TO 1
           SEARCH WS-LTV-ENTRY
               AT END
                   MOVE WS-LTV-PREMIUM(5) TO WS-LTV-APPLIED
               WHEN WS-LTV-BAND(WS-LTV-IDX) >= WS-LTV-RATIO
                   MOVE 'Y' TO WS-LTV-FOUND
                   MOVE WS-LTV-PREMIUM(WS-LTV-IDX) TO WS-LTV-APPLIED
           END-SEARCH.

      *----------------------------------------------------------------
       AMORTISE-LOAN.
           MOVE WS-PRINCIPAL      TO WS-RUNNING-BALANCE
           MOVE ZEROS             TO WS-TOTAL-INTEREST
           MOVE ZEROS             TO WS-TOTAL-REPAID
           MOVE ZEROS             TO WS-CUMUL-INTEREST
           MOVE ZEROS             TO WS-CUMUL-PRINCIPAL
           PERFORM VARYING WS-MONTH-IDX FROM 1 BY 1
               UNTIL WS-MONTH-IDX > WS-TERM-MONTHS
               COMPUTE WS-INTEREST-PORTION =
                   WS-RUNNING-BALANCE * WS-MONTHLY-RATE
               COMPUTE WS-PRINCIPAL-PORTION =
                   WS-MONTHLY-PAYMENT - WS-INTEREST-PORTION
               IF WS-PRINCIPAL-PORTION > WS-RUNNING-BALANCE
                   MOVE WS-RUNNING-BALANCE TO WS-PRINCIPAL-PORTION
               END-IF
               COMPUTE WS-RUNNING-BALANCE =
                   WS-RUNNING-BALANCE - WS-PRINCIPAL-PORTION
               COMPUTE WS-TOTAL-INTEREST =
                   WS-TOTAL-INTEREST + WS-INTEREST-PORTION
               COMPUTE WS-TOTAL-REPAID =
                   WS-TOTAL-REPAID + WS-MONTHLY-PAYMENT
               COMPUTE WS-CUMUL-INTEREST =
                   WS-CUMUL-INTEREST + WS-INTEREST-PORTION
               COMPUTE WS-CUMUL-PRINCIPAL =
                   WS-CUMUL-PRINCIPAL + WS-PRINCIPAL-PORTION
           END-PERFORM.

      *----------------------------------------------------------------
       COMPUTE-AFFORDABILITY.
           COMPUTE WS-DEBT-RATIO =
               WS-MONTHLY-PAYMENT / WS-MONTHLY-INCOME
           COMPUTE WS-MAX-AFFORDABLE =
               WS-MONTHLY-INCOME * 0.35
           IF WS-MONTHLY-PAYMENT <= WS-MAX-AFFORDABLE
               MOVE 'Y' TO WS-AFFORDABLE-FLAG
           ELSE
               MOVE 'N' TO WS-AFFORDABLE-FLAG
           END-IF.

      *----------------------------------------------------------------
       DISPLAY-RESULTS.
           MOVE WS-MONTHLY-PAYMENT  TO WS-DISPLAY-PAYMENT
           MOVE WS-TOTAL-INTEREST   TO WS-DISPLAY-INTEREST
           MOVE WS-TOTAL-REPAID     TO WS-DISPLAY-TOTAL
           COMPUTE WS-WORK-A = WS-EFFECTIVE-RATE * 100
           MOVE WS-WORK-A           TO WS-DISPLAY-RATE
           DISPLAY '=================================='
           DISPLAY 'FNB MORTGAGE ASSESSMENT ENGINE   '
           DISPLAY '=================================='
           DISPLAY 'PRINCIPAL       : ' WS-PRINCIPAL
           DISPLAY 'ANNUAL RATE     : ' WS-ANNUAL-RATE
           DISPLAY 'TERM (MONTHS)   : ' WS-TERM-MONTHS
           DISPLAY '----------------------------------'
           DISPLAY 'MONTHLY PAYMENT : ' WS-DISPLAY-PAYMENT
           DISPLAY 'TOTAL INTEREST  : ' WS-DISPLAY-INTEREST
           DISPLAY 'TOTAL REPAID    : ' WS-DISPLAY-TOTAL
           DISPLAY 'EFFECTIVE RATE  : ' WS-DISPLAY-RATE '%'
           DISPLAY 'LTV RATIO       : ' WS-LTV-RATIO
           DISPLAY 'LTV PREMIUM     : ' WS-LTV-APPLIED
           DISPLAY 'STRESS PAYMENT  : ' WS-STRESS-PAYMENT
           DISPLAY 'DEBT RATIO      : ' WS-DEBT-RATIO
           IF IS-AFFORDABLE
               DISPLAY 'AFFORDABILITY   : PASS'
           ELSE
               DISPLAY 'AFFORDABILITY   : REFER'
           END-IF
           DISPLAY '=================================='.

       END PROGRAM INTEREST01.
