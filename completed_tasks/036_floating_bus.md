# Idea: Floating Bus Simulation

## Description
Simulate the "floating bus" behavior where reading from an unassigned I/O port returns the data currently being fetched by the ULA from the video memory.

## Key Features
- **Dynamic Port Reading:** Instead of returning a static `0xFF` for unused ports, return the byte currently on the data bus.
- **Timing Dependency:** The returned value depends exactly on the current T-state within the frame (what the ULA is "looking at" at that microsecond).
- **Game Compatibility:** Some specific games (e.g., *Arkanoid*, *Sidewize*) use this effect for synchronization or identifying the hardware version.

## Technical Needs
- Real-time link between the `IOBus.read_byte` and the `ULA` fetch cycle.
- Precise T-state tracking for the ULA's beam position.
