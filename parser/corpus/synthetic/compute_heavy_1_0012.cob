       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0012.
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
       01  WS-VAR-001        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-002        PIC X(20) VALUE ZERO.
       01  WS-VAR-003        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-004        PIC 9(5) VALUE ZERO.
       01  WS-VAR-005        PIC 9(3) VALUE ZERO.
       01  WS-VAR-006        PIC X(20) VALUE ZERO.
       01  WS-VAR-007        PIC 9(3) VALUE ZERO.
       01  WS-VAR-008        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-009        PIC X(20) VALUE ZERO.
       01  WS-VAR-010        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-011        PIC 9(5) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 - 34.
                  COMPUTE WS-VAR-000 = 66.
                  COMPUTE WS-VAR-001 = WS-VAR-002 - 6.
                  COMPUTE WS-VAR-002 = WS-VAR-003 * 96.
                  COMPUTE WS-VAR-003 = WS-VAR-004 + 46.
                  COMPUTE WS-VAR-004 = WS-VAR-005 + 3.
                  COMPUTE WS-VAR-005 = WS-VAR-006 * 21.
                  COMPUTE WS-VAR-005 = 82.
                  COMPUTE WS-VAR-006 = WS-VAR-007 - 89.
                  COMPUTE WS-VAR-007 = WS-VAR-008 * 27.
                  COMPUTE WS-VAR-007 = 43.
                  COMPUTE WS-VAR-008 = WS-VAR-009 + 35.
                  COMPUTE WS-VAR-008 = 67.
                  COMPUTE WS-VAR-009 = WS-VAR-010 - 85.
                  COMPUTE WS-VAR-010 = WS-VAR-011 * 72.
                  COMPUTE WS-VAR-010 = 39.
                  COMPUTE WS-VAR-011 = WS-VAR-012 * 84.
                  COMPUTE WS-VAR-012 = WS-VAR-013 - 72.
                  COMPUTE WS-VAR-013 = WS-VAR-014 + 95.
                  COMPUTE WS-VAR-014 = WS-VAR-015 + 52.           STOP RUN.
