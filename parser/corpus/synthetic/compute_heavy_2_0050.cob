       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0050.
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
       01  WS-VAR-000        PIC X(20) VALUE ZERO.
       01  WS-VAR-001        PIC 9(3) VALUE ZERO.
       01  WS-VAR-002        PIC 9(3) VALUE ZERO.
       01  WS-VAR-003        PIC 9(3) VALUE ZERO.
       01  WS-VAR-004        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-005        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-006        PIC 9(3) VALUE ZERO.
       01  WS-VAR-007        PIC 9(3) VALUE ZERO.
       01  WS-VAR-008        PIC X(20) VALUE ZERO.
       01  WS-VAR-009        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-010        PIC 9(3) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 - 22.
                  COMPUTE WS-VAR-001 = WS-VAR-002 + 48.
                  COMPUTE WS-VAR-002 = WS-VAR-003 - 60.
                  COMPUTE WS-VAR-002 = 48.
                  COMPUTE WS-VAR-003 = WS-VAR-004 * 94.
                  COMPUTE WS-VAR-004 = WS-VAR-005 + 64.
                  COMPUTE WS-VAR-004 = 94.
                  COMPUTE WS-VAR-005 = WS-VAR-006 * 37.
                  COMPUTE WS-VAR-005 = 81.
                  COMPUTE WS-VAR-006 = WS-VAR-007 * 1.
                  COMPUTE WS-VAR-006 = 17.
                  COMPUTE WS-VAR-007 = WS-VAR-008 + 12.
                  COMPUTE WS-VAR-007 = 93.
                  COMPUTE WS-VAR-008 = WS-VAR-009 * 24.
                  COMPUTE WS-VAR-009 = WS-VAR-010 * 46.
                  COMPUTE WS-VAR-010 = WS-VAR-011 - 11.
                  COMPUTE WS-VAR-011 = WS-VAR-012 + 87.
                  COMPUTE WS-VAR-012 = WS-VAR-013 - 93.
                  COMPUTE WS-VAR-012 = 53.
                  COMPUTE WS-VAR-013 = WS-VAR-014 + 8.           STOP RUN.
