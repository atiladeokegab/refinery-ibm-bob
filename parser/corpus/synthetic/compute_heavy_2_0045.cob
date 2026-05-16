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
       01  WS-VAR-000        PIC 9(3) VALUE ZERO.
       01  WS-VAR-001        PIC X(20) VALUE ZERO.
       01  WS-VAR-002        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-003        PIC 9(5) VALUE ZERO.
       01  WS-VAR-004        PIC 9(7)V99 VALUE ZERO.
       01  WS-VAR-005        PIC X(20) VALUE ZERO.
       01  WS-VAR-006        PIC 9(3) VALUE ZERO.
       01  WS-VAR-007        PIC X(20) VALUE ZERO.
       01  WS-VAR-008        PIC 9(3) VALUE ZERO.
       01  WS-VAR-009        PIC 9(5) VALUE ZERO.
       01  WS-VAR-010        PIC X(20) VALUE ZERO.
       01  WS-VAR-011        PIC 9(3) VALUE ZERO.
       01  WS-VAR-012        PIC X(20) VALUE ZERO.
       01  WS-VAR-013        PIC 9(5) VALUE ZERO.
       01  WS-VAR-014        PIC X(20) VALUE ZERO.
       01  WS-VAR-015        PIC X(20) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
                  COMPUTE WS-VAR-000 = WS-VAR-001 + 7.
                  COMPUTE WS-VAR-000 = 77.
                  COMPUTE WS-VAR-001 = WS-VAR-002 + 3.
                  COMPUTE WS-VAR-002 = WS-VAR-003 - 67.
                  COMPUTE WS-VAR-003 = WS-VAR-004 * 65.
                  COMPUTE WS-VAR-004 = WS-VAR-005 - 2.
                  COMPUTE WS-VAR-005 = WS-VAR-006 + 45.
                  COMPUTE WS-VAR-005 = 8.
                  COMPUTE WS-VAR-006 = WS-VAR-007 - 45.
                  COMPUTE WS-VAR-006 = 66.
                  COMPUTE WS-VAR-007 = WS-VAR-008 - 31.
                  COMPUTE WS-VAR-007 = 83.
                  COMPUTE WS-VAR-008 = WS-VAR-009 + 59.
                  COMPUTE WS-VAR-009 = WS-VAR-010 - 72.
                  COMPUTE WS-VAR-010 = WS-VAR-011 - 57.
                  COMPUTE WS-VAR-011 = WS-VAR-012 * 38.
                  COMPUTE WS-VAR-012 = WS-VAR-013 - 42.
                  COMPUTE WS-VAR-012 = 70.
                  COMPUTE WS-VAR-013 = WS-VAR-014 - 72.
                  COMPUTE WS-VAR-014 = WS-VAR-015 * 35.           STOP RUN.
