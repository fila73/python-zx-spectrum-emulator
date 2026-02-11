# Task: Fix 128K Memory Paging (Port 7FFD)

1. [ ] Analyze `src/memory.py` `write_port_7ffd` method.
2. [ ] Identify incorrect bit shifts for ROM and Screen selection.
    - Current: Bit 3 = ROM, Bit 4 = Screen.
    - Correct: Bit 3 = Screen, Bit 4 = ROM.
3. [ ] Fix the bit logic.
4. [ ] Verify ROM loading order in `emulator.py` (Bank 0 = Editor, Bank 1 = BASIC).
5. [ ] Verify with `tests/test_memory_128k.py` (create if missing).
