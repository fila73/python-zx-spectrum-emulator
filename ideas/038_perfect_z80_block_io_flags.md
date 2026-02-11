# Task: Achieve 100% Z80 Block I/O Flag Accuracy

## Description
The block I/O instructions (INIR, OTIR, INDR, OTDR) are currently at ~50% accuracy. The remaining failures are due to subtle PV flag behavior differences between NMOS Z80 versions or very specific internal state interactions.

## Key Goals
- [ ] Resolve the remaining ~500 failures in `edb2.json`, `edb3.json`, `edba.json`, and `edbb.json`.
- [ ] Investigate if `B` register value used for PV XORing depends on the result of the `val + modifier` addition (e.g., using `B_old` if carry occurred, `B_new` otherwise).
- [ ] Verify the `h_int` calculation logic against silicon-accurate sources like Z80 Explorer.
- [ ] Consider if the ULA contention affects internal CPU registers during block I/O.

## Current Status
- S, Z, F5, F3, N, H, C flags are largely correct.
- PV flag uses `parity(((val + modifier) & 7) ^ B_old ^ h_int)`.
- Accuracy: ~50%.
