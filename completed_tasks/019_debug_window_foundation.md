# Task: Implement Debug Window Foundation

1. Create a secondary window (using Pygame or integrated UI library) specifically for debugging.
2. Implement a dedicated "Debugger" class to manage state, UI elements, and layout.
3. **Register View:** Create a display panel for all Z80 registers (A, F, BC, DE, HL, IX, IY, SP, PC) and internal flags.
4. **Stack View:** Create a scrollable view showing the top 10-20 entries of the stack memory relative to the current SP.
5. Integrate with the main `emulator.py` loop to update these views every frame or upon pause.
6. Verify layout and performance.
