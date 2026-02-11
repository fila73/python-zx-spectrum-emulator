# Task: Debug 128K Freeze and Audio Crash

1. [ ] Fix `ZeroDivisionError` in `src/ula.py` `render_audio`.
    - Handle case where `cycles_per_frame` (actual cycles) is 0 or very small.
2. [ ] Investigate 128K BASIC freeze.
    - User says entering command freezes it.
    - Check `HALT` implementation and Interrupts in 128K mode.
    - Verify `cpu.interrupt()` logic for 128K (IM 1? Vector?).
    - Verify Stack Pointer in 128K mode (Bank 2/5/etc?).
3. [ ] Verify fix with 128K mode.
