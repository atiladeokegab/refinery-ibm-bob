# VSAM File Layout and Downstream System Risk

## VSAM Overview
VSAM (Virtual Storage Access Method) is IBM's high-performance file system for mainframe batch and online workloads. VSAM files store records in fixed or variable-length format. The record layout is implicitly defined by the COBOL programs that access the file — there is no schema enforcement at the file level.

## Layout Sensitivity
Any change to the byte length, order, or type of fields in a VSAM record definition immediately breaks all programs that read or write that file, unless all programs are updated and redeployed simultaneously. This is the primary source of blast radius in COBOL change management.

## Blast Radius Calculation
Blast radius measures how many downstream systems depend on a changed VSAM file layout. A score above 30/100 means multiple batch jobs or online transactions share the file. A score above 70/100 means a core banking or insurance file is affected — regulatory sign-off is mandatory before deployment.

## Common Failure Mode
IBM Bob may optimise a COMPUTE statement that writes to a VSAM field, changing the field's PICTURE clause for performance. If that field is in a shared copybook, every program using that copybook must be updated. Deploying only the changed program creates a binary mismatch that causes corrupted records with no runtime exception.
