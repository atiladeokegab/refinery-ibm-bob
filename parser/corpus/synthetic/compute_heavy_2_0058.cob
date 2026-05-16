       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0058.
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
       01  WS-VAR-001        PIC X(20) VALUE ZERO.
       01  WS-VAR-002        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-003        PIC 9(3) VALUE ZERO.
       01  WS-VAR-004        PIC X(20) VALUE ZERO.
       01  WS-VAR-005        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-006        PIC X(20) VALUE ZERO.
       01  WS-VAR-007        PIC 9(5) VALUE ZERO.
       01  WS-VAR-008        PIC X(20) VALUE ZERO.
       01  WS-VAR-009        PIC X(20) VALUE ZERO.
       01  WS-VAR-010        PIC 9(3) VALUE ZERO.
       01  WS-VAR-011        PIC 9(3) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 * 3.
                  COMPUTE WS-VAR-000 = 84.
                  COMPUTE WS-VAR-001 = WS-VAR-002 + 57.
                  COMPUTE WS-VAR-002 = WS-VAR-003 * 82.
                  COMPUTE WS-VAR-002 = 61.
                  COMPUTE WS-VAR-003 = WS-VAR-004 * 77.
                  COMPUTE WS-VAR-004 = WS-VAR-005 - 9.
                  COMPUTE WS-VAR-005 = WS-VAR-006 - 86.
                  COMPUTE WS-VAR-006 = WS-VAR-007 - 25.
                  COMPUTE WS-VAR-006 = 54.
                  COMPUTE WS-VAR-007 = WS-VAR-008 - 13.
                  COMPUTE WS-VAR-008 = WS-VAR-009 * 4.
                  COMPUTE WS-VAR-009 = WS-VAR-010 + 37.
                  COMPUTE WS-VAR-009 = 3.           STOP RUN.
