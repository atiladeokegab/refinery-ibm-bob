       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0017.
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
       01  WS-VAR-001        PIC 9(5) VALUE ZERO.
       01  WS-VAR-002        PIC 9(5) VALUE ZERO.
       01  WS-VAR-003        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-004        PIC 9(5) VALUE ZERO.
       01  WS-VAR-005        PIC 9(3) VALUE ZERO.
       01  WS-VAR-006        PIC X(20) VALUE ZERO.
       01  WS-VAR-007        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-008        PIC X(20) VALUE ZERO.
       01  WS-VAR-009        PIC X(20) VALUE ZERO.
       01  WS-VAR-010        PIC X(20) VALUE ZERO.
       01  WS-VAR-011        PIC 9(3) VALUE ZERO.
       01  WS-VAR-012        PIC X(20) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 - 53.
                  COMPUTE WS-VAR-000 = 9.
                  COMPUTE WS-VAR-001 = WS-VAR-002 - 6.
                  COMPUTE WS-VAR-002 = WS-VAR-003 * 84.
                  COMPUTE WS-VAR-003 = WS-VAR-004 - 39.
                  COMPUTE WS-VAR-004 = WS-VAR-005 * 42.
                  COMPUTE WS-VAR-005 = WS-VAR-006 + 65.
                  COMPUTE WS-VAR-006 = WS-VAR-007 - 20.
                  COMPUTE WS-VAR-007 = WS-VAR-008 - 42.
                  COMPUTE WS-VAR-008 = WS-VAR-009 - 58.           STOP RUN.
