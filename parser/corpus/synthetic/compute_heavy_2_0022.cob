       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0022.
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
       01  WS-VAR-002        PIC 9(5) VALUE ZERO.
       01  WS-VAR-003        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-004        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-005        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-006        PIC 9(5) VALUE ZERO.
       01  WS-VAR-007        PIC X(20) VALUE ZERO.
       01  WS-VAR-008        PIC 9(5) VALUE ZERO.
       01  WS-VAR-009        PIC X(20) VALUE ZERO.
       01  WS-VAR-010        PIC 9(5) VALUE ZERO.
       01  WS-VAR-011        PIC X(20) VALUE ZERO.
       01  WS-VAR-012        PIC 9(5) VALUE ZERO.
       01  WS-VAR-013        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-014        PIC X(20) VALUE ZERO.
       01  WS-VAR-015        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-016        PIC 9(3) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 * 5.
                  COMPUTE WS-VAR-001 = WS-VAR-002 + 49.
                  COMPUTE WS-VAR-001 = 60.
                  COMPUTE WS-VAR-002 = WS-VAR-003 + 23.
                  COMPUTE WS-VAR-003 = WS-VAR-004 - 99.
                  COMPUTE WS-VAR-004 = WS-VAR-005 + 83.
                  COMPUTE WS-VAR-004 = 62.
                  COMPUTE WS-VAR-005 = WS-VAR-006 + 69.
                  COMPUTE WS-VAR-006 = WS-VAR-007 * 68.
                  COMPUTE WS-VAR-007 = WS-VAR-008 + 37.
                  COMPUTE WS-VAR-008 = WS-VAR-009 + 72.
                  COMPUTE WS-VAR-008 = 17.
                  COMPUTE WS-VAR-009 = WS-VAR-010 * 24.
                  COMPUTE WS-VAR-010 = WS-VAR-011 + 26.
                  COMPUTE WS-VAR-011 = WS-VAR-012 + 59.
                  COMPUTE WS-VAR-011 = 30.           STOP RUN.
