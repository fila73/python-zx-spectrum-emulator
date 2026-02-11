# Task: Integrate Standard Z80 Tests

## Objective
Integrate known-good Z80 test suites (like Fuse or SingleStepTests) to verify the accuracy of the CPU implementation, including flags and undocumented behaviors.

## Plan
1.  Download a sample JSON test file (e.g., for a simple instruction like NOP or LD A, n).
2.  Implement a test runner that parses the JSON and verifies the CPU state before and after execution.
3.  Extend the runner to support more instructions.
4.  Fix any identified CPU bugs.

## Verification
- Run the new test runner against selected instructions and ensure they pass.
