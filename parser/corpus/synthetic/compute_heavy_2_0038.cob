       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0038.
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
       01  WS-VAR-001        PIC 9(3) VALUE ZERO.
       01  WS-VAR-002        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-003        PIC X(20) VALUE ZERO.
       01  WS-VAR-004        PIC 9(3) VALUE ZERO.
       01  WS-VAR-005        PIC X(20) VALUE ZERO.
       01  WS-VAR-006        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-007        PIC 9(5) VALUE ZERO.
       01  WS-VAR-008        PIC 9(3) VALUE ZERO.
       01  WS-VAR-009        PIC 9(5) VALUE ZERO.
       01  WS-VAR-010        PIC 9(3) VALUE ZERO.
       01  WS-VAR-011        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-012        PIC 9(7)V99 VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 - 68.
                  COMPUTE WS-VAR-000 = 30.
                  COMPUTE WS-VAR-001 = WS-VAR-002 - 77.
                  COMPUTE WS-VAR-002 = WS-VAR-003 - 37.
                  COMPUTE WS-VAR-002 = 36.
                  COMPUTE WS-VAR-003 = WS-VAR-004 * 47.
                  COMPUTE WS-VAR-004 = WS-VAR-005 * 88.
                  COMPUTE WS-VAR-004 = 48.
                  COMPUTE WS-VAR-005 = WS-VAR-006 * 89.
                  COMPUTE WS-VAR-006 = WS-VAR-007 + 73.
                  COMPUTE WS-VAR-007 = WS-VAR-008 - 56.
                  COMPUTE WS-VAR-008 = WS-VAR-009 * 35.
                  COMPUTE WS-VAR-008 = 88.
                  COMPUTE WS-VAR-009 = WS-VAR-010 * 40.
                  COMPUTE WS-VAR-010 = WS-VAR-011 * 31.
                  COMPUTE WS-VAR-011 = WS-VAR-012 * 2.
                  COMPUTE WS-VAR-012 = WS-VAR-013 - 94.
                  COMPUTE WS-VAR-012 = 70.
                  COMPUTE WS-VAR-013 = WS-VAR-014 + 26.
                  COMPUTE WS-VAR-013 = 83.           STOP RUN.
