# Task: Complete all Standard Z80 Tests

## Objective
Reach 100% coverage of standard, CB, ED, and index-prefixed instructions using the SingleStepTests suite.

## Plan
1.  Systematically download remaining JSON test files.
2.  Update the test runner to automatically discover and run all JSON files in `tests/z80_standard/`.
3.  Fix any remaining CPU bugs identified by these tests.
4.  Ensure all undocumented behaviors (flags, WZ, etc.) are fully verified.

## Verification
- Run `pytest tests/test_standard_z80.py` and ensure all tests pass.
