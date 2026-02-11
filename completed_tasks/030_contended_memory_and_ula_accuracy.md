# Task: Contended Memory and ULA Accuracy

1. [ ] Implement "Contended Memory" logic: Access to RAM 0x4000-0x7FFF should be delayed if ULA is accessing it.
2. [ ] Refine ULA scanline timing: Exact T-state when each pixel is drawn.
3. [ ] Implement "Floating Bus" behavior: Reading from unattached ports should return currently drawing pixel data.
4. [ ] Verify with specific ULA timing tests (e.g. `border.tap` or `floating.tap`).
