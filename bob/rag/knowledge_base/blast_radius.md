# Blast Radius and Change Propagation in COBOL Systems

## Definition
Blast radius is the number of downstream systems that must be updated, tested, and redeployed when a single COBOL program changes. In IBM Z estates, programs are connected by: COPY members (shared data layouts), CALL statements (runtime dependencies), JCL EXEC PGM= entries (job dependencies), and VSAM file access (shared data stores).

## Score Interpretation
- 0–30: Low blast radius. Change is self-contained. Standard change management applies.
- 31–60: Medium blast radius. Multiple downstream programs or batch jobs affected. Integration testing required. Technical sign-off mandatory.
- 61–100: High blast radius. Core file layout or shared copybook affected. CRO sign-off mandatory under DORA Article 28 before deployment. Parallel testing of all affected programs required.

## CRO Sign-off Threshold
Refinery flags changes with blast radius > 30 for CRO review. This threshold reflects industry practice for regulated financial institutions — any change affecting more than one downstream system in a core banking COBOL estate requires documented officer approval.

## Common High-Blast-Radius Changes
1. Modifying a field in a shared COPY member used by 10+ programs
2. Changing a VSAM record layout shared by batch and online programs
3. Altering a CALL interface (parameter list or data types) in a utility program called by multiple applications
4. Restructuring a working storage area that is passed via LINKAGE SECTION to subprograms
