       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0032.
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
       01  WS-VAR-002        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-003        PIC 9(5) VALUE ZERO.
       01  WS-VAR-004        PIC X(20) VALUE ZERO.
       01  WS-VAR-005        PIC 9(3) VALUE ZERO.
       01  WS-VAR-006        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-007        PIC 9(5) VALUE ZERO.
       01  WS-VAR-008        PIC X(20) VALUE ZERO.
       01  WS-VAR-009        PIC 9(3) VALUE ZERO.
       01  WS-VAR-010        PIC X(20) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 + 53.
                  COMPUTE WS-VAR-000 = 71.
                  COMPUTE WS-VAR-001 = WS-VAR-002 * 93.
                  COMPUTE WS-VAR-001 = 27.
                  COMPUTE WS-VAR-002 = WS-VAR-003 - 13.
                  COMPUTE WS-VAR-003 = WS-VAR-004 * 7.
                  COMPUTE WS-VAR-004 = WS-VAR-005 * 27.
                  COMPUTE WS-VAR-004 = 41.
                  COMPUTE WS-VAR-005 = WS-VAR-006 - 44.
                  COMPUTE WS-VAR-006 = WS-VAR-007 + 18.
                  COMPUTE WS-VAR-007 = WS-VAR-008 * 47.
                  COMPUTE WS-VAR-007 = 41.
                  COMPUTE WS-VAR-008 = WS-VAR-009 * 54.
                  COMPUTE WS-VAR-008 = 72.
                  COMPUTE WS-VAR-009 = WS-VAR-010 * 6.
                  COMPUTE WS-VAR-010 = WS-VAR-011 * 85.
                  COMPUTE WS-VAR-011 = WS-VAR-012 + 55.           STOP RUN.
