# Z80 Assembly Reference & Implementation Guide

This document serves as a reference for Z80 instructions and how they are implemented in our Python emulator.

## Register Set
The Z80 has a rich set of registers, implemented as attributes in the `Z80` class.

| Category | Registers | Implementation |
|----------|-----------|----------------|
| Main | A, F, B, C, D, E, H, L | `self.a`, `self.f`, etc. |
| Alternate | A', F', B', C', D', E', H', L' | `self.a_alt`, etc. |
| Index | IX, IY | `self.ix`, `self.iy` |
| Special | PC, SP, I, R | `self.pc`, `self.sp`, etc. |

### 16-bit Register Pairs
Register pairs (BC, DE, HL, AF) are implemented using Python `@property` decorators for seamless 16-bit access.
- **Example:** `self.hl` combined from `self.h` (high) and `self.l` (low).

---

## Instruction Groups

### 1. Load Instructions (8-bit)
- **LD r, n:** Loads an immediate 8-bit value into register `r`.
- **LD r, r':** Copies value from register `r'` to `r`.
- **Emulator:** Handled by `_ld_r_n` and `_ld_r_r` methods.

### 2. Load Instructions (16-bit)
- **LD dd, nn:** Loads an immediate 16-bit value into register pair `dd`.
- **LD HL, (nn):** Loads HL with the contents of memory at address `nn`.
- **LD (nn), HL:** Stores contents of HL at memory address `nn`.
- **LD SP, HL:** Copies HL to SP.
- **Extended (ED):** `LD dd, (nn)` and `LD (nn), dd` for BC, DE, SP.
- **Index (DD/FD):** `LD IX/IY, nn`, `LD SP, IX/IY`, `LD (nn), IX/IY`.

### 3. Arithmetic & Logic (8-bit)
The 8-bit ALU operations update flags in the `F` register.

| Instruction | Description | Flags Affected |
|-------------|-------------|----------------|
| **ADD A, n** | Add value `n` to Accumulator. | S, Z, H, P/V, N, C |
| **SUB n** | Subtract value `n` from Accumulator. | S, Z, H, P/V, N, C |
| **INC r** | Increment register `r`. | S, Z, H, P/V, N (C preserved) |
| **AND n** | Logical AND with Accumulator. | S, Z, H (set), P, N, C (reset) |
| **NEG** | Negate Accumulator (Two's complement). | S, Z, H, P/V, N=1, C |

### 4. Arithmetic (16-bit)
- **ADD HL, ss:** Add 16-bit register pair `ss` to HL. Updates C, H, N.
- **ADC/SBC HL, ss:** Add/Subtract with Carry for 16-bit pairs. Updates S, Z, H, P/V, N, C.
- **INC/DEC ss:** Increment or decrement 16-bit register pair. Does NOT affect flags.

### 5. Program Flow Control
Instructions that modify the **PC** (Program Counter).

- **JP nn / JP cc, nn:** Absolute jump to address `nn`.
- **JP (HL) / JP (IX) / JP (IY):** Jump to the address contained in the register.
- **JR e / JR cc, e:** Relative jump by signed offset `e`.
- **CALL nn / CALL cc, nn:** Pushes current PC to stack and jumps to `nn`.
- **RET / RET cc:** Pops return address from stack and sets PC.
- **RETI / RETN:** Return from Interrupt / Non-Maskable Interrupt.
- **RST p:** Restart at fixed page 0 location (0x00, 0x08, ... 0x38).

### 6. Stack Operations
Z80 uses a 16-bit stack pointer (**SP**) that grows **downward**.

- **PUSH qq:** Decrements SP by 2 and stores register pair `qq` at `(SP)`.
- **POP qq:** Loads register pair `qq` from `(SP)` and increments SP by 2.

### 7. Exchange Instructions
- **EX DE, HL:** Swaps contents of DE and HL.
- **EX AF, AF':** Swaps the accumulator and flags with their shadow counterparts.
- **EXX:** Swaps BC, DE, and HL with shadow registers (BC', DE', HL').
- **EX (SP), HL / IX / IY:** Swaps the 16-bit value at the top of the stack with the register.

### 8. Bit Manipulation & Rotates (CB Prefix)
- **BIT b, r / (IX+d):** Test bit `b`.
- **SET b, r / (IX+d):** Set bit `b` to 1.
- **RES b, r / (IX+d):** Reset bit `b` to 0.
- **RLC / RRC / RL / RR / SLA / SRA / SRL / SLL:** Rotates and shifts.
- **RLD / RRD:** 4-bit BCD digit rotates between Accumulator and (HL).

### 9. Block Transfer & Compare (Extended ED Prefix)
- **LDI / LDIR / LDD / LDDR:** Data block movement.
- **CPI / CPIR / CPD / CPDR:** Data block searching.

### 10. Input / Output (I/O)
- **IN A, (n):** Input from port `n` to Accumulator.
- **OUT (n), A:** Output Accumulator to port `n`.
- **IN r, (C) / OUT (C), r:** Input/Output using C register as port address.
- **INI / INIR / OUTI / OTIR:** Block I/O instructions.

---

## Hardware Emulation (ULA & Audio)
- **Memory Map:** 16K ROM, 6.75K Video RAM (Interleaved), RAM up to 64K.
- **IO Bus:** Centralized `IOBus` class routing requests to devices.
- **ULA:** Emulated chip handling Port `0xFE`.
    - **Border Color:** Bits 0-2 of 0xFE.
    - **Audio (Beeper/MIC):** Bits 3-4 of 0xFE. `ULA.render_audio()` generates 8-bit PCM data.
    - **Keyboard:** Matrix scanning by selecting rows via high byte of address.
- **Video:** `ULA.render_screen()` converts interleaved VRAM to linear RGB for Pygame.
- **Interrupts:** Triggered at 50Hz (Mode 1 - `RST 38h`).

---

## Tape Support
- **Format:** Supports `.tap` files (standard Spectrum tape images).
- **Implementation:** `TapePlayer` class handles block reading. Integration via ROM traps (planned) or direct memory injection.

---
*Last updated: 2026-02-09. Synchronized with Antigravity Brain Logs.*
