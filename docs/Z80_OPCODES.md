# Z80 Opcode Table

This document contains the standard Z80 instruction set based on [clrhome.org/table](https://clrhome.org/table/).

## Main Instructions (Base Opcodes)

| Opcode | Mnemonic | Bytes | Cycles | Flags (S Z H P/V N C) | Description |
| :--- | :--- | :---: | :---: | :---: | :--- |
| 00 | `nop` | 1 | 4 | - - - - - - | No operation. |
| 01 nn | `ld bc,nn` | 3 | 10 | - - - - - - | Loads 16-bit immediate `nn` into BC. |
| 02 | `ld (bc),a` | 1 | 7 | - - - - - - | Stores A into memory at (BC). |
| 03 | `inc bc` | 1 | 6 | - - - - - - | Increments BC. |
| 04 | `inc b` | 1 | 4 | V Z H 0 - | Increments B. |
| 05 | `dec b` | 1 | 4 | V Z H 1 - | Decrements B. |
| 06 n | `ld b,n` | 2 | 7 | - - - - - - | Loads 8-bit immediate `n` into B. |
| 07 | `rlca` | 1 | 4 | - - 0 0 C | Rotates A left circular. Bit 7 to C and Bit 0. |
| 08 | `ex af,af'` | 1 | 4 | * * * * * * | Exchanges AF with alternate AF'. |
| 09 | `add hl,bc` | 1 | 11 | - - H - 0 C | Adds BC to HL. |
| 0A | `ld a,(bc)` | 1 | 7 | - - - - - - | Loads A from memory at (BC). |
| 0B | `dec bc` | 1 | 6 | - - - - - - | Decrements BC. |
| 0C | `inc c` | 1 | 4 | V Z H 0 - | Increments C. |
| 0D | `dec c` | 1 | 4 | V Z H 1 - | Decrements C. |
| 0E n | `ld c,n` | 2 | 7 | - - - - - - | Loads 8-bit immediate `n` into C. |
| 0F | `rrca` | 1 | 4 | - - 0 0 C | Rotates A right circular. Bit 0 to C and Bit 7. |
| 10 d | `djnz d` | 2 | 13/8 | - - - - - - | Dec B, jump relative if B != 0. |
| 11 nn | `ld de,nn` | 3 | 10 | - - - - - - | Loads 16-bit immediate `nn` into DE. |
| 12 | `ld (de),a` | 1 | 7 | - - - - - - | Stores A into memory at (DE). |
| 13 | `inc de` | 1 | 6 | - - - - - - | Increments DE. |
| 14 | `inc d` | 1 | 4 | V Z H 0 - | Increments D. |
| 15 | `dec d` | 1 | 4 | V Z H 1 - | Decrements D. |
| 16 n | `ld d,n` | 2 | 7 | - - - - - - | Loads 8-bit immediate `n` into D. |
| 17 | `rla` | 1 | 4 | - - 0 0 C | Rotates A left through Carry. |
| 18 d | `jr d` | 2 | 12 | - - - - - - | Unconditional jump relative. |
| 19 | `add hl,de` | 1 | 11 | - - H - 0 C | Adds DE to HL. |
| 1A | `ld a,(de)` | 1 | 7 | - - - - - - | Loads A from memory at (DE). |
| 1B | `dec de` | 1 | 6 | - - - - - - | Decrements DE. |
| 1C | `inc e` | 1 | 4 | V Z H 0 - | Increments E. |
| 1D | `dec e` | 1 | 4 | V Z H 1 - | Decrements E. |
| 1E n | `ld e,n` | 2 | 7 | - - - - - - | Loads 8-bit immediate `n` into E. |
| 1F | `rra` | 1 | 4 | - - 0 0 C | Rotates A right through Carry. |
| 20 d | `jr nz,d` | 2 | 12/7 | - - - - - - | Jump relative if Z flag is 0. |
| 21 nn | `ld hl,nn` | 3 | 10 | - - - - - - | Loads 16-bit immediate `nn` into HL. |
| 22 nn | `ld (nn),hl` | 3 | 16 | - - - - - - | Stores HL into memory at `nn`. |
| 23 | `inc hl` | 1 | 6 | - - - - - - | Increments HL. |
| 24 | `inc h` | 1 | 4 | V Z H 0 - | Increments H. |
| 25 | `dec h` | 1 | 4 | V Z H 1 - | Decrements H. |
| 26 n | `ld h,n` | 2 | 7 | - - - - - - | Loads 8-bit immediate `n` into H. |
| 27 | `daa` | 1 | 4 | P Z H - C | Decimal Adjust Accumulator. |
| 28 d | `jr z,d` | 2 | 12/7 | - - - - - - | Jump relative if Z flag is 1. |
| 29 | `add hl,hl` | 1 | 11 | - - H - 0 C | Adds HL to HL. |
| 2A nn | `ld hl,(nn)` | 3 | 16 | - - - - - - | Loads HL from memory at `nn`. |
| 2B | `dec hl` | 1 | 6 | - - - - - - | Decrements HL. |
| 2C | `inc l` | 1 | 4 | V Z H 0 - | Increments L. |
| 2D | `dec l` | 1 | 4 | V Z H 1 - | Decrements L. |
| 2E n | `ld l,n` | 2 | 7 | - - - - - - | Loads 8-bit immediate `n` into L. |
| 2F | `cpl` | 1 | 4 | - - 1 - 1 - | Inverts Accumulator (NOT A). |
| 30 d | `jr nc,d` | 2 | 12/7 | - - - - - - | Jump relative if C flag is 0. |
| 31 nn | `ld sp,nn` | 3 | 10 | - - - - - - | Loads 16-bit immediate `nn` into SP. |
| 32 nn | `ld (nn),a` | 3 | 13 | - - - - - - | Stores A into memory at `nn`. |
| 33 | `inc sp` | 1 | 6 | - - - - - - | Increments SP. |
| 34 | `inc (hl)` | 1 | 11 | V Z H 0 - | Increments memory at (HL). |
| 35 | `dec (hl)` | 1 | 11 | V Z H 1 - | Decrements memory at (HL). |
| 36 n | `ld (hl),n` | 2 | 10 | - - - - - - | Loads 8-bit immediate `n` to (HL). |
| 37 | `scf` | 1 | 4 | - - 0 - 0 1 | Sets Carry flag. |
| 38 d | `jr c,d` | 2 | 12/7 | - - - - - - | Jump relative if C flag is 1. |
| 39 | `add hl,sp` | 1 | 11 | - - H - 0 C | Adds SP to HL. |
| 3A nn | `ld a,(nn)` | 3 | 13 | - - - - - - | Loads A from memory at `nn`. |
| 3B | `dec sp` | 1 | 6 | - - - - - - | Decrements SP. |
| 3C | `inc a` | 1 | 4 | V Z H 0 - | Increments A. |
| 3D | `dec a` | 1 | 4 | V Z H 1 - | Decrements A. |
| 3E n | `ld a,n` | 2 | 7 | - - - - - - | Loads 8-bit immediate `n` into A. |
| 3F | `ccf` | 1 | 4 | - - H - 0 C | Complements Carry flag (C = NOT C). |
| 40-47 | `ld b,r` | 1 | 4/7 | - - - - - - | Load register `r` into B (46 is (HL)). |
| 48-4F | `ld c,r` | 1 | 4/7 | - - - - - - | Load register `r` into C (4E is (HL)). |
| 50-57 | `ld d,r` | 1 | 4/7 | - - - - - - | Load register `r` into D (56 is (HL)). |
| 58-5F | `ld e,r` | 1 | 4/7 | - - - - - - | Load register `r` into E (5E is (HL)). |
| 60-67 | `ld h,r` | 1 | 4/7 | - - - - - - | Load register `r` into H (66 is (HL)). |
| 68-6F | `ld l,r` | 1 | 4/7 | - - - - - - | Load register `r` into L (6E is (HL)). |
| 70-75,77 | `ld (hl),r` | 1 | 7 | - - - - - - | Store register `r` into (HL). |
| 76 | `halt` | 1 | 4 | - - - - - - | Halts CPU. |
| 78-7F | `ld a,r` | 1 | 4/7 | - - - - - - | Load register `r` into A (7E is (HL)). |
| 80-87 | `add a,r` | 1 | 4/7 | V Z H 0 C | Add register `r` to A. |
| 88-8F | `adc a,r` | 1 | 4/7 | V Z H 0 C | Add `r` and Carry to A. |
| 90-97 | `sub r` | 1 | 4/7 | V Z H 1 C | Subtract `r` from A. |
| 98-9F | `sbc a,r` | 1 | 4/7 | V Z H 1 C | Sub `r` and Carry from A. |
| A0-A7 | `and r` | 1 | 4/7 | P Z 1 0 0 | Bitwise AND A with `r`. |
| A8-AF | `xor r` | 1 | 4/7 | P Z 0 0 0 | Bitwise XOR A with `r`. |
| B0-B7 | `or r` | 1 | 4/7 | P Z 0 0 0 | Bitwise OR A with `r`. |
| B8-BF | `cp r` | 1 | 4/7 | V Z H 1 C | Compare A with `r`. |
| C0 | `ret nz` | 1 | 11/5 | - - - - - - | Return if Z flag is 0. |
| C1 | `pop bc` | 1 | 10 | - - - - - - | Pop BC from stack. |
| C2 nn | `jp nz,nn` | 3 | 10 | - - - - - - | Jump to `nn` if Z flag is 0. |
| C3 nn | `jp nn` | 3 | 10 | - - - - - - | Unconditional jump to `nn`. |
| C4 nn | `call nz,nn` | 3 | 17/10 | - - - - - - | Call `nn` if Z flag is 0. |
| C5 | `push bc` | 1 | 11 | - - - - - - | Push BC onto stack. |
| C6 n | `add a,n` | 2 | 7 | V Z H 0 C | Add immediate `n` to A. |
| C7 | `rst 00h` | 1 | 11 | - - - - - - | Restart at 0x0000. |
| C8 | `ret z` | 1 | 11/5 | - - - - - - | Return if Z flag is 1. |
| C9 | `ret` | 1 | 10 | - - - - - - | Unconditional return. |
| CA nn | `jp z,nn` | 3 | 10 | - - - - - - | Jump to `nn` if Z flag is 1. |
| CB | `prefix cb` | 1 | 4 | * * * * * * | Bit/Shift instructions prefix. |
| CC nn | `call z,nn` | 3 | 17/10 | - - - - - - | Call `nn` if Z flag is 1. |
| CD nn | `call nn` | 3 | 17 | - - - - - - | Unconditional call to `nn`. |
| CE n | `adc a,n` | 2 | 7 | V Z H 0 C | Add `n` and Carry to A. |
| CF | `rst 08h` | 1 | 11 | - - - - - - | Restart at 0x0008. |
| D0 | `ret nc` | 1 | 11/5 | - - - - - - | Return if C flag is 0. |
| D1 | `pop de` | 1 | 10 | - - - - - - | Pop DE from stack. |
| D2 nn | `jp nc,nn` | 3 | 10 | - - - - - - | Jump to `nn` if C flag is 0. |
| D3 n | `out (n),a` | 2 | 11 | - - - - - - | Output A to port `n`. |
| D4 nn | `call nc,nn`| 3 | 17/10 | - - - - - - | Call `nn` if C flag is 0. |
| D5 | `push de` | 1 | 11 | - - - - - - | Push DE onto stack. |
| D6 n | `sub n` | 2 | 7 | V Z H 1 C | Subtract immediate `n` from A. |
| D7 | `rst 10h` | 1 | 11 | - - - - - - | Restart at 0x0010. |
| D8 | `ret c` | 1 | 11/5 | - - - - - - | Return if C flag is 1. |
| D9 | `exx` | 1 | 4 | - - - - - - | Exchange BC, DE, HL with alternates. |
| DA nn | `jp c,nn` | 3 | 10 | - - - - - - | Jump to `nn` if C flag is 1. |
| DB n | `in a,(n)` | 2 | 11 | - - - - - - | Input from port `n` into A. |
| DC nn | `call c,nn` | 3 | 17/10 | - - - - - - | Call `nn` if C flag is 1. |
| DD | `prefix dd` | 1 | 4 | - - - - - - | IX instruction prefix. |
| DE n | `sbc a,n` | 2 | 7 | V Z H 1 C | Sub `n` and Carry from A. |
| DF | `rst 18h` | 1 | 11 | - - - - - - | Restart at 0x0018. |
| E0 | `ret po` | 1 | 11/5 | - - - - - - | Return if parity is odd. |
| E1 | `pop hl` | 1 | 10 | - - - - - - | Pop HL from stack. |
| E2 nn | `jp po,nn` | 3 | 10 | - - - - - - | Jump relative if parity is odd. |
| E3 | `ex (sp),hl`| 1 | 19 | - - - - - - | Exchange HL with top of stack. |
| E4 nn | `call po,nn`| 3 | 17/10 | - - - - - - | Call `nn` if parity is odd. |
| E5 | `push hl` | 1 | 11 | - - - - - - | Push HL onto stack. |
| E6 n | `and n` | 2 | 7 | P Z 1 0 0 | Bitwise AND A with immediate `n`. |
| E7 | `rst 20h` | 1 | 11 | - - - - - - | Restart at 0x0020. |
| E8 | `ret pe` | 1 | 11/5 | - - - - - - | Return if parity is even. |
| E9 | `jp (hl)` | 1 | 4 | - - - - - - | Jump to address in HL. |
| EA nn | `jp pe,nn` | 3 | 10 | - - - - - - | Jump relative if parity is even. |
| EB | `ex de,hl` | 1 | 4 | - - - - - - | Exchange DE and HL. |
| EC nn | `call pe,nn`| 3 | 17/10 | - - - - - - | Call `nn` if parity is even. |
| ED | `prefix ed` | 1 | 4 | - - - - - - | Extended instructions prefix. |
| EE n | `xor n` | 2 | 7 | P Z 0 0 0 | Bitwise XOR A with immediate `n`. |
| EF | `rst 28h` | 1 | 11 | - - - - - - | Restart at 0x0028. |
| F0 | `ret p` | 1 | 11/5 | - - - - - - | Return if Sign flag is 0 (+). |
| F1 | `pop af` | 1 | 10 | * * * * * * | Pop AF from stack (restores flags). |
| F2 nn | `jp p,nn` | 3 | 10 | - - - - - - | Jump relative if Sign flag is 0 (+). |
| F3 | `di` | 1 | 4 | - - - - - - | Disable interrupts. |
| F4 nn | `call p,nn` | 3 | 17/10 | - - - - - - | Call `nn` if Sign flag is 0 (+). |
| F5 | `push af` | 1 | 11 | - - - - - - | Push AF onto stack. |
| F6 n | `or n` | 2 | 7 | P Z 0 0 0 | Bitwise OR A with immediate `n`. |
| F7 | `rst 30h` | 1 | 11 | - - - - - - | Restart at 0x0030. |
| F8 | `ret m` | 1 | 11/5 | - - - - - - | Return if Sign flag is 1 (-). |
| F9 | `ld sp,hl` | 1 | 6 | - - - - - - | Load HL into SP. |
| FA nn | `jp m,nn` | 3 | 10 | - - - - - - | Jump relative if Sign flag is 1 (-). |
| FB | `ei` | 1 | 4 | - - - - - - | Enable interrupts. |
| FC nn | `call m,nn` | 3 | 17/10 | - - - - - - | Call `nn` if Sign flag is 1 (-). |
| FD | `prefix fd` | 1 | 4 | - - - - - - | IY instruction prefix. |
| FE n | `cp n` | 2 | 7 | V Z H 1 C | Compare A with immediate `n`. |
| FF | `rst 38h` | 1 | 11 | - - - - - - | Restart at 0x0038. |

---

## ED Instructions (Extended)

| Opcode | Mnemonic | Bytes | Cycles | Flags (S Z H P/V N C) | Description |
| :--- | :--- | :---: | :---: | :---: | :--- |
| ED 40 | `in b,(c)` | 2 | 12 | P Z 0 0 0 | Input from port C into B. |
| ED 41 | `out (c),b` | 2 | 12 | - - - - - - | Output B to port C. |
| ED 42 | `sbc hl,bc` | 2 | 15 | V Z H 1 C | HL = HL - BC - Carry. |
| ED 43 nn | `ld (nn),bc` | 4 | 20 | - - - - - - | Store BC to memory at `nn`. |
| ED 44 | `neg` | 2 | 8 | V Z H 1 C | Negate Accumulator (A = -A). |
| ED 45 | `retn` | 2 | 14 | - - - - - - | Return from NMI. |
| ED 46 | `im 0` | 2 | 8 | - - - - - - | Set interrupt mode 0. |
| ED 47 | `ld i,a` | 2 | 9 | - - - - - - | Load A into I register. |
| ED 48 | `in c,(c)` | 2 | 12 | P Z 0 0 0 | Input from port C into C. |
| ED 49 | `out (c),c` | 2 | 12 | - - - - - - | Output C to port C. |
| ED 4A | `adc hl,bc` | 2 | 15 | V Z H 0 C | HL = HL + BC + Carry. |
| ED 4B nn | `ld bc,(nn)` | 4 | 20 | - - - - - - | Load BC from memory at `nn`. |
| ED 4D | `reti` | 2 | 14 | - - - - - - | Return from maskable interrupt. |
| ED 4F | `ld r,a` | 2 | 9 | - - - - - - | Load A into Refresh register. |
| ED 50 | `in d,(c)` | 2 | 12 | P Z 0 0 0 | Input from port C into D. |
| ED 51 | `out (c),d` | 2 | 12 | - - - - - - | Output D to port C. |
| ED 52 | `sbc hl,de` | 2 | 15 | V Z H 1 C | HL = HL - DE - Carry. |
| ED 53 nn | `ld (nn),de` | 4 | 20 | - - - - - - | Store DE to memory at `nn`. |
| ED 56 | `im 1` | 2 | 8 | - - - - - - | Set interrupt mode 1. |
| ED 57 | `ld a,i` | 2 | 9 | P Z 0 0 0 | Load I into A. |
| ED 58 | `in e,(c)` | 2 | 12 | P Z 0 0 0 | Input from port C into E. |
| ED 59 | `out (c),e` | 2 | 12 | - - - - - - | Output E to port C. |
| ED 5A | `adc hl,de` | 2 | 15 | V Z H 0 C | HL = HL + DE + Carry. |
| ED 5B nn | `ld de,(nn)` | 4 | 20 | - - - - - - | Load DE from memory at `nn`. |
| ED 5E | `im 2` | 2 | 8 | - - - - - - | Set interrupt mode 2. |
| ED 5F | `ld a,r` | 2 | 9 | P Z 0 0 0 | Load Refresh register into A. |
| ED 60 | `in h,(c)` | 2 | 12 | P Z 0 0 0 | Input from port C into H. |
| ED 61 | `out (c),h` | 2 | 12 | - - - - - - | Output H to port C. |
| ED 62 | `sbc hl,hl` | 2 | 15 | V Z H 1 C | HL = HL - HL - Carry (HL = -Carry). |
| ED 63 nn | `ld (nn),hl` | 4 | 20 | - - - - - - | Store HL to memory at `nn`. |
| ED 67 | `rrd` | 2 | 18 | P Z 0 0 - | Rotate Right Decimal. |
| ED 68 | `in l,(c)` | 2 | 12 | P Z 0 0 0 | Input from port C into L. |
| ED 69 | `out (c),l` | 2 | 12 | - - - - - - | Output L to port C. |
| ED 6A | `adc hl,hl` | 2 | 15 | V Z H 0 C | HL = HL + HL + Carry. |
| ED 6B nn | `ld hl,(nn)` | 4 | 20 | - - - - - - | Load HL from memory at `nn`. |
| ED 6F | `rld` | 2 | 18 | P Z 0 0 - | Rotate Left Decimal. |
| ED 72 | `sbc hl,sp` | 2 | 15 | V Z H 1 C | HL = HL - SP - Carry. |
| ED 73 nn | `ld (nn),sp` | 4 | 20 | - - - - - - | Store SP to memory at `nn`. |
| ED 78 | `in a,(c)` | 2 | 12 | P Z 0 0 0 | Input from port C into A. |
| ED 79 | `out (c),a` | 2 | 12 | - - - - - - | Output A to port C. |
| ED 7A | `adc hl,sp` | 2 | 15 | V Z H 0 C | HL = HL + SP + Carry. |
| ED 7B nn | `ld sp,(nn)` | 4 | 20 | - - - - - - | Load SP from memory at `nn`. |
| ED A0 | `ldi` | 2 | 16 | P - 0 0 - | Block Transfer Increment. |
| ED A1 | `cpi` | 2 | 16 | P Z H 1 - | Block Compare Increment. |
| ED A2 | `ini` | 2 | 16 | - Z - 1 - | Block Input Increment. |
| ED A3 | `outi` | 2 | 16 | - Z - 1 - | Block Output Increment. |
| ED A8 | `ldd` | 2 | 16 | P - 0 0 - | Block Transfer Decrement. |
| ED A9 | `cpd` | 2 | 16 | P Z H 1 - | Block Compare Decrement. |
| ED AA | `ind` | 2 | 16 | - Z - 1 - | Block Input Decrement. |
| ED AB | `outd` | 2 | 16 | - Z - 1 - | Block Output Decrement. |
| ED B0 | `ldir` | 2 | 21/16 | - - 0 0 0 - | Block Transfer Incr. Repeat. |
| ED B1 | `cpir` | 2 | 21/16 | P Z H 1 - | Block Compare Incr. Repeat. |
| ED B2 | `inir` | 2 | 21/16 | - 1 - 1 - | Block Input Incr. Repeat. |
| ED B3 | `otir` | 2 | 21/16 | - 1 - 1 - | Block Output Incr. Repeat. |
| ED B8 | `lddr` | 2 | 21/16 | - - 0 0 0 - | Block Transfer Decr. Repeat. |
| ED B9 | `cpdr` | 2 | 21/16 | P Z H 1 - | Block Compare Decr. Repeat. |
| ED BA | `indr` | 2 | 21/16 | - 1 - 1 - | Block Input Decr. Repeat. |
| ED BB | `otdr` | 2 | 21/16 | - 1 - 1 - | Block Output Decr. Repeat. |

---

## CB Instructions (Bit/Shift)

| Opcode | Mnemonic | Bytes | Cycles | Flags (S Z H P/V N C) | Description |
| :--- | :--- | :---: | :---: | :---: | :--- |
| CB 00-07 | `rlc r` | 2 | 8/15 | P Z 0 0 C | Rotate register `r` left circular. |
| CB 08-0F | `rrc r` | 2 | 8/15 | P Z 0 0 C | Rotate register `r` right circular. |
| CB 10-17 | `rl r` | 2 | 8/15 | P Z 0 0 C | Rotate register `r` left through Carry. |
| CB 18-1F | `rr r` | 2 | 8/15 | P Z 0 0 C | Rotate register `r` right through Carry. |
| CB 20-27 | `sla r` | 2 | 8/15 | P Z 0 0 C | Shift register `r` left arithmetic. |
| CB 28-2F | `sra r` | 2 | 8/15 | P Z 0 0 C | Shift register `r` right arithmetic. |
| CB 30-37 | `sll r` | 2 | 8/15 | P Z 0 0 C | Shift register `r` left logical (undocumented). |
| CB 38-3F | `srl r` | 2 | 8/15 | P Z 0 0 C | Shift register `r` right logical. |
| CB 40-7F | `bit b,r` | 2 | 8/12 | - Z 1 - 0 - | Test bit `b` of register `r`. |
| CB 80-BF | `res b,r` | 2 | 8/15 | - - - - - - | Reset bit `b` of register `r`. |
| CB C0-FF | `set b,r` | 2 | 8/15 | - - - - - - | Set bit `b` of register `r`. |

*(Note: Cycle 15 applies when operating on `(HL)` at suffix `06`.)*
