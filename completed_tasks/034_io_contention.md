# Idea: Contended Memory and I/O Emulation

## Description
Implement the delicate timing delays that occur when the CPU and ULA compete for access to the same memory bank. This is a hallmark of ZX Spectrum hardware fidelity.

## Key Features
- **Memory Contention:** Simulate the "halt" state of the CPU when it tries to access the lower 16K of RAM (0x4000-0x7FFF) while the ULA is fetching data for screen rendering.
- **I/O Contention:** Apply similar delays to I/O port operations that trigger memory bank switching or reside in the contended range.
- **Accuracy:** Essential for games that use precise timing loops for advanced graphical effects (like multicolor or rainbow effects).

## Technical Needs
- A cycle-exact ULA rendering map (knowing exactly which T-state corresponds to which pixel/fetch).
- Logic in `Memory.read_byte` and `Memory.write_byte` to inject wait states (T-states) into the CPU.
