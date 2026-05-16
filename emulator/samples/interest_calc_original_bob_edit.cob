      ******************************************************************
      * INTCALC  -- Monthly loan interest calculation
      * Standard bank COBOL, 1988. Display-format numerics.
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID.    INTCALC.
       AUTHOR.        CORE-BANKING-SYSTEMS.
       DATE-WRITTEN.  1988-03-14.

       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SOURCE-COMPUTER.  IBM-3090.
       OBJECT-COMPUTER.  IBM-3090.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-ACCOUNT-NO        PIC X(10).
       01  WS-PRINCIPAL         PIC 9(10)V99 COMP-3.
       01  WS-ANNUAL-RATE       PIC 9(3)V9(4) COMP-3.
       01  WS-MONTHLY-INTEREST  PIC 9(10)V99 COMP-3.
       01  WS-NEW-BALANCE       PIC 9(10)V99 COMP-3.
       01  WS-RETURN-CODE       PIC 99 VALUE 0 COMP-3.
           88  WS-OK            VALUE 0.
           88  WS-INVALID-RATE  VALUE 1.
           88  WS-INVALID-PRIN  VALUE 2.

       PROCEDURE DIVISION.
       000-MAIN.
           PERFORM 100-VALIDATE-INPUT
           IF WS-OK
               PERFORM 200-CALC-INTEREST
               PERFORM 300-OUTPUT-RESULT
           END-IF
           STOP RUN.

       100-VALIDATE-INPUT.
           IF WS-PRINCIPAL <= ZEROS
               MOVE 2 TO WS-RETURN-CODE
           END-IF
           IF WS-ANNUAL-RATE <= ZEROS
               OR WS-ANNUAL-RATE > 99.9999
               MOVE 1 TO WS-RETURN-CODE
           END-IF.

       200-CALC-INTEREST.
           COMPUTE WS-MONTHLY-INTEREST =
               WS-PRINCIPAL * (WS-ANNUAL-RATE / 100) / 12
           COMPUTE WS-NEW-BALANCE =
               WS-PRINCIPAL + WS-MONTHLY-INTEREST.

       300-OUTPUT-RESULT.
           DISPLAY 'ACCOUNT:  ' WS-ACCOUNT-NO
           DISPLAY 'BALANCE:  ' WS-PRINCIPAL
           DISPLAY 'INTEREST: ' WS-MONTHLY-INTEREST
           DISPLAY 'NEW BAL:  ' WS-NEW-BALANCE.
