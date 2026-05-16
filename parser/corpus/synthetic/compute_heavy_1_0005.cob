       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0005.
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
       01  WS-VAR-002        PIC X(20) VALUE ZERO.
       01  WS-VAR-003        PIC 9(3) VALUE ZERO.
       01  WS-VAR-004        PIC 9(3) VALUE ZERO.
       01  WS-VAR-005        PIC X(20) VALUE ZERO.
       01  WS-VAR-006        PIC 9(3) VALUE ZERO.
       01  WS-VAR-007        PIC 9(5) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 - 6.
                  COMPUTE WS-VAR-000 = 86.
                  COMPUTE WS-VAR-001 = WS-VAR-002 + 2.
                  COMPUTE WS-VAR-002 = WS-VAR-003 + 6.
                  COMPUTE WS-VAR-002 = 76.
                  COMPUTE WS-VAR-003 = WS-VAR-004 + 54.
                  COMPUTE WS-VAR-003 = 22.
                  COMPUTE WS-VAR-004 = WS-VAR-005 + 88.
                  COMPUTE WS-VAR-004 = 14.
                  COMPUTE WS-VAR-005 = WS-VAR-006 - 56.
                  COMPUTE WS-VAR-006 = WS-VAR-007 - 70.
                  COMPUTE WS-VAR-007 = WS-VAR-008 - 92.
                  COMPUTE WS-VAR-008 = WS-VAR-009 * 27.           STOP RUN.
