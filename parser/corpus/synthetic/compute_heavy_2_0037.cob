       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0037.
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
       01  WS-VAR-004        PIC 9(3) VALUE ZERO.
       01  WS-VAR-005        PIC X(20) VALUE ZERO.
       01  WS-VAR-006        PIC X(20) VALUE ZERO.
       01  WS-VAR-007        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-008        PIC 9(3) VALUE ZERO.
       01  WS-VAR-009        PIC 9(3) VALUE ZERO.
       01  WS-VAR-010        PIC 9(5) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 - 53.
                  COMPUTE WS-VAR-000 = 58.
                  COMPUTE WS-VAR-001 = WS-VAR-002 * 19.
                  COMPUTE WS-VAR-002 = WS-VAR-003 - 60.
                  COMPUTE WS-VAR-003 = WS-VAR-004 * 35.
                  COMPUTE WS-VAR-004 = WS-VAR-005 - 55.
                  COMPUTE WS-VAR-004 = 64.
                  COMPUTE WS-VAR-005 = WS-VAR-006 - 82.
                  COMPUTE WS-VAR-005 = 61.
                  COMPUTE WS-VAR-006 = WS-VAR-007 + 49.
                  COMPUTE WS-VAR-006 = 33.
                  COMPUTE WS-VAR-007 = WS-VAR-008 - 39.
                  COMPUTE WS-VAR-007 = 82.
                  COMPUTE WS-VAR-008 = WS-VAR-009 + 54.
                  COMPUTE WS-VAR-008 = 24.
                  COMPUTE WS-VAR-009 = WS-VAR-010 - 22.
                  COMPUTE WS-VAR-009 = 69.
                  COMPUTE WS-VAR-010 = WS-VAR-011 * 29.
                  COMPUTE WS-VAR-010 = 81.
                  COMPUTE WS-VAR-011 = WS-VAR-012 + 10.
                  COMPUTE WS-VAR-012 = WS-VAR-013 - 68.
                  COMPUTE WS-VAR-013 = WS-VAR-014 + 97.           STOP RUN.
