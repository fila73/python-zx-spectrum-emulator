# ZX Spectrum Emulator in Python

A stable, cycle-accurate Sinclair ZX Spectrum emulator developed by an autonomous agent team.

## Project Vision
To build a high-fidelity emulation of the ZX Spectrum 48K (and later 128K) using Python, focusing on:
- **Cycle-accuracy:** Faithful Z80 instruction timing.
- **Hardware Fidelity:** Precise ULA, memory, and audio emulation.
- **Developer Experience:** Clean, modular codebase with high test coverage.

## Project Structure
- `emulator.py`: The main entry point.
- `src/`: Core logic (CPU, Memory, Video, Audio).
- `roms/`: Original system ROM images.
- `tests/`: Automated test suite (Pytest).
- `current_tasks/`: Active development objectives.
- `completed_tasks/`: Historical record of achieved milestones.
- `ideas/`: Future enhancements and sparks of inspiration.
- `agent_logs/`: Logs from the autonomous architect sessions.

## Current State
The project is currently in the **Initialization Phase**.
- [x] Basic project structure established.
- [x] Z80 register set defined.
- [x] 48K Memory map stubbed.
- [x] Original ROM images (48K, 128K, ZX80, ZX81) acquired and indexed.
- [x] ROM assembly sources added for reference.

## Getting Started
### Prerequisites
- Python 3.12+
- `pygame`, `numpy`, `numba`

### Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the Emulator
```bash
python3 emulator.py
```

## Other rules to obey
- @.antigravityrules

---
*Maintained by Saturnin & The Architect Agent.*
