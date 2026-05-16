       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0060.
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
       01  WS-VAR-001        PIC 9(5) VALUE ZERO.
       01  WS-VAR-002        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-003        PIC 9(3) VALUE ZERO.
       01  WS-VAR-004        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-005        PIC X(20) VALUE ZERO.
       01  WS-VAR-006        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-007        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-008        PIC X(20) VALUE ZERO.
       01  WS-VAR-009        PIC 9(7)V99 VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 + 15.
                  COMPUTE WS-VAR-000 = 50.
                  COMPUTE WS-VAR-001 = WS-VAR-002 + 8.
                  COMPUTE WS-VAR-001 = 60.
                  COMPUTE WS-VAR-002 = WS-VAR-003 * 71.
                  COMPUTE WS-VAR-003 = WS-VAR-004 + 4.
                  COMPUTE WS-VAR-003 = 68.
                  COMPUTE WS-VAR-004 = WS-VAR-005 * 61.
                  COMPUTE WS-VAR-005 = WS-VAR-006 * 46.
                  COMPUTE WS-VAR-006 = WS-VAR-007 - 44.
                  COMPUTE WS-VAR-007 = WS-VAR-008 - 84.
                  COMPUTE WS-VAR-007 = 30.
                  COMPUTE WS-VAR-008 = WS-VAR-009 - 93.
                  COMPUTE WS-VAR-009 = WS-VAR-010 - 55.
                  COMPUTE WS-VAR-010 = WS-VAR-011 * 94.
                  COMPUTE WS-VAR-011 = WS-VAR-012 + 35.
                  COMPUTE WS-VAR-011 = 7.
                  COMPUTE WS-VAR-012 = WS-VAR-013 - 43.
                  COMPUTE WS-VAR-013 = WS-VAR-014 * 9.
                  COMPUTE WS-VAR-014 = WS-VAR-015 * 41.           STOP RUN.
