# Task: Finalize Z80 Block I/O Flag Accuracy

## Description
The block I/O repeat instructions (INIR, OTIR, INDR, OTDR) are now much closer to 100% accuracy. F5, F3, H, and N flags are mostly correct. The remaining ~500 failures per file are due to the undocumented P/V flag behavior, which seems to depend on a complex interaction between the transferred value, the modifier, and the B register.

## Key Goals
- [ ] Investigate the 4-bit ALU internal state influence on the P/V flag for NMOS Z80.
- [ ] Try the "internal carry" based formulas for P/V.
- [ ] Aim for 100% pass rate in `edb2.json`, `edb3.json`, `edba.json`, and `edbb.json`.
- [ ] Verify if `N` flag is indeed always `val >> 7` or if it's affected by the instruction type (INI vs OUTI).

## Current Status
- F5/F3 from PC: Verified and implemented.
- H cleared during repeat: Verified and implemented for ALL block instructions.
- N preserved during repeat: Verified and implemented.
- Port Address: Fixed! `INI/IND` uses OLD B, `OUTI/OUTD` uses NEW B.
- P/V formula: Implemented `parity(((val + modifier) & 7) ^ B_old ^ h_int)`.
- Progress: ~500 failures per block I/O file (down from ~750). The first few tests in each file now pass.
- New Insight: PV flag behavior is extremely sensitive to which `B` register value is used and how `h_int` is derived. Some cases work with `B_old`, others with `B_after`.

