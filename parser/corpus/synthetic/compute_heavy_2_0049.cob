       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0049.
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
       01  WS-VAR-001        PIC X(20) VALUE ZERO.
       01  WS-VAR-002        PIC 9(3) VALUE ZERO.
       01  WS-VAR-003        PIC X(20) VALUE ZERO.
       01  WS-VAR-004        PIC 9(3) VALUE ZERO.
       01  WS-VAR-005        PIC X(20) VALUE ZERO.
       01  WS-VAR-006        PIC X(20) VALUE ZERO.
       01  WS-VAR-007        PIC 9(7)V99 VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 + 72.
                  COMPUTE WS-VAR-001 = WS-VAR-002 + 67.
                  COMPUTE WS-VAR-002 = WS-VAR-003 + 77.
                  COMPUTE WS-VAR-003 = WS-VAR-004 + 6.
                  COMPUTE WS-VAR-003 = 75.
                  COMPUTE WS-VAR-004 = WS-VAR-005 - 21.
                  COMPUTE WS-VAR-004 = 13.
                  COMPUTE WS-VAR-005 = WS-VAR-006 * 15.
                  COMPUTE WS-VAR-006 = WS-VAR-007 - 1.
                  COMPUTE WS-VAR-007 = WS-VAR-008 - 95.
                  COMPUTE WS-VAR-008 = WS-VAR-009 - 25.
                  COMPUTE WS-VAR-009 = WS-VAR-010 + 24.
                  COMPUTE WS-VAR-010 = WS-VAR-011 - 93.
                  COMPUTE WS-VAR-011 = WS-VAR-012 * 91.
                  COMPUTE WS-VAR-012 = WS-VAR-013 + 79.           STOP RUN.
