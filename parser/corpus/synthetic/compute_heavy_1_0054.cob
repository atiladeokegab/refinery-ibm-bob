       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0054.
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
       01  WS-VAR-000        PIC 9(5) VALUE ZERO.
       01  WS-VAR-001        PIC 9(3) VALUE ZERO.
       01  WS-VAR-002        PIC 9(5) VALUE ZERO.
       01  WS-VAR-003        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-004        PIC 9(5) VALUE ZERO.
       01  WS-VAR-005        PIC X(20) VALUE ZERO.
       01  WS-VAR-006        PIC 9(3) VALUE ZERO.
       01  WS-VAR-007        PIC X(20) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 * 50.
                  COMPUTE WS-VAR-000 = 5.
                  COMPUTE WS-VAR-001 = WS-VAR-002 + 58.
                  COMPUTE WS-VAR-002 = WS-VAR-003 * 15.
                  COMPUTE WS-VAR-003 = WS-VAR-004 + 99.
                  COMPUTE WS-VAR-004 = WS-VAR-005 * 38.
                  COMPUTE WS-VAR-005 = WS-VAR-006 - 84.
                  COMPUTE WS-VAR-006 = WS-VAR-007 + 9.
                  COMPUTE WS-VAR-007 = WS-VAR-008 * 16.
                  COMPUTE WS-VAR-008 = WS-VAR-009 - 72.
                  COMPUTE WS-VAR-008 = 22.
                  COMPUTE WS-VAR-009 = WS-VAR-010 - 59.
                  COMPUTE WS-VAR-010 = WS-VAR-011 + 25.
                  COMPUTE WS-VAR-010 = 28.
                  COMPUTE WS-VAR-011 = WS-VAR-012 * 67.
                  COMPUTE WS-VAR-011 = 40.
                  COMPUTE WS-VAR-012 = WS-VAR-013 - 34.
                  COMPUTE WS-VAR-012 = 7.           STOP RUN.
