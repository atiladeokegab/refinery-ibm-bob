       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0006.
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
       01  WS-VAR-001        PIC 9(3) VALUE ZERO.
       01  WS-VAR-002        PIC X(20) VALUE ZERO.
       01  WS-VAR-003        PIC X(20) VALUE ZERO.
       01  WS-VAR-004        PIC 9(5) VALUE ZERO.
       01  WS-VAR-005        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-006        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-007        PIC 9(3) VALUE ZERO.
       01  WS-VAR-008        PIC 9(3) VALUE ZERO.
       01  WS-VAR-009        PIC 9(5) VALUE ZERO.
       01  WS-VAR-010        PIC X(20) VALUE ZERO.
       01  WS-VAR-011        PIC 9(3) VALUE ZERO.
       01  WS-VAR-012        PIC 9(3) VALUE ZERO.
       01  WS-VAR-013        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-014        PIC 9(5) VALUE ZERO.
       01  WS-VAR-015        PIC 9(5) VALUE ZERO.
       01  WS-VAR-016        PIC 9(3) VALUE ZERO.
       01  WS-VAR-017        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-018        PIC 9(3) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 + 9.
                  COMPUTE WS-VAR-001 = WS-VAR-002 * 88.
                  COMPUTE WS-VAR-001 = 38.
                  COMPUTE WS-VAR-002 = WS-VAR-003 + 50.
                  COMPUTE WS-VAR-003 = WS-VAR-004 - 88.
                  COMPUTE WS-VAR-004 = WS-VAR-005 - 68.
                  COMPUTE WS-VAR-004 = 70.
                  COMPUTE WS-VAR-005 = WS-VAR-006 - 97.
                  COMPUTE WS-VAR-005 = 67.
                  COMPUTE WS-VAR-006 = WS-VAR-007 * 32.
                  COMPUTE WS-VAR-007 = WS-VAR-008 + 22.
                  COMPUTE WS-VAR-008 = WS-VAR-009 + 91.
                  COMPUTE WS-VAR-009 = WS-VAR-010 * 46.
                  COMPUTE WS-VAR-010 = WS-VAR-011 - 60.
                  COMPUTE WS-VAR-011 = WS-VAR-012 - 77.
                  COMPUTE WS-VAR-012 = WS-VAR-013 - 24.
                  COMPUTE WS-VAR-013 = WS-VAR-014 - 62.           STOP RUN.
