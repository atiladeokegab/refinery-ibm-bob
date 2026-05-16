       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0004.
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
       01  WS-VAR-004        PIC 9(3) VALUE ZERO.
       01  WS-VAR-005        PIC 9(5) VALUE ZERO.
       01  WS-VAR-006        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-007        PIC 9(5) VALUE ZERO.
       01  WS-VAR-008        PIC X(20) VALUE ZERO.
       01  WS-VAR-009        PIC X(20) VALUE ZERO.
       01  WS-VAR-010        PIC X(20) VALUE ZERO.
       01  WS-VAR-011        PIC 9(5) VALUE ZERO.
       01  WS-VAR-012        PIC 9(3) VALUE ZERO.
       01  WS-VAR-013        PIC X(20) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 - 3.
                  COMPUTE WS-VAR-001 = WS-VAR-002 - 52.
                  COMPUTE WS-VAR-001 = 26.
                  COMPUTE WS-VAR-002 = WS-VAR-003 * 42.
                  COMPUTE WS-VAR-003 = WS-VAR-004 - 44.
                  COMPUTE WS-VAR-003 = 87.
                  COMPUTE WS-VAR-004 = WS-VAR-005 - 13.
                  COMPUTE WS-VAR-005 = WS-VAR-006 * 45.
                  COMPUTE WS-VAR-006 = WS-VAR-007 * 99.
                  COMPUTE WS-VAR-006 = 93.
                  COMPUTE WS-VAR-007 = WS-VAR-008 + 6.
                  COMPUTE WS-VAR-007 = 22.
                  COMPUTE WS-VAR-008 = WS-VAR-009 + 69.
                  COMPUTE WS-VAR-008 = 43.
                  COMPUTE WS-VAR-009 = WS-VAR-010 * 77.
                  COMPUTE WS-VAR-010 = WS-VAR-011 - 48.
                  COMPUTE WS-VAR-011 = WS-VAR-012 + 38.
                  COMPUTE WS-VAR-012 = WS-VAR-013 * 78.
                  COMPUTE WS-VAR-013 = WS-VAR-014 * 18.
                  COMPUTE WS-VAR-014 = WS-VAR-015 - 14.
                  COMPUTE WS-VAR-014 = 10.           STOP RUN.
