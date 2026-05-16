       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0062.
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
       01  WS-VAR-001        PIC X(20) VALUE ZERO.
       01  WS-VAR-002        PIC 9(3) VALUE ZERO.
       01  WS-VAR-003        PIC 9(3) VALUE ZERO.
       01  WS-VAR-004        PIC X(20) VALUE ZERO.
       01  WS-VAR-005        PIC X(20) VALUE ZERO.
       01  WS-VAR-006        PIC X(20) VALUE ZERO.
       01  WS-VAR-007        PIC X(20) VALUE ZERO.
       01  WS-VAR-008        PIC 9(3) VALUE ZERO.
       01  WS-VAR-009        PIC 9(3) VALUE ZERO.
       01  WS-VAR-010        PIC 9(3) VALUE ZERO.
       01  WS-VAR-011        PIC 9(3) VALUE ZERO.
       01  WS-VAR-012        PIC 9(5) VALUE ZERO.
       01  WS-VAR-013        PIC 9(5) VALUE ZERO.
       01  WS-VAR-014        PIC X(20) VALUE ZERO.
       01  WS-VAR-015        PIC 9(5) VALUE ZERO.
       01  WS-VAR-016        PIC 9(5) VALUE ZERO.
       01  WS-VAR-017        PIC 9(5) VALUE ZERO.
       01  WS-VAR-018        PIC 9(3) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 - 58.
                  COMPUTE WS-VAR-000 = 46.
                  COMPUTE WS-VAR-001 = WS-VAR-002 - 12.
                  COMPUTE WS-VAR-002 = WS-VAR-003 * 47.
                  COMPUTE WS-VAR-003 = WS-VAR-004 * 64.
                  COMPUTE WS-VAR-004 = WS-VAR-005 * 79.
                  COMPUTE WS-VAR-005 = WS-VAR-006 * 76.
                  COMPUTE WS-VAR-006 = WS-VAR-007 + 50.
                  COMPUTE WS-VAR-007 = WS-VAR-008 + 33.
                  COMPUTE WS-VAR-007 = 94.
                  COMPUTE WS-VAR-008 = WS-VAR-009 * 63.
                  COMPUTE WS-VAR-009 = WS-VAR-010 - 17.
                  COMPUTE WS-VAR-010 = WS-VAR-011 - 71.
                  COMPUTE WS-VAR-011 = WS-VAR-012 + 44.
                  COMPUTE WS-VAR-012 = WS-VAR-013 + 17.
                  COMPUTE WS-VAR-013 = WS-VAR-014 * 26.
                  COMPUTE WS-VAR-014 = WS-VAR-015 * 94.           STOP RUN.
