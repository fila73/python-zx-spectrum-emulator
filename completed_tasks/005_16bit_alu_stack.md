# Task: Implement 16-bit Arithmetic and Stack Operations

1. Implement 16-bit Arithmetic instructions:
    - `ADD HL, ss` (ss = BC, DE, HL, SP)
    - `ADC HL, ss`
    - `SBC HL, ss`
    - `INC ss` / `DEC ss` (ss = BC, DE, HL, SP, IX, IY)
2. Implement Stack operations:
    - `PUSH qq` (qq = BC, DE, HL, AF)
    - `POP qq`
    - `EX (SP), HL` / `EX (SP), IX` / `EX (SP), IY`
3. Verify with unit tests.
