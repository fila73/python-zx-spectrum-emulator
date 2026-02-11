# Task: Debug Toolbar and Control Logic

1. **Toolbar UI:** Implement a persistent toolbar in the debug window with the following controls:
    - **Toggle Buttons:** Register View, Stack View, Code View.
    - **Execution Buttons:** Run (Go), Pause (Break), Step In, Step Over, Step Out.
2. **Step Logic:**
    - **Step In:** Execute exactly one instruction.
    - **Step Over:** Skip calls (execute until return).
    - **Step Out:** Execute until the current subroutine returns.
3. **Synchronization:** Ensure the emulator loop respects the "Paused" state and only steps the CPU when requested.
4. Implement basic "Breakpoint" support (manual list or click-to-set in code view).
5. Verify button responsiveness and state management.
