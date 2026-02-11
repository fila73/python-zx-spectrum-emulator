# Task: Fix remaining Block I/O Repeat flags

## Description
The block I/O repeat instructions (INIR, OTIR, INDR, OTDR) still fail about 500 tests in the standard Z80 suite. The failures are mostly due to subtle undocumented flag behavior during the repeat phase (interrupted state).

## Key Goals
- [ ] Research exact NMOS Z80 flag behavior for interrupted block I/O.
- [ ] Verify if F5 and F3 come from PC or from the decremented B register.
- [ ] Confirm if H and N should be cleared or preserved.
- [ ] Match the expected results in `edb2.json`, `edb3.json`, `edba.json`, and `edbb.json`.

## Progress
- [x] Initial implementation of unified H=C logic.
- [x] Implemented clearing H and updating F5/F3 from PC bits 13 and 11.
- [ ] Still failing about 500 tests per file.
