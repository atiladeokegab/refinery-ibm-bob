       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0057.
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
       01  WS-VAR-001        PIC 9(3) VALUE ZERO.
       01  WS-VAR-002        PIC X(20) VALUE ZERO.
       01  WS-VAR-003        PIC 9(5) VALUE ZERO.
       01  WS-VAR-004        PIC X(20) VALUE ZERO.
       01  WS-VAR-005        PIC 9(5) VALUE ZERO.
       01  WS-VAR-006        PIC X(20) VALUE ZERO.
       01  WS-VAR-007        PIC X(20) VALUE ZERO.
       01  WS-VAR-008        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-009        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-010        PIC 9(3) VALUE ZERO.
       01  WS-VAR-011        PIC X(20) VALUE ZERO.
       01  WS-VAR-012        PIC 9(3) VALUE ZERO.
       01  WS-VAR-013        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-014        PIC 9(3) VALUE ZERO.
       01  WS-VAR-015        PIC 9(3) VALUE ZERO.
       01  WS-VAR-016        PIC 9(5) VALUE ZERO.
       01  WS-VAR-017        PIC X(20) VALUE ZERO.
       01  WS-VAR-018        PIC 9(5) VALUE ZERO.
       01  WS-VAR-019        PIC X(20) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 - 17.
                  COMPUTE WS-VAR-001 = WS-VAR-002 * 64.
                  COMPUTE WS-VAR-002 = WS-VAR-003 * 56.
                  COMPUTE WS-VAR-002 = 57.
                  COMPUTE WS-VAR-003 = WS-VAR-004 - 34.
                  COMPUTE WS-VAR-004 = WS-VAR-005 + 73.
                  COMPUTE WS-VAR-005 = WS-VAR-006 + 80.
                  COMPUTE WS-VAR-005 = 77.
                  COMPUTE WS-VAR-006 = WS-VAR-007 - 81.
                  COMPUTE WS-VAR-006 = 54.
                  COMPUTE WS-VAR-007 = WS-VAR-008 - 76.
                  COMPUTE WS-VAR-007 = 98.
                  COMPUTE WS-VAR-008 = WS-VAR-009 + 59.           STOP RUN.
