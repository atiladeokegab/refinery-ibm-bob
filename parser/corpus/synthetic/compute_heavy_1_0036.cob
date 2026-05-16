       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0036.
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
       01  WS-VAR-001        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-002        PIC X(20) VALUE ZERO.
       01  WS-VAR-003        PIC 9(5) VALUE ZERO.
       01  WS-VAR-004        PIC 9(5) VALUE ZERO.
       01  WS-VAR-005        PIC X(20) VALUE ZERO.
       01  WS-VAR-006        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-007        PIC 9(5) VALUE ZERO.
       01  WS-VAR-008        PIC 9(3) VALUE ZERO.
       01  WS-VAR-009        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-010        PIC 9(7)V99 VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 + 7.
                  COMPUTE WS-VAR-000 = 87.
                  COMPUTE WS-VAR-001 = WS-VAR-002 - 8.
                  COMPUTE WS-VAR-002 = WS-VAR-003 + 3.
                  COMPUTE WS-VAR-002 = 5.
                  COMPUTE WS-VAR-003 = WS-VAR-004 - 69.
                  COMPUTE WS-VAR-004 = WS-VAR-005 * 3.
                  COMPUTE WS-VAR-004 = 28.
                  COMPUTE WS-VAR-005 = WS-VAR-006 + 61.
                  COMPUTE WS-VAR-005 = 75.
                  COMPUTE WS-VAR-006 = WS-VAR-007 * 71.
                  COMPUTE WS-VAR-006 = 30.
                  COMPUTE WS-VAR-007 = WS-VAR-008 + 24.
                  COMPUTE WS-VAR-008 = WS-VAR-009 + 8.
                  COMPUTE WS-VAR-009 = WS-VAR-010 - 90.
                  COMPUTE WS-VAR-009 = 42.
                  COMPUTE WS-VAR-010 = WS-VAR-011 + 53.
                  COMPUTE WS-VAR-010 = 24.
                  COMPUTE WS-VAR-011 = WS-VAR-012 * 65.
                  COMPUTE WS-VAR-011 = 24.           STOP RUN.
