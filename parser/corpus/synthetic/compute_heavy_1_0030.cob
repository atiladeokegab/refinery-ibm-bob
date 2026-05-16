       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0030.
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
       01  WS-VAR-002        PIC 9(3) VALUE ZERO.
       01  WS-VAR-003        PIC X(20) VALUE ZERO.
       01  WS-VAR-004        PIC X(20) VALUE ZERO.
       01  WS-VAR-005        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-006        PIC X(20) VALUE ZERO.
       01  WS-VAR-007        PIC 9(5) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 - 28.
                  COMPUTE WS-VAR-001 = WS-VAR-002 - 69.
                  COMPUTE WS-VAR-002 = WS-VAR-003 + 13.
                  COMPUTE WS-VAR-003 = WS-VAR-004 - 6.
                  COMPUTE WS-VAR-004 = WS-VAR-005 + 25.
                  COMPUTE WS-VAR-005 = WS-VAR-006 * 25.
                  COMPUTE WS-VAR-006 = WS-VAR-007 + 47.
                  COMPUTE WS-VAR-006 = 85.
                  COMPUTE WS-VAR-007 = WS-VAR-008 + 76.
                  COMPUTE WS-VAR-008 = WS-VAR-009 - 7.
                  COMPUTE WS-VAR-008 = 79.
                  COMPUTE WS-VAR-009 = WS-VAR-010 + 23.
                  COMPUTE WS-VAR-010 = WS-VAR-011 - 37.
                  COMPUTE WS-VAR-010 = 65.
                  COMPUTE WS-VAR-011 = WS-VAR-012 * 9.
                  COMPUTE WS-VAR-012 = WS-VAR-013 * 52.
                  COMPUTE WS-VAR-013 = WS-VAR-014 - 83.
                  COMPUTE WS-VAR-014 = WS-VAR-015 - 46.           STOP RUN.
