# Task: Implement Disassembler and Code View

1. **Disassembler Engine:** Create a utility to translate Z80 opcodes into human-readable Assembly mnemonics (e.g., `0x3E 0x05` -> `LD A, 5`).
2. **Code View Panel:** Display a list of instructions centered around the current PC.
    - Show memory address (Hex).
    - Show raw instruction bytes (Hex).
    - Show Assembly interpretation.
3. Include visual marking for the current instruction line.
4. Support looking back (instructions before PC) and looking ahead.
5. Verify disassembly accuracy against Z80 documentation.
