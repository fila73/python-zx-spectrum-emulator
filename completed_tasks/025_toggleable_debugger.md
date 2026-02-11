# Task: Toggleable Debugger

1. [ ] Set debugger to `enabled = False` by default in `emulator.py`.
2. [ ] Adjust initial window width to only cover the Spectrum screen (320px * Scale).
3. [ ] Implement `F8` key handler to toggle `enabled` state.
4. [ ] When toggled:
    - Resize window (add/remove 300px for debug panel).
    - Enable/Disable `debugger.draw()` call in the main loop.
5. [ ] Ensure disassembler and debug logic is skipped entirely when disabled.
6. [ ] Verify and commit.
