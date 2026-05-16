       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0016.
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
       01  WS-VAR-002        PIC 9(5) VALUE ZERO.
       01  WS-VAR-003        PIC X(20) VALUE ZERO.
       01  WS-VAR-004        PIC X(20) VALUE ZERO.
       01  WS-VAR-005        PIC 9(3) VALUE ZERO.
       01  WS-VAR-006        PIC 9(5) VALUE ZERO.
       01  WS-VAR-007        PIC X(20) VALUE ZERO.
       01  WS-VAR-008        PIC X(20) VALUE ZERO.
       01  WS-VAR-009        PIC 9(5) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 + 37.
                  COMPUTE WS-VAR-000 = 8.
                  COMPUTE WS-VAR-001 = WS-VAR-002 * 69.
                  COMPUTE WS-VAR-002 = WS-VAR-003 * 12.
                  COMPUTE WS-VAR-003 = WS-VAR-004 + 87.
                  COMPUTE WS-VAR-003 = 91.
                  COMPUTE WS-VAR-004 = WS-VAR-005 - 56.
                  COMPUTE WS-VAR-004 = 35.
                  COMPUTE WS-VAR-005 = WS-VAR-006 - 13.
                  COMPUTE WS-VAR-006 = WS-VAR-007 - 67.
                  COMPUTE WS-VAR-007 = WS-VAR-008 - 91.
                  COMPUTE WS-VAR-008 = WS-VAR-009 - 29.
                  COMPUTE WS-VAR-008 = 62.
                  COMPUTE WS-VAR-009 = WS-VAR-010 + 6.
                  COMPUTE WS-VAR-010 = WS-VAR-011 - 27.
                  COMPUTE WS-VAR-010 = 7.
                  COMPUTE WS-VAR-011 = WS-VAR-012 + 79.
                  COMPUTE WS-VAR-012 = WS-VAR-013 + 98.
                  COMPUTE WS-VAR-013 = WS-VAR-014 + 70.           STOP RUN.
