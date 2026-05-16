       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0024.
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
       01  WS-VAR-002        PIC X(20) VALUE ZERO.
       01  WS-VAR-003        PIC 9(3) VALUE ZERO.
       01  WS-VAR-004        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-005        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-006        PIC 9(5) VALUE ZERO.
       01  WS-VAR-007        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-008        PIC 9(7)V99 VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 + 36.
                  COMPUTE WS-VAR-001 = WS-VAR-002 + 42.
                  COMPUTE WS-VAR-002 = WS-VAR-003 * 83.
                  COMPUTE WS-VAR-003 = WS-VAR-004 - 78.
                  COMPUTE WS-VAR-004 = WS-VAR-005 * 87.
                  COMPUTE WS-VAR-005 = WS-VAR-006 - 68.
                  COMPUTE WS-VAR-006 = WS-VAR-007 - 69.
                  COMPUTE WS-VAR-007 = WS-VAR-008 * 29.
                  COMPUTE WS-VAR-008 = WS-VAR-009 + 18.
                  COMPUTE WS-VAR-009 = WS-VAR-010 + 15.
                  COMPUTE WS-VAR-009 = 56.
                  COMPUTE WS-VAR-010 = WS-VAR-011 * 36.
                  COMPUTE WS-VAR-010 = 69.
                  COMPUTE WS-VAR-011 = WS-VAR-012 * 35.
                  COMPUTE WS-VAR-011 = 17.
                  COMPUTE WS-VAR-012 = WS-VAR-013 * 52.
                  COMPUTE WS-VAR-012 = 48.           STOP RUN.
