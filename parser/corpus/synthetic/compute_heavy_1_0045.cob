       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0045.
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
       01  WS-VAR-002        PIC 9(3) VALUE ZERO.
       01  WS-VAR-003        PIC 9(3) VALUE ZERO.
       01  WS-VAR-004        PIC X(20) VALUE ZERO.
       01  WS-VAR-005        PIC X(20) VALUE ZERO.
       01  WS-VAR-006        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-007        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-008        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-009        PIC 9(7)V99 VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 + 80.
                  COMPUTE WS-VAR-001 = WS-VAR-002 - 4.
                  COMPUTE WS-VAR-002 = WS-VAR-003 * 77.
                  COMPUTE WS-VAR-003 = WS-VAR-004 + 53.
                  COMPUTE WS-VAR-004 = WS-VAR-005 + 37.
                  COMPUTE WS-VAR-005 = WS-VAR-006 - 90.
                  COMPUTE WS-VAR-006 = WS-VAR-007 + 23.
                  COMPUTE WS-VAR-007 = WS-VAR-008 * 45.
                  COMPUTE WS-VAR-008 = WS-VAR-009 + 79.
                  COMPUTE WS-VAR-008 = 79.
                  COMPUTE WS-VAR-009 = WS-VAR-010 - 41.
                  COMPUTE WS-VAR-009 = 38.
                  COMPUTE WS-VAR-010 = WS-VAR-011 - 13.
                  COMPUTE WS-VAR-010 = 45.
                  COMPUTE WS-VAR-011 = WS-VAR-012 - 12.
                  COMPUTE WS-VAR-012 = WS-VAR-013 * 15.           STOP RUN.
