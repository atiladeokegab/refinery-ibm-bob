       IDENTIFICATION DIVISION.
       PROGRAM-ID. CMPTH0040.
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
       01  WS-VAR-001        PIC X(20) VALUE ZERO.
       01  WS-VAR-002        PIC X(20) VALUE ZERO.
       01  WS-VAR-003        PIC X(20) VALUE ZERO.
       01  WS-VAR-004        PIC X(20) VALUE ZERO.
       01  WS-VAR-005        PIC 9(3) VALUE ZERO.
       01  WS-VAR-006        PIC 9(3) VALUE ZERO.
       01  WS-VAR-007        PIC 9(5) VALUE ZERO.
       01  WS-VAR-008        PIC X(20) VALUE ZERO.
       01  WS-VAR-009        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-010        PIC X(20) VALUE ZERO.
       01  WS-VAR-011        PIC 9(5) VALUE ZERO.
       01  WS-VAR-012        PIC 9(5) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 + 47.
                  COMPUTE WS-VAR-000 = 47.
                  COMPUTE WS-VAR-001 = WS-VAR-002 * 11.
                  COMPUTE WS-VAR-001 = 90.
                  COMPUTE WS-VAR-002 = WS-VAR-003 + 28.
                  COMPUTE WS-VAR-003 = WS-VAR-004 + 84.
                  COMPUTE WS-VAR-004 = WS-VAR-005 * 22.
                  COMPUTE WS-VAR-005 = WS-VAR-006 * 86.
                  COMPUTE WS-VAR-006 = WS-VAR-007 + 3.
                  COMPUTE WS-VAR-007 = WS-VAR-008 * 62.
                  COMPUTE WS-VAR-007 = 7.
                  COMPUTE WS-VAR-008 = WS-VAR-009 - 47.
                  COMPUTE WS-VAR-009 = WS-VAR-010 - 18.
                  COMPUTE WS-VAR-009 = 41.
                  COMPUTE WS-VAR-010 = WS-VAR-011 * 86.
                  COMPUTE WS-VAR-011 = WS-VAR-012 - 86.
                  COMPUTE WS-VAR-012 = WS-VAR-013 + 74.
                  COMPUTE WS-VAR-013 = WS-VAR-014 + 54.
                  COMPUTE WS-VAR-013 = 85.
                  COMPUTE WS-VAR-014 = WS-VAR-015 - 83.
                  COMPUTE WS-VAR-014 = 24.           STOP RUN.
