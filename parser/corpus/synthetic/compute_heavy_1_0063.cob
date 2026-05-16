       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0063.
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
       01  WS-VAR-001        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-002        PIC 9(5) VALUE ZERO.
       01  WS-VAR-003        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-004        PIC 9(5) VALUE ZERO.
       01  WS-VAR-005        PIC 9(5) VALUE ZERO.
       01  WS-VAR-006        PIC 9(5) VALUE ZERO.
       01  WS-VAR-007        PIC 9(5) VALUE ZERO.
       01  WS-VAR-008        PIC 9(5) VALUE ZERO.
       01  WS-VAR-009        PIC 9(5) VALUE ZERO.
       01  WS-VAR-010        PIC X(20) VALUE ZERO.
       01  WS-VAR-011        PIC 9(3) VALUE ZERO.
       01  WS-VAR-012        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-013        PIC X(20) VALUE ZERO.
       01  WS-VAR-014        PIC 9(5) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 + 83.
                  COMPUTE WS-VAR-001 = WS-VAR-002 * 61.
                  COMPUTE WS-VAR-001 = 77.
                  COMPUTE WS-VAR-002 = WS-VAR-003 * 33.
                  COMPUTE WS-VAR-003 = WS-VAR-004 * 51.
                  COMPUTE WS-VAR-004 = WS-VAR-005 + 53.
                  COMPUTE WS-VAR-005 = WS-VAR-006 - 59.
                  COMPUTE WS-VAR-006 = WS-VAR-007 * 72.
                  COMPUTE WS-VAR-006 = 83.
                  COMPUTE WS-VAR-007 = WS-VAR-008 * 11.
                  COMPUTE WS-VAR-008 = WS-VAR-009 - 79.
                  COMPUTE WS-VAR-008 = 63.
                  COMPUTE WS-VAR-009 = WS-VAR-010 + 94.
                  COMPUTE WS-VAR-010 = WS-VAR-011 - 95.
                  COMPUTE WS-VAR-010 = 82.
                  COMPUTE WS-VAR-011 = WS-VAR-012 - 35.
                  COMPUTE WS-VAR-011 = 33.
                  COMPUTE WS-VAR-012 = WS-VAR-013 + 2.
                  COMPUTE WS-VAR-013 = WS-VAR-014 - 14.           STOP RUN.
