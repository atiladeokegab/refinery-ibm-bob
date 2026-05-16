       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0056.
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
       01  WS-VAR-001        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-002        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-003        PIC 9(5) VALUE ZERO.
       01  WS-VAR-004        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-005        PIC X(20) VALUE ZERO.
       01  WS-VAR-006        PIC 9(5) VALUE ZERO.
       01  WS-VAR-007        PIC 9(3) VALUE ZERO.
       01  WS-VAR-008        PIC 9(3) VALUE ZERO.
       01  WS-VAR-009        PIC X(20) VALUE ZERO.
       01  WS-VAR-010        PIC X(20) VALUE ZERO.
       01  WS-VAR-011        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-012        PIC X(20) VALUE ZERO.
       01  WS-VAR-013        PIC 9(3) VALUE ZERO.
       01  WS-VAR-014        PIC X(20) VALUE ZERO.
       01  WS-VAR-015        PIC X(20) VALUE ZERO.
       01  WS-VAR-016        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-017        PIC 9(3) VALUE ZERO.
       01  WS-VAR-018        PIC 9(3) VALUE ZERO.
       01  WS-VAR-019        PIC 9(7)V99 VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 + 22.
                  COMPUTE WS-VAR-001 = WS-VAR-002 - 64.
                  COMPUTE WS-VAR-001 = 72.
                  COMPUTE WS-VAR-002 = WS-VAR-003 - 23.
                  COMPUTE WS-VAR-002 = 91.
                  COMPUTE WS-VAR-003 = WS-VAR-004 + 14.
                  COMPUTE WS-VAR-004 = WS-VAR-005 * 31.
                  COMPUTE WS-VAR-005 = WS-VAR-006 - 32.
                  COMPUTE WS-VAR-006 = WS-VAR-007 - 48.
                  COMPUTE WS-VAR-007 = WS-VAR-008 + 28.
                  COMPUTE WS-VAR-008 = WS-VAR-009 - 14.
                  COMPUTE WS-VAR-008 = 38.
                  COMPUTE WS-VAR-009 = WS-VAR-010 + 52.
                  COMPUTE WS-VAR-010 = WS-VAR-011 + 59.
                  COMPUTE WS-VAR-010 = 40.
                  COMPUTE WS-VAR-011 = WS-VAR-012 - 25.
                  COMPUTE WS-VAR-011 = 42.
                  COMPUTE WS-VAR-012 = WS-VAR-013 + 25.
                  COMPUTE WS-VAR-013 = WS-VAR-014 - 68.
                  COMPUTE WS-VAR-014 = WS-VAR-015 - 56.           STOP RUN.
