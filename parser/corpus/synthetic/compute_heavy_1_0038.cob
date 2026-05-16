       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0038.
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
       01  WS-VAR-001        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-002        PIC X(20) VALUE ZERO.
       01  WS-VAR-003        PIC X(20) VALUE ZERO.
       01  WS-VAR-004        PIC X(20) VALUE ZERO.
       01  WS-VAR-005        PIC X(20) VALUE ZERO.
       01  WS-VAR-006        PIC X(20) VALUE ZERO.
       01  WS-VAR-007        PIC 9(5) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 - 53.
                  COMPUTE WS-VAR-001 = WS-VAR-002 - 41.
                  COMPUTE WS-VAR-002 = WS-VAR-003 + 66.
                  COMPUTE WS-VAR-003 = WS-VAR-004 + 39.
                  COMPUTE WS-VAR-004 = WS-VAR-005 * 17.
                  COMPUTE WS-VAR-005 = WS-VAR-006 + 20.
                  COMPUTE WS-VAR-006 = WS-VAR-007 + 81.
                  COMPUTE WS-VAR-006 = 11.
                  COMPUTE WS-VAR-007 = WS-VAR-008 - 79.
                  COMPUTE WS-VAR-007 = 83.
                  COMPUTE WS-VAR-008 = WS-VAR-009 + 41.
                  COMPUTE WS-VAR-008 = 61.
                  COMPUTE WS-VAR-009 = WS-VAR-010 + 40.
                  COMPUTE WS-VAR-010 = WS-VAR-011 - 71.
                  COMPUTE WS-VAR-011 = WS-VAR-012 + 14.
                  COMPUTE WS-VAR-012 = WS-VAR-013 * 9.
                  COMPUTE WS-VAR-012 = 69.           STOP RUN.
