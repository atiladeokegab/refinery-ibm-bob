       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0063.
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
       01  WS-VAR-000        PIC 9(3) VALUE ZERO.
       01  WS-VAR-001        PIC X(20) VALUE ZERO.
       01  WS-VAR-002        PIC X(20) VALUE ZERO.
       01  WS-VAR-003        PIC X(20) VALUE ZERO.
       01  WS-VAR-004        PIC 9(5) VALUE ZERO.
       01  WS-VAR-005        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-006        PIC 9(5) VALUE ZERO.
       01  WS-VAR-007        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-008        PIC 9(5) VALUE ZERO.
       01  WS-VAR-009        PIC 9(3) VALUE ZERO.
       01  WS-VAR-010        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-011        PIC 9(5) VALUE ZERO.
       01  WS-VAR-012        PIC X(20) VALUE ZERO.
       01  WS-VAR-013        PIC 9(3) VALUE ZERO.
       01  WS-VAR-014        PIC X(20) VALUE ZERO.
       01  WS-VAR-015        PIC 9(5) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 - 17.
                  COMPUTE WS-VAR-000 = 11.
                  COMPUTE WS-VAR-001 = WS-VAR-002 + 3.
                  COMPUTE WS-VAR-001 = 63.
                  COMPUTE WS-VAR-002 = WS-VAR-003 * 5.
                  COMPUTE WS-VAR-002 = 65.
                  COMPUTE WS-VAR-003 = WS-VAR-004 * 72.
                  COMPUTE WS-VAR-004 = WS-VAR-005 * 57.
                  COMPUTE WS-VAR-004 = 69.
                  COMPUTE WS-VAR-005 = WS-VAR-006 - 28.
                  COMPUTE WS-VAR-006 = WS-VAR-007 - 87.
                  COMPUTE WS-VAR-006 = 70.
                  COMPUTE WS-VAR-007 = WS-VAR-008 + 8.
                  COMPUTE WS-VAR-008 = WS-VAR-009 + 11.
                  COMPUTE WS-VAR-009 = WS-VAR-010 * 57.
                  COMPUTE WS-VAR-009 = 47.           STOP RUN.
