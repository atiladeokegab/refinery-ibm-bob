       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0060.
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
       01  WS-VAR-000        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-001        PIC 9(5) VALUE ZERO.
       01  WS-VAR-002        PIC 9(5) VALUE ZERO.
       01  WS-VAR-003        PIC X(20) VALUE ZERO.
       01  WS-VAR-004        PIC 9(5) VALUE ZERO.
       01  WS-VAR-005        PIC X(20) VALUE ZERO.
       01  WS-VAR-006        PIC 9(5) VALUE ZERO.
       01  WS-VAR-007        PIC 9(5) VALUE ZERO.
       01  WS-VAR-008        PIC X(20) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 - 19.
                  COMPUTE WS-VAR-001 = WS-VAR-002 - 38.
                  COMPUTE WS-VAR-002 = WS-VAR-003 + 14.
                  COMPUTE WS-VAR-003 = WS-VAR-004 * 6.
                  COMPUTE WS-VAR-004 = WS-VAR-005 * 37.
                  COMPUTE WS-VAR-005 = WS-VAR-006 + 1.
                  COMPUTE WS-VAR-006 = WS-VAR-007 + 95.
                  COMPUTE WS-VAR-007 = WS-VAR-008 - 72.
                  COMPUTE WS-VAR-008 = WS-VAR-009 + 2.
                  COMPUTE WS-VAR-009 = WS-VAR-010 * 11.
                  COMPUTE WS-VAR-010 = WS-VAR-011 * 82.
                  COMPUTE WS-VAR-010 = 36.
                  COMPUTE WS-VAR-011 = WS-VAR-012 - 80.
                  COMPUTE WS-VAR-011 = 32.
                  COMPUTE WS-VAR-012 = WS-VAR-013 + 56.
                  COMPUTE WS-VAR-012 = 96.
                  COMPUTE WS-VAR-013 = WS-VAR-014 * 32.
                  COMPUTE WS-VAR-014 = WS-VAR-015 * 80.           STOP RUN.
