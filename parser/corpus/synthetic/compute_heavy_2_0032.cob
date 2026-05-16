       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0032.
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
       01  WS-VAR-001        PIC 9(5) VALUE ZERO.
       01  WS-VAR-002        PIC X(20) VALUE ZERO.
       01  WS-VAR-003        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-004        PIC 9(3) VALUE ZERO.
       01  WS-VAR-005        PIC 9(3) VALUE ZERO.
       01  WS-VAR-006        PIC 9(5) VALUE ZERO.
       01  WS-VAR-007        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-008        PIC 9(5) VALUE ZERO.
       01  WS-VAR-009        PIC 9(5) VALUE ZERO.
       01  WS-VAR-010        PIC 9(7)V99 VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 + 49.
                  COMPUTE WS-VAR-001 = WS-VAR-002 + 29.
                  COMPUTE WS-VAR-002 = WS-VAR-003 + 57.
                  COMPUTE WS-VAR-003 = WS-VAR-004 - 84.
                  COMPUTE WS-VAR-004 = WS-VAR-005 - 8.
                  COMPUTE WS-VAR-004 = 59.
                  COMPUTE WS-VAR-005 = WS-VAR-006 * 93.
                  COMPUTE WS-VAR-006 = WS-VAR-007 + 89.
                  COMPUTE WS-VAR-007 = WS-VAR-008 * 53.
                  COMPUTE WS-VAR-008 = WS-VAR-009 * 8.
                  COMPUTE WS-VAR-009 = WS-VAR-010 - 52.
                  COMPUTE WS-VAR-009 = 37.
                  COMPUTE WS-VAR-010 = WS-VAR-011 * 39.
                  COMPUTE WS-VAR-011 = WS-VAR-012 + 54.
                  COMPUTE WS-VAR-012 = WS-VAR-013 + 98.           STOP RUN.
