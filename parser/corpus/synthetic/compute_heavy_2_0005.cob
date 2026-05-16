       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0005.
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
       01  WS-VAR-003        PIC 9(3) VALUE ZERO.
       01  WS-VAR-004        PIC X(20) VALUE ZERO.
       01  WS-VAR-005        PIC 9(3) VALUE ZERO.
       01  WS-VAR-006        PIC 9(5) VALUE ZERO.
       01  WS-VAR-007        PIC 9(5) VALUE ZERO.
       01  WS-VAR-008        PIC 9(5) VALUE ZERO.
       01  WS-VAR-009        PIC X(20) VALUE ZERO.
       01  WS-VAR-010        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-011        PIC 9(7)V99 VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 * 27.
                  COMPUTE WS-VAR-001 = WS-VAR-002 - 1.
                  COMPUTE WS-VAR-001 = 40.
                  COMPUTE WS-VAR-002 = WS-VAR-003 + 93.
                  COMPUTE WS-VAR-002 = 63.
                  COMPUTE WS-VAR-003 = WS-VAR-004 + 25.
                  COMPUTE WS-VAR-004 = WS-VAR-005 * 51.
                  COMPUTE WS-VAR-005 = WS-VAR-006 - 97.
                  COMPUTE WS-VAR-006 = WS-VAR-007 - 16.
                  COMPUTE WS-VAR-006 = 11.
                  COMPUTE WS-VAR-007 = WS-VAR-008 - 79.
                  COMPUTE WS-VAR-008 = WS-VAR-009 * 28.
                  COMPUTE WS-VAR-008 = 80.
                  COMPUTE WS-VAR-009 = WS-VAR-010 - 85.
                  COMPUTE WS-VAR-010 = WS-VAR-011 * 93.
                  COMPUTE WS-VAR-011 = WS-VAR-012 - 46.
                  COMPUTE WS-VAR-011 = 48.
                  COMPUTE WS-VAR-012 = WS-VAR-013 - 35.
                  COMPUTE WS-VAR-013 = WS-VAR-014 * 62.
                  COMPUTE WS-VAR-014 = WS-VAR-015 - 54.           STOP RUN.
