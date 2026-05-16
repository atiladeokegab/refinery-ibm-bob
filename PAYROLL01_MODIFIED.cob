       IDENTIFICATION DIVISION.
       PROGRAM-ID. PAYROLL01.
       AUTHOR. FNB-PAYROLL-TEAM.
       DATE-WRITTEN. 2017-06-15.
       DATE-COMPILED.
       SECURITY. RESTRICTED.
      *----------------------------------------------------------------
      * PROGRAMME:  PAYROLL01
      * SYSTEM:     HR CORE BANKING - PAYROLL SUBSYSTEM
      * PURPOSE:    NIGHTLY PAYROLL BATCH - COMPUTES GROSS/NET PAY,
      *             INCOME TAX, NATIONAL INSURANCE CONTRIBUTIONS AND
      *             PENSION DEDUCTIONS FOR ALL ACTIVE EMPLOYEES.
      *             PRODUCES PAYSLIP FILE AND MANAGEMENT SUMMARY.
      * FREQUENCY:  NIGHTLY - FULL PAY RUN ON 25TH OF EACH MONTH
      * INPUT:      EMPFILE  - EMPLOYEE MASTER FILE (INDEXED VSAM)
      *             TIMEFILE - APPROVED TIMESHEET RECORDS (SEQ)
      *             TAXFILE  - HMRC TAX CODE TABLE (SEQ)
      * OUTPUT:     PAYFILE  - PAYSLIP OUTPUT RECORDS (SEQ)
      *             RPTFILE  - MANAGEMENT SUMMARY REPORT (SEQ)
      *             ERRFILE  - EXCEPTION / ERROR RECORDS (SEQ)
      * SORT WORK:  SRTWORK  - INTERNAL SORT SCRATCH
      * RETURN CODE: 0=SUCCESS  8=WARNINGS  16=ABEND
      *----------------------------------------------------------------
       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SOURCE-COMPUTER. IBM-ZOS.
       OBJECT-COMPUTER. IBM-ZOS.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT EMPFILE   ASSIGN TO 'EMPFILE'
               ORGANIZATION IS INDEXED
               ACCESS MODE  IS DYNAMIC
               RECORD KEY   IS EMP-NUMBER
               FILE STATUS  IS WS-EMP-STATUS.
           SELECT TIMEFILE  ASSIGN TO 'TIMEFILE'
               ORGANIZATION IS SEQUENTIAL
               ACCESS MODE  IS SEQUENTIAL
               FILE STATUS  IS WS-TIME-STATUS.
           SELECT TAXFILE   ASSIGN TO 'TAXFILE'
               ORGANIZATION IS SEQUENTIAL
               ACCESS MODE  IS SEQUENTIAL
               FILE STATUS  IS WS-TAX-STATUS.
           SELECT PAYFILE   ASSIGN TO 'PAYFILE'
               ORGANIZATION IS SEQUENTIAL
               ACCESS MODE  IS SEQUENTIAL
               FILE STATUS  IS WS-PAY-STATUS.
           SELECT RPTFILE   ASSIGN TO 'RPTFILE'
               ORGANIZATION IS SEQUENTIAL
               ACCESS MODE  IS SEQUENTIAL
               FILE STATUS  IS WS-RPT-STATUS.
           SELECT ERRFILE   ASSIGN TO 'ERRFILE'
               ORGANIZATION IS SEQUENTIAL
               ACCESS MODE  IS SEQUENTIAL
               FILE STATUS  IS WS-ERR-STATUS.
           SELECT SRTWORK   ASSIGN TO 'SRTWORK'.

       DATA DIVISION.
       FILE SECTION.
       FD  EMPFILE
           LABEL RECORDS ARE STANDARD
           RECORDING MODE IS F.
       01  EMP-RECORD.
           05  EMP-NUMBER       PIC X(8).
           05  EMP-SURNAME      PIC X(20).
           05  EMP-FORENAME     PIC X(15).
           05  EMP-DEPARTMENT   PIC X(6).
           05  EMP-GRADE        PIC X(2).
           05  EMP-SALARY       PIC 9(7)V99.
           05  EMP-TAX-CODE     PIC X(6).
           05  EMP-NI-NUMBER    PIC X(9).
           05  EMP-PENSION-RATE PIC 9V99.
           05  EMP-STATUS       PIC X(1).
               88  EMP-ACTIVE   VALUE 'A'.
               88  EMP-LEAVER   VALUE 'L'.
               88  EMP-SUSPENDED VALUE 'S'.
           05  EMP-START-DATE   PIC 9(8).
           05  EMP-BANK-SORT    PIC X(6).
           05  EMP-BANK-ACCT    PIC X(8).
           05  FILLER           PIC X(10).

       FD  TIMEFILE
           LABEL RECORDS ARE STANDARD
           RECORDING MODE IS F.
       01  TIME-RECORD.
           05  TR-EMP-NUMBER    PIC X(8).
           05  TR-PAY-PERIOD    PIC X(6).
           05  TR-BASIC-HOURS   PIC 9(3)V99.
           05  TR-OVERTIME-HRS  PIC 9(3)V99.
           05  TR-ABSENCE-DAYS  PIC 9(2)V9.
           05  TR-BANK-HOLS     PIC 9(2).
           05  TR-APPROVED      PIC X(1).
               88  TR-APPROVED-YES VALUE 'Y'.
           05  FILLER           PIC X(15).

       FD  TAXFILE
           LABEL RECORDS ARE STANDARD
           RECORDING MODE IS F.
       01  TAX-RECORD.
           05  TX-CODE          PIC X(6).
           05  TX-BAND-LOW      PIC 9(7)V99.
           05  TX-BAND-HIGH     PIC 9(7)V99.
           05  TX-RATE          PIC 9V9999.
           05  TX-PERSONAL-ALLOW PIC 9(7)V99.
           05  FILLER           PIC X(10).

       FD  PAYFILE
           LABEL RECORDS ARE STANDARD
           RECORDING MODE IS F.
       01  PAY-RECORD.
           05  PR-EMP-NUMBER    PIC X(8).
           05  PR-PAY-PERIOD    PIC X(6).
           05  PR-GROSS-PAY     PIC 9(9)V99.
           05  PR-INCOME-TAX    PIC 9(7)V99.
           05  PR-NI-EMP        PIC 9(7)V99.
           05  PR-NI-EMPLR      PIC 9(7)V99.
           05  PR-PENSION-EMP   PIC 9(7)V99.
           05  PR-PENSION-EMPLR PIC 9(7)V99.
           05  PR-NET-PAY       PIC 9(9)V99.
           05  PR-BANK-SORT     PIC X(6).
           05  PR-BANK-ACCT     PIC X(8).
           05  FILLER           PIC X(15).

       FD  RPTFILE
           LABEL RECORDS ARE STANDARD
           RECORDING MODE IS F.
       01  RPT-LINE             PIC X(132).

       FD  ERRFILE
           LABEL RECORDS ARE STANDARD
           RECORDING MODE IS F.
       01  ERR-RECORD           PIC X(120).

       SD  SRTWORK
           RECORD IS 80 CHARACTERS.
       01  SORT-REC.
           05  SR-EMP-NUMBER    PIC X(8).
           05  SR-DEPARTMENT    PIC X(6).
           05  SR-GROSS-PAY     PIC 9(9)V99.
           05  FILLER           PIC X(57).

       WORKING-STORAGE SECTION.
      *--- FILE STATUS CODES ---
       01  WS-EMP-STATUS        PIC X(2) VALUE '00'.
       01  WS-TIME-STATUS       PIC X(2) VALUE '00'.
       01  WS-TAX-STATUS        PIC X(2) VALUE '00'.
       01  WS-PAY-STATUS        PIC X(2) VALUE '00'.
       01  WS-RPT-STATUS        PIC X(2) VALUE '00'.
       01  WS-ERR-STATUS        PIC X(2) VALUE '00'.

      *--- CONTROL FLAGS AND SWITCHES ---
       01  WS-EOF-TIME          PIC X(1) VALUE 'N'.
           88  EOF-TIME         VALUE 'Y'.
           88  NOT-EOF-TIME     VALUE 'N'.
       01  WS-EOF-TAX           PIC X(1) VALUE 'N'.
           88  EOF-TAX          VALUE 'Y'.
       01  WS-PROCESS-FLAG      PIC X(1) VALUE 'N'.
           88  OK-TO-PROCESS    VALUE 'Y'.
           88  SKIP-RECORD      VALUE 'N'.
       01  WS-ABEND-FLAG        PIC X(1) VALUE 'N'.
           88  ABEND-REQUESTED  VALUE 'Y'.
       01  WS-FIRST-PAGE        PIC X(1) VALUE 'Y'.
           88  IS-FIRST-PAGE    VALUE 'Y'.

      *--- REDEFINES: DATE FORMATTING BUFFER (placed before numerics) ---
       01  WS-DATE-BUF          PIC X(8)  VALUE SPACES.
       01  WS-DATE-EDIT REDEFINES WS-DATE-BUF
                                PIC X(8).
       01  WS-PERIOD-BUF        PIC X(6)  VALUE SPACES.
       01  WS-PERIOD-EDIT REDEFINES WS-PERIOD-BUF
                                PIC X(6).

      *--- NUMERIC ACCUMULATORS - OPTIMISED WITH COMP-3 (PACKED DECIMAL) ---
       01  WS-TOTAL-GROSS       PIC 9(13)V99 COMP-3 VALUE ZEROS.
       01  WS-TOTAL-TAX         PIC 9(11)V99 COMP-3 VALUE ZEROS.
       01  WS-TOTAL-NI-EMP      PIC 9(11)V99 COMP-3 VALUE ZEROS.
       01  WS-TOTAL-NI-EMPLR    PIC 9(11)V99 COMP-3 VALUE ZEROS.
       01  WS-TOTAL-PENSION-EMP PIC 9(11)V99 COMP-3 VALUE ZEROS.
       01  WS-TOTAL-NET         PIC 9(13)V99 COMP-3 VALUE ZEROS.
       01  WS-YTD-GROSS         PIC 9(13)V99 COMP-3 VALUE ZEROS.
       01  WS-YTD-TAX           PIC 9(11)V99 COMP-3 VALUE ZEROS.
       01  WS-DEPT-GROSS        PIC 9(11)V99 COMP-3 VALUE ZEROS.
       01  WS-RUN-TOTAL-NET     PIC 9(13)V99 COMP-3 VALUE ZEROS.

      *--- RECORD COUNTS ---
       01  WS-EMP-READ          PIC 9(7) VALUE ZEROS.
       01  WS-TIME-READ         PIC 9(7) VALUE ZEROS.
       01  WS-PAY-WRITTEN       PIC 9(7) VALUE ZEROS.
       01  WS-ERR-COUNT         PIC 9(5) VALUE ZEROS.
       01  WS-SKIP-COUNT        PIC 9(5) VALUE ZEROS.
       01  WS-PAGE-NO           PIC 9(4) VALUE ZEROS.
       01  WS-LINE-NO           PIC 9(3) VALUE ZEROS.

      *--- WORK FIELDS ---
       01  WS-CURRENT-DATE      PIC X(8)  VALUE SPACES.
       01  WS-CURRENT-TIME      PIC X(6)  VALUE SPACES.
       01  WS-PAY-PERIOD-ID     PIC X(6)  VALUE SPACES.
       01  WS-ANNUAL-SALARY     PIC 9(7)V99 VALUE ZEROS.
       01  WS-MONTHLY-GROSS     PIC 9(7)V99 VALUE ZEROS.
       01  WS-HOURLY-RATE       PIC 9(5)V9999 VALUE ZEROS.
       01  WS-OVERTIME-PAY      PIC 9(7)V99 VALUE ZEROS.
       01  WS-BASIC-PAY         PIC 9(7)V99 VALUE ZEROS.
       01  WS-ABSENCE-DEDUCT    PIC 9(5)V99 VALUE ZEROS.
       01  WS-GROSS-PAY         PIC 9(9)V99 VALUE ZEROS.
       01  WS-TAXABLE-INCOME    PIC 9(9)V99 VALUE ZEROS.
       01  WS-INCOME-TAX        PIC 9(7)V99 VALUE ZEROS.
       01  WS-NI-EMP            PIC 9(7)V99 VALUE ZEROS.
       01  WS-NI-EMPLR          PIC 9(7)V99 VALUE ZEROS.
       01  WS-PENSION-EMP       PIC 9(7)V99 VALUE ZEROS.
       01  WS-PENSION-EMPLR     PIC 9(7)V99 VALUE ZEROS.
       01  WS-NET-PAY           PIC 9(9)V99 VALUE ZEROS.
       01  WS-OVERTIME-MULT     PIC 9V9999   VALUE 1.5000.
       01  WS-NI-THRESHOLD      PIC 9(7)V99  VALUE 9100.00.
       01  WS-NI-UPPER-LIMIT    PIC 9(7)V99  VALUE 50270.00.
       01  WS-NI-RATE-MAIN      PIC 9V9999   VALUE 0.1200.
       01  WS-NI-RATE-UPPER     PIC 9V9999   VALUE 0.0200.
       01  WS-NI-EMPLR-RATE     PIC 9V9999   VALUE 0.1380.
       01  WS-PENSION-EMPLR-RT  PIC 9V9999   VALUE 0.0300.
       01  WS-BASIC-HOURS-STD   PIC 9(3)V99  VALUE 173.33.
       01  WS-DAYS-IN-MONTH     PIC 9(2)      VALUE 21.
       01  WS-TAX-FOUND-FLAG    PIC X(1)     VALUE 'N'.
           88  TAX-FOUND        VALUE 'Y'.
           88  TAX-NOT-FOUND    VALUE 'N'.
       01  WS-DEPT-PREV         PIC X(6)     VALUE SPACES.
       01  WS-DEPT-CURR         PIC X(6)     VALUE SPACES.
       01  WS-LOOP-IDX          PIC 9(3)     VALUE ZEROS.
       01  WS-LINES-PER-PAGE    PIC 9(3)     VALUE 55.

      *--- TAX TABLE (loaded from TAXFILE) ---
       01  WS-TAX-TABLE.
           05  WS-TAX-ENTRY OCCURS 10 TIMES
               ASCENDING KEY IS WS-TX-CODE
               INDEXED BY WS-TX-IDX.
               10  WS-TX-CODE       PIC X(6).
               10  WS-TX-BAND-LOW   PIC 9(7)V99.
               10  WS-TX-BAND-HIGH  PIC 9(7)V99.
               10  WS-TX-RATE       PIC 9V9999.
               10  WS-TX-ALLOW      PIC 9(7)V99.
       01  WS-TAX-TABLE-CNT     PIC 9(2)     VALUE ZEROS.

      *--- DEPARTMENT TABLE ---
       01  WS-DEPT-TABLE.
           05  FILLER  PIC X(6) VALUE 'RETAIL'.
           05  FILLER  PIC X(6) VALUE 'CORP  '.
           05  FILLER  PIC X(6) VALUE 'TRADE '.
           05  FILLER  PIC X(6) VALUE 'TECH  '.
           05  FILLER  PIC X(6) VALUE 'RISK  '.
           05  FILLER  PIC X(6) VALUE 'COMPL '.
           05  FILLER  PIC X(6) VALUE 'OPS   '.
           05  FILLER  PIC X(6) VALUE 'HR    '.
       01  WS-DEPT-ARRAY REDEFINES WS-DEPT-TABLE.
           05  WS-DEPT-ENTRY PIC X(6) OCCURS 8 TIMES
               INDEXED BY WS-DEPT-IDX.
       01  WS-DEPT-VALID        PIC X(1)     VALUE 'N'.

      *--- REPORT HEADER LINE ---
       01  WS-RPT-HEADER-1.
           05  FILLER   PIC X(25) VALUE 'FIRST NATIONAL BANK PLC  '.
           05  FILLER   PIC X(30) VALUE '   PAYROLL PROCESSING REPORT'.
           05  FILLER   PIC X(20) VALUE SPACES.
           05  WS-HDR-DATE  PIC X(10) VALUE SPACES.
           05  FILLER   PIC X(47) VALUE SPACES.

       01  WS-RPT-HEADER-2.
           05  FILLER   PIC X(20) VALUE 'PAY PERIOD: '.
           05  WS-HDR-PERIOD PIC X(6)  VALUE SPACES.
           05  FILLER   PIC X(106) VALUE SPACES.

       01  WS-COL-HEADER.
           05  FILLER   PIC X(10) VALUE 'EMP NO    '.
           05  FILLER   PIC X(22) VALUE 'NAME                  '.
           05  FILLER   PIC X(8)  VALUE 'DEPT    '.
           05  FILLER   PIC X(14) VALUE 'GROSS PAY     '.
           05  FILLER   PIC X(12) VALUE 'INCOME TAX  '.
           05  FILLER   PIC X(12) VALUE 'NI (EMP)    '.
           05  FILLER   PIC X(12) VALUE 'PENSION     '.
           05  FILLER   PIC X(12) VALUE 'NET PAY     '.
           05  FILLER   PIC X(40) VALUE SPACES.

       01  WS-DETAIL-LINE.
           05  WS-DL-EMPNO    PIC X(8).
           05  FILLER         PIC X(2)  VALUE SPACES.
           05  WS-DL-NAME     PIC X(20).
           05  FILLER         PIC X(2)  VALUE SPACES.
           05  WS-DL-DEPT     PIC X(6).
           05  FILLER         PIC X(2)  VALUE SPACES.
           05  WS-DL-GROSS    PIC ZZZ,ZZ9.99.
           05  FILLER         PIC X(5)  VALUE SPACES.
           05  WS-DL-TAX      PIC ZZZ,ZZ9.99.
           05  FILLER         PIC X(4)  VALUE SPACES.
           05  WS-DL-NI       PIC ZZZ,ZZ9.99.
           05  FILLER         PIC X(4)  VALUE SPACES.
           05  WS-DL-PENSION  PIC ZZZ,ZZ9.99.
           05  FILLER         PIC X(4)  VALUE SPACES.
           05  WS-DL-NET      PIC ZZZ,ZZ9.99.
           05  FILLER         PIC X(41) VALUE SPACES.

       01  WS-SUMMARY-LINE.
           05  FILLER         PIC X(30) VALUE SPACES.
           05  WS-SL-LABEL    PIC X(25).
           05  WS-SL-COUNT    PIC ZZZ,ZZ9.
           05  FILLER         PIC X(4)  VALUE SPACES.
           05  WS-SL-AMOUNT   PIC Z,ZZZ,ZZZ,ZZZ.99.
           05  FILLER         PIC X(54) VALUE SPACES.

       01  WS-DEPT-BREAK-LINE.
           05  FILLER         PIC X(30) VALUE SPACES.
           05  WS-DBL-DEPT    PIC X(6).
           05  FILLER         PIC X(6)  VALUE ' TOTAL'.
           05  FILLER         PIC X(4)  VALUE SPACES.
           05  WS-DBL-AMOUNT  PIC Z,ZZZ,ZZZ,ZZZ.99.
           05  FILLER         PIC X(72) VALUE SPACES.

       PROCEDURE DIVISION.
      *----------------------------------------------------------------
       MAIN-LOGIC.
           PERFORM INITIALISE-RUN
           PERFORM LOAD-TAX-TABLE
           PERFORM SORT-TIME-RECORDS
           PERFORM OPEN-OUTPUT-FILES
           PERFORM PROCESS-TIME-RECORDS
           PERFORM WRITE-RUN-TOTALS
           PERFORM CLOSE-ALL-FILES
           STOP RUN.

      *----------------------------------------------------------------
       INITIALISE-RUN.
           MOVE FUNCTION CURRENT-DATE(1:8) TO WS-CURRENT-DATE
           MOVE FUNCTION CURRENT-DATE(9:6) TO WS-CURRENT-TIME
           MOVE WS-CURRENT-DATE            TO WS-HDR-DATE
           MOVE ZEROS   TO WS-TOTAL-GROSS
           MOVE ZEROS   TO WS-TOTAL-TAX
           MOVE ZEROS   TO WS-TOTAL-NI-EMP
           MOVE ZEROS   TO WS-TOTAL-NI-EMPLR
           MOVE ZEROS   TO WS-TOTAL-PENSION-EMP
           MOVE ZEROS   TO WS-TOTAL-NET
           MOVE ZEROS   TO WS-YTD-GROSS
           MOVE ZEROS   TO WS-YTD-TAX
           MOVE ZEROS   TO WS-DEPT-GROSS
           MOVE ZEROS   TO WS-RUN-TOTAL-NET
           MOVE ZEROS   TO WS-EMP-READ
           MOVE ZEROS   TO WS-TIME-READ
           MOVE ZEROS   TO WS-PAY-WRITTEN
           MOVE ZEROS   TO WS-ERR-COUNT
           MOVE ZEROS   TO WS-SKIP-COUNT
           MOVE ZEROS   TO WS-TAX-TABLE-CNT.

      *----------------------------------------------------------------
       LOAD-TAX-TABLE.
           OPEN INPUT TAXFILE
           IF WS-TAX-STATUS NOT = '00'
               DISPLAY 'TAXFILE OPEN ERROR: ' WS-TAX-STATUS
               MOVE 'Y' TO WS-ABEND-FLAG
               PERFORM ABEND-ROUTINE
           END-IF
           MOVE 'N' TO WS-EOF-TAX
           PERFORM UNTIL EOF-TAX
               READ TAXFILE INTO TAX-RECORD
                   AT END MOVE 'Y' TO WS-EOF-TAX
               END-READ
               IF NOT EOF-TAX
                   ADD 1 TO WS-TAX-TABLE-CNT
                   MOVE TX-CODE     TO WS-TX-CODE(WS-TAX-TABLE-CNT)
                   MOVE TX-BAND-LOW TO WS-TX-BAND-LOW(WS-TAX-TABLE-CNT)
                   MOVE TX-BAND-HIGH TO WS-TX-BAND-HIGH(WS-TAX-TABLE-CNT)
                   MOVE TX-RATE     TO WS-TX-RATE(WS-TAX-TABLE-CNT)
                   MOVE TX-ALLOW    TO WS-TX-ALLOW(WS-TAX-TABLE-CNT)
               END-IF
           END-PERFORM
           CLOSE TAXFILE.

      *----------------------------------------------------------------
       SORT-TIME-RECORDS.
           SORT SRTWORK
               ASCENDING KEY SR-DEPARTMENT
               ASCENDING KEY SR-EMP-NUMBER
               USING  TIMEFILE
               GIVING TIMEFILE.

      *----------------------------------------------------------------
       OPEN-OUTPUT-FILES.
           OPEN OUTPUT PAYFILE
           IF WS-PAY-STATUS NOT = '00'
               DISPLAY 'PAYFILE OPEN ERROR: ' WS-PAY-STATUS
               PERFORM ABEND-ROUTINE
           END-IF
           OPEN OUTPUT RPTFILE
           IF WS-RPT-STATUS NOT = '00'
               DISPLAY 'RPTFILE OPEN ERROR: ' WS-RPT-STATUS
               PERFORM ABEND-ROUTINE
           END-IF
           OPEN OUTPUT ERRFILE
           IF WS-ERR-STATUS NOT = '00'
               DISPLAY 'ERRFILE OPEN ERROR: ' WS-ERR-STATUS
               PERFORM ABEND-ROUTINE
           END-IF
           PERFORM WRITE-PAGE-HEADER.

      *----------------------------------------------------------------
       PROCESS-TIME-RECORDS.
           OPEN INPUT TIMEFILE
           IF WS-TIME-STATUS NOT = '00'
               DISPLAY 'TIMEFILE OPEN ERROR: ' WS-TIME-STATUS
               PERFORM ABEND-ROUTINE
           END-IF
           MOVE 'N' TO WS-EOF-TIME
           PERFORM READ-TIME-RECORD
           PERFORM UNTIL EOF-TIME
               ADD 1 TO WS-TIME-READ
               PERFORM VALIDATE-TIME-RECORD
               IF OK-TO-PROCESS
                   PERFORM FETCH-EMPLOYEE
                   IF OK-TO-PROCESS
                       PERFORM COMPUTE-GROSS-PAY
                       PERFORM LOOKUP-TAX-CODE
                       PERFORM COMPUTE-DEDUCTIONS
                       PERFORM COMPUTE-NET-PAY
                       PERFORM WRITE-PAYSLIP
                       PERFORM WRITE-REPORT-LINE
                       PERFORM UPDATE-ACCUMULATORS
                   END-IF
               ELSE
                   PERFORM WRITE-ERROR-RECORD
               END-IF
               PERFORM READ-TIME-RECORD
           END-PERFORM
           CLOSE TIMEFILE.

      *----------------------------------------------------------------
       READ-TIME-RECORD.
           READ TIMEFILE
               AT END MOVE 'Y' TO WS-EOF-TIME
           END-READ.

      *----------------------------------------------------------------
       VALIDATE-TIME-RECORD.
           MOVE 'Y' TO WS-PROCESS-FLAG
           IF TR-EMP-NUMBER = SPACES
               MOVE 'N' TO WS-PROCESS-FLAG
           END-IF
           IF TR-PAY-PERIOD = SPACES
               MOVE 'N' TO WS-PROCESS-FLAG
           END-IF
           IF NOT TR-APPROVED-YES
               MOVE 'N' TO WS-PROCESS-FLAG
           END-IF
           IF TR-BASIC-HOURS < ZEROS
               MOVE 'N' TO WS-PROCESS-FLAG
           END-IF.

      *----------------------------------------------------------------
       FETCH-EMPLOYEE.
           MOVE TR-EMP-NUMBER TO EMP-NUMBER
           READ EMPFILE
               INVALID KEY
                   MOVE 'N' TO WS-PROCESS-FLAG
                   ADD 1 TO WS-SKIP-COUNT
           END-READ
           IF OK-TO-PROCESS
               ADD 1 TO WS-EMP-READ
               IF NOT EMP-ACTIVE
                   MOVE 'N' TO WS-PROCESS-FLAG
               END-IF
           END-IF.

      *----------------------------------------------------------------
       COMPUTE-GROSS-PAY.
           COMPUTE WS-ANNUAL-SALARY = EMP-SALARY
           COMPUTE WS-MONTHLY-GROSS = WS-ANNUAL-SALARY / 12
           COMPUTE WS-HOURLY-RATE   =
               WS-MONTHLY-GROSS / WS-BASIC-HOURS-STD
           COMPUTE WS-BASIC-PAY     =
               TR-BASIC-HOURS * WS-HOURLY-RATE
           COMPUTE WS-OVERTIME-PAY  =
               TR-OVERTIME-HRS * WS-HOURLY-RATE * WS-OVERTIME-MULT
           IF TR-ABSENCE-DAYS > ZEROS
               COMPUTE WS-ABSENCE-DEDUCT =
                   (WS-MONTHLY-GROSS / WS-DAYS-IN-MONTH) *
                   TR-ABSENCE-DAYS
           ELSE
               MOVE ZEROS TO WS-ABSENCE-DEDUCT
           END-IF
           COMPUTE WS-GROSS-PAY =
               WS-BASIC-PAY + WS-OVERTIME-PAY - WS-ABSENCE-DEDUCT.

      *----------------------------------------------------------------
       LOOKUP-TAX-CODE.
           MOVE 'N' TO WS-TAX-FOUND-FLAG
           SET WS-TX-IDX TO 1
           SEARCH WS-TAX-ENTRY
               AT END
                   MOVE 'N' TO WS-TAX-FOUND-FLAG
               WHEN WS-TX-CODE(WS-TX-IDX) = EMP-TAX-CODE
                   MOVE 'Y' TO WS-TAX-FOUND-FLAG
           END-SEARCH.

      *----------------------------------------------------------------
       COMPUTE-DEDUCTIONS.
           PERFORM COMPUTE-INCOME-TAX
           PERFORM COMPUTE-NI
           PERFORM COMPUTE-PENSION.

      *----------------------------------------------------------------
       COMPUTE-INCOME-TAX.
           IF TAX-FOUND
               COMPUTE WS-TAXABLE-INCOME =
                   WS-GROSS-PAY - WS-TX-ALLOW(WS-TX-IDX)
               IF WS-TAXABLE-INCOME < ZEROS
                   MOVE ZEROS TO WS-TAXABLE-INCOME
               END-IF
               COMPUTE WS-INCOME-TAX =
                   WS-TAXABLE-INCOME * WS-TX-RATE(WS-TX-IDX)
           ELSE
               COMPUTE WS-INCOME-TAX = WS-GROSS-PAY * 0.2000
           END-IF.

      *----------------------------------------------------------------
       COMPUTE-NI.
           IF WS-GROSS-PAY > WS-NI-THRESHOLD
               IF WS-GROSS-PAY <= WS-NI-UPPER-LIMIT
                   COMPUTE WS-NI-EMP =
                       (WS-GROSS-PAY - WS-NI-THRESHOLD) *
                       WS-NI-RATE-MAIN
               ELSE
                   COMPUTE WS-NI-EMP =
                       (WS-NI-UPPER-LIMIT - WS-NI-THRESHOLD) *
                       WS-NI-RATE-MAIN +
                       (WS-GROSS-PAY - WS-NI-UPPER-LIMIT) *
                       WS-NI-RATE-UPPER
               END-IF
               COMPUTE WS-NI-EMPLR =
                   WS-GROSS-PAY * WS-NI-EMPLR-RATE
           ELSE
               MOVE ZEROS TO WS-NI-EMP
               MOVE ZEROS TO WS-NI-EMPLR
           END-IF.

      *----------------------------------------------------------------
       COMPUTE-PENSION.
           COMPUTE WS-PENSION-EMP  =
               WS-GROSS-PAY * EMP-PENSION-RATE
           COMPUTE WS-PENSION-EMPLR =
               WS-GROSS-PAY * WS-PENSION-EMPLR-RT.

      *----------------------------------------------------------------
       COMPUTE-NET-PAY.
           COMPUTE WS-NET-PAY =
               WS-GROSS-PAY
               - WS-INCOME-TAX
               - WS-NI-EMP
               - WS-PENSION-EMP.

      *----------------------------------------------------------------
       WRITE-PAYSLIP.
           MOVE TR-EMP-NUMBER    TO PR-EMP-NUMBER
           MOVE TR-PAY-PERIOD    TO PR-PAY-PERIOD
           MOVE WS-GROSS-PAY     TO PR-GROSS-PAY
           MOVE WS-INCOME-TAX    TO PR-INCOME-TAX
           MOVE WS-NI-EMP        TO PR-NI-EMP
           MOVE WS-NI-EMPLR      TO PR-NI-EMPLR
           MOVE WS-PENSION-EMP   TO PR-PENSION-EMP
           MOVE WS-PENSION-EMPLR TO PR-PENSION-EMPLR
           MOVE WS-NET-PAY       TO PR-NET-PAY
           MOVE EMP-BANK-SORT    TO PR-BANK-SORT
           MOVE EMP-BANK-ACCT    TO PR-BANK-ACCT
           WRITE PAY-RECORD
           ADD 1 TO WS-PAY-WRITTEN.

      *----------------------------------------------------------------
       WRITE-REPORT-LINE.
           IF WS-LINE-NO > WS-LINES-PER-PAGE
               PERFORM WRITE-PAGE-HEADER
           END-IF
           MOVE TR-EMP-NUMBER    TO WS-DL-EMPNO
           MOVE EMP-SURNAME      TO WS-DL-NAME
           MOVE EMP-DEPARTMENT   TO WS-DL-DEPT
           MOVE WS-GROSS-PAY     TO WS-DL-GROSS
           MOVE WS-INCOME-TAX    TO WS-DL-TAX
           MOVE WS-NI-EMP        TO WS-DL-NI
           MOVE WS-PENSION-EMP   TO WS-DL-PENSION
           MOVE WS-NET-PAY       TO WS-DL-NET
           WRITE RPT-LINE FROM WS-DETAIL-LINE
               AFTER ADVANCING 1 LINE
           ADD 1 TO WS-LINE-NO.

      *----------------------------------------------------------------
       WRITE-PAGE-HEADER.
           ADD 1 TO WS-PAGE-NO
           WRITE RPT-LINE FROM WS-RPT-HEADER-1
               AFTER ADVANCING PAGE
           WRITE RPT-LINE FROM WS-RPT-HEADER-2
               AFTER ADVANCING 1 LINE
           WRITE RPT-LINE FROM WS-COL-HEADER
               AFTER ADVANCING 2 LINES
           MOVE ZEROS TO WS-LINE-NO.

      *----------------------------------------------------------------
       UPDATE-ACCUMULATORS.
           COMPUTE WS-TOTAL-GROSS =
               WS-TOTAL-GROSS + WS-GROSS-PAY
           COMPUTE WS-TOTAL-TAX =
               WS-TOTAL-TAX + WS-INCOME-TAX
           COMPUTE WS-TOTAL-NI-EMP =
               WS-TOTAL-NI-EMP + WS-NI-EMP
           COMPUTE WS-TOTAL-NI-EMPLR =
               WS-TOTAL-NI-EMPLR + WS-NI-EMPLR
           COMPUTE WS-TOTAL-PENSION-EMP =
               WS-TOTAL-PENSION-EMP + WS-PENSION-EMP
           COMPUTE WS-TOTAL-NET =
               WS-TOTAL-NET + WS-NET-PAY
           COMPUTE WS-DEPT-GROSS =
               WS-DEPT-GROSS + WS-GROSS-PAY
           COMPUTE WS-RUN-TOTAL-NET =
               WS-RUN-TOTAL-NET + WS-NET-PAY.

      *----------------------------------------------------------------
       WRITE-DEPT-BREAK.
           MOVE WS-DEPT-PREV      TO WS-DBL-DEPT
           MOVE WS-DEPT-GROSS     TO WS-DBL-AMOUNT
           WRITE RPT-LINE FROM WS-DEPT-BREAK-LINE
               AFTER ADVANCING 2 LINES
           MOVE ZEROS             TO WS-DEPT-GROSS.

      *----------------------------------------------------------------
       WRITE-RUN-TOTALS.
           MOVE 'TOTAL EMPLOYEES PROCESSED ' TO WS-SL-LABEL
           MOVE WS-PAY-WRITTEN               TO WS-SL-COUNT
           MOVE WS-TOTAL-GROSS               TO WS-SL-AMOUNT
           WRITE RPT-LINE FROM WS-SUMMARY-LINE
               AFTER ADVANCING 3 LINES
           MOVE 'TOTAL GROSS PAYROLL       ' TO WS-SL-LABEL
           MOVE WS-PAY-WRITTEN               TO WS-SL-COUNT
           MOVE WS-TOTAL-GROSS               TO WS-SL-AMOUNT
           WRITE RPT-LINE FROM WS-SUMMARY-LINE
               AFTER ADVANCING 1 LINE
           MOVE 'TOTAL INCOME TAX          ' TO WS-SL-LABEL
           MOVE WS-PAY-WRITTEN               TO WS-SL-COUNT
           MOVE WS-TOTAL-TAX                 TO WS-SL-AMOUNT
           WRITE RPT-LINE FROM WS-SUMMARY-LINE
               AFTER ADVANCING 1 LINE
           MOVE 'TOTAL NI (EMPLOYEE)       ' TO WS-SL-LABEL
           MOVE WS-PAY-WRITTEN               TO WS-SL-COUNT
           MOVE WS-TOTAL-NI-EMP              TO WS-SL-AMOUNT
           WRITE RPT-LINE FROM WS-SUMMARY-LINE
               AFTER ADVANCING 1 LINE
           MOVE 'TOTAL NI (EMPLOYER)       ' TO WS-SL-LABEL
           MOVE WS-PAY-WRITTEN               TO WS-SL-COUNT
           MOVE WS-TOTAL-NI-EMPLR            TO WS-SL-AMOUNT
           WRITE RPT-LINE FROM WS-SUMMARY-LINE
               AFTER ADVANCING 1 LINE
           MOVE 'TOTAL PENSION (EMPLOYEE)  ' TO WS-SL-LABEL
           MOVE WS-PAY-WRITTEN               TO WS-SL-COUNT
           MOVE WS-TOTAL-PENSION-EMP         TO WS-SL-AMOUNT
           WRITE RPT-LINE FROM WS-SUMMARY-LINE
               AFTER ADVANCING 1 LINE
           MOVE 'TOTAL NET PAYROLL         ' TO WS-SL-LABEL
           MOVE WS-PAY-WRITTEN               TO WS-SL-COUNT
           MOVE WS-TOTAL-NET                 TO WS-SL-AMOUNT
           WRITE RPT-LINE FROM WS-SUMMARY-LINE
               AFTER ADVANCING 1 LINE
           MOVE 'EXCEPTION RECORDS         ' TO WS-SL-LABEL
           MOVE WS-ERR-COUNT                 TO WS-SL-COUNT
           MOVE ZEROS                        TO WS-SL-AMOUNT
           WRITE RPT-LINE FROM WS-SUMMARY-LINE
               AFTER ADVANCING 1 LINE.

      *----------------------------------------------------------------
       WRITE-ERROR-RECORD.
           ADD 1 TO WS-ERR-COUNT
           MOVE TR-EMP-NUMBER  TO ERR-RECORD(1:8)
           MOVE TR-PAY-PERIOD  TO ERR-RECORD(9:6)
           MOVE 'VALIDATION FAILED           '
                               TO ERR-RECORD(15:28)
           WRITE ERR-RECORD
               AFTER ADVANCING 1 LINE.

      *----------------------------------------------------------------
       VALIDATE-DEPARTMENT.
           MOVE 'N' TO WS-DEPT-VALID
           SET WS-DEPT-IDX TO 1
           SEARCH WS-DEPT-ENTRY
               AT END
                   MOVE 'N' TO WS-DEPT-VALID
               WHEN WS-DEPT-ENTRY(WS-DEPT-IDX) = EMP-DEPARTMENT
                   MOVE 'Y' TO WS-DEPT-VALID
           END-SEARCH.

      *----------------------------------------------------------------
       GENERATE-AUDIT-TRAIL.
           PERFORM VARYING WS-LOOP-IDX FROM 1 BY 1
               UNTIL WS-LOOP-IDX > WS-TAX-TABLE-CNT
               MOVE WS-TX-CODE(WS-LOOP-IDX)  TO ERR-RECORD(1:6)
               MOVE WS-TX-RATE(WS-LOOP-IDX)  TO WS-DL-TAX
               WRITE ERR-RECORD
                   AFTER ADVANCING 1 LINE
           END-PERFORM.

      *----------------------------------------------------------------
       CLOSE-ALL-FILES.
           CLOSE PAYFILE
           CLOSE RPTFILE
           CLOSE ERRFILE.

      *----------------------------------------------------------------
       ABEND-ROUTINE.
           DISPLAY 'PAYROLL01 ABENDING - CHECK JES2 SPOOL'
           CLOSE PAYFILE
           CLOSE RPTFILE
           CLOSE ERRFILE
           STOP RUN.

       END PROGRAM PAYROLL01.
