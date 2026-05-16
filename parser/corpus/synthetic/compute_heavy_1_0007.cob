       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0007.
       AUTHOR. ZOPTIMA-GEN.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT INFILE  ASSIGN TO 'INPUT.DAT'
               ORGANIZATION IS SEQUENTIAL.
           SELECT OUTFILE ASSIGN TO 'OUTPUT.DAT'
               ORGANIZATION IS SEQUENTIAL.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-VAR-000        PIC X(20) VALUE ZERO.
       01  WS-VAR-001        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-002        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-003        PIC X(20) VALUE ZERO.
       01  WS-VAR-004        PIC 9(3) VALUE ZERO.
       01  WS-VAR-005        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-006        PIC 9(5) VALUE ZERO.
       01  WS-VAR-007        PIC 9(7)V99 VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 * 3.
                  COMPUTE WS-VAR-000 = 97.
                  COMPUTE WS-VAR-001 = WS-VAR-002 - 46.
                  COMPUTE WS-VAR-002 = WS-VAR-003 + 20.
                  COMPUTE WS-VAR-003 = WS-VAR-004 + 42.
                  COMPUTE WS-VAR-004 = WS-VAR-005 + 86.
                  COMPUTE WS-VAR-004 = 20.
                  COMPUTE WS-VAR-005 = WS-VAR-006 - 19.
                  COMPUTE WS-VAR-006 = WS-VAR-007 * 91.
                  COMPUTE WS-VAR-007 = WS-VAR-008 - 78.
                  COMPUTE WS-VAR-007 = 27.
                  COMPUTE WS-VAR-008 = WS-VAR-009 * 19.           STOP RUN.
