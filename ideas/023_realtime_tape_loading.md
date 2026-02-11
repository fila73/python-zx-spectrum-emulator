# Idea: Real-time "Whistling" Tape Loading

## Description
Implement an option for realistic tape loading that mimics the original hardware experience. Instead of the current instant loading (via ROM traps), this mode would feed the pulse data into the ULA at the original speed (approx. 1500 baud).

## Key Features
- **Visuals:** Restore the iconic border loading stripes during the process.
- **Audio:** Play the characteristic "whistling" loading sounds (pilot tones, data pulses).
- **Control:** Toggle between "Instant Load" and "Real-time Load".
- **Authenticity:** Allows loading of tapes that use custom loaders (which often bypass the standard ROM routine).

## Technical Needs
- Pulse-to-bit conversion logic or raw sample playback linked to the ULA EAR bit.
- Synchronization with the 50Hz frame loop to ensure correct pulse timing.
