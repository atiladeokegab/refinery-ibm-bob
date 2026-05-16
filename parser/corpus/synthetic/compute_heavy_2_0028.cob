       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0028.
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
       01  WS-VAR-001        PIC 9(5) VALUE ZERO.
       01  WS-VAR-002        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-003        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-004        PIC 9(5) VALUE ZERO.
       01  WS-VAR-005        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-006        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-007        PIC 9(7)V99 VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 + 10.
                  COMPUTE WS-VAR-000 = 68.
                  COMPUTE WS-VAR-001 = WS-VAR-002 * 99.
                  COMPUTE WS-VAR-001 = 4.
                  COMPUTE WS-VAR-002 = WS-VAR-003 - 38.
                  COMPUTE WS-VAR-002 = 83.
                  COMPUTE WS-VAR-003 = WS-VAR-004 + 76.
                  COMPUTE WS-VAR-004 = WS-VAR-005 + 36.
                  COMPUTE WS-VAR-005 = WS-VAR-006 * 86.
                  COMPUTE WS-VAR-006 = WS-VAR-007 + 53.
                  COMPUTE WS-VAR-006 = 21.
                  COMPUTE WS-VAR-007 = WS-VAR-008 * 80.           STOP RUN.
