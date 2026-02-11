# Task 039: Fix Emulator Timing to 50Hz

## Description
The emulator needs to run at the correct Sinclair ZX Spectrum speed, which is approximately 50Hz (50 frames per second). Currently, it might be running as fast as the host CPU allows, or using a less precise timing method.

## Requirements
- Target exactly 50 frames per second (approx 20ms per frame).
- Ensure each frame executes the correct number of Z80 T-states (approx 69888 for 48K model, 70908 for 128K).
- Use a high-precision timer to avoid drift.
- Handle cases where the host is too slow (frame skipping) or too fast (yielding/sleeping).

## Status
- [ ] Implement frame timing loop.
- [ ] Verify T-states per frame.
- [ ] Test on 48K and 128K modes.
