       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0052.
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
       01  WS-VAR-001        PIC X(20) VALUE ZERO.
       01  WS-VAR-002        PIC 9(5) VALUE ZERO.
       01  WS-VAR-003        PIC X(20) VALUE ZERO.
       01  WS-VAR-004        PIC X(20) VALUE ZERO.
       01  WS-VAR-005        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-006        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-007        PIC 9(5) VALUE ZERO.
       01  WS-VAR-008        PIC 9(5) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 * 57.
                  COMPUTE WS-VAR-000 = 51.
                  COMPUTE WS-VAR-001 = WS-VAR-002 + 36.
                  COMPUTE WS-VAR-001 = 49.
                  COMPUTE WS-VAR-002 = WS-VAR-003 * 84.
                  COMPUTE WS-VAR-003 = WS-VAR-004 + 42.
                  COMPUTE WS-VAR-003 = 63.
                  COMPUTE WS-VAR-004 = WS-VAR-005 - 82.
                  COMPUTE WS-VAR-005 = WS-VAR-006 - 55.
                  COMPUTE WS-VAR-005 = 35.
                  COMPUTE WS-VAR-006 = WS-VAR-007 + 88.
                  COMPUTE WS-VAR-007 = WS-VAR-008 - 90.
                  COMPUTE WS-VAR-007 = 73.
                  COMPUTE WS-VAR-008 = WS-VAR-009 + 61.
                  COMPUTE WS-VAR-009 = WS-VAR-010 * 79.
                  COMPUTE WS-VAR-010 = WS-VAR-011 + 51.
                  COMPUTE WS-VAR-011 = WS-VAR-012 - 77.           STOP RUN.
