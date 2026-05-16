       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0019.
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
       01  WS-VAR-003        PIC X(20) VALUE ZERO.
       01  WS-VAR-004        PIC 9(5) VALUE ZERO.
       01  WS-VAR-005        PIC 9(5) VALUE ZERO.
       01  WS-VAR-006        PIC 9(5) VALUE ZERO.
       01  WS-VAR-007        PIC 9(5) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 * 39.
                  COMPUTE WS-VAR-001 = WS-VAR-002 * 1.
                  COMPUTE WS-VAR-001 = 39.
                  COMPUTE WS-VAR-002 = WS-VAR-003 * 66.
                  COMPUTE WS-VAR-003 = WS-VAR-004 * 70.
                  COMPUTE WS-VAR-004 = WS-VAR-005 - 71.
                  COMPUTE WS-VAR-005 = WS-VAR-006 * 70.
                  COMPUTE WS-VAR-006 = WS-VAR-007 * 81.
                  COMPUTE WS-VAR-007 = WS-VAR-008 + 39.
                  COMPUTE WS-VAR-008 = WS-VAR-009 + 76.
                  COMPUTE WS-VAR-009 = WS-VAR-010 - 21.
                  COMPUTE WS-VAR-010 = WS-VAR-011 * 55.           STOP RUN.
