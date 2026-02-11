# ZX Spectrum Emulator in Python

A stable, cycle-accurate Sinclair ZX Spectrum emulator developed by an autonomous agent team (Saturnin & The Architect).

## Features
- **Models:** Supports **ZX Spectrum 48K** and **ZX Spectrum 128K** + Toastrack.
- **CPU:** Cycle-accurate Z80 emulation with correct T-state timing and contention.
- **Video:** Accurate ULA emulation including border effects, floating bus, and flash attributes.
- **Audio:** High-fidelity 44.1kHz stereo sound using `miniaudio`.
  - **Beeper:** Band-limited synthesis (Area-Based Resampling) for clean square waves.
  - **AY-3-8912:** Full 3-channel PSG emulation for 128K mode with envelope support and oversampling.
  - **Low Latency:** Threaded audio engine with ring buffer architecture to prevent underruns ("humming").
- **Storage:** Fast tape loading (.TAP files) via ROM traps.
- **Input:** Keyboard mapping to modern PC layout.
- **Debug:** Built-in debugger with disassembler, memory viewer, and execution control (F8).

## Project Structure
- `emulator.py`: Main entry point.
- `src/`: Core logic.
  - `cpu.py`: Z80 CPU implementation.
  - `ula.py`: Video/Audio/IO controller.
  - `memory.py`: Memory management and banking (128K).
  - `audio_engine.py`: Miniaudio wrapper and ring buffer.
  - `ay38910.py`: Sound chip emulation.
  - `tape.py`: Tape file parser.
  - `debug.py`: Integrated debugger UI.
- `roms/`: System ROM images (48.rom, 128.rom).
- `games/`: Tape images for testing.
- `tests/`: Automated test suite (Pytest).

## Getting Started

### Prerequisites
- Python 3.12+
- `pygame-ce` (or standard `pygame`)
- `numpy`
- `miniaudio`

### Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

*(Note: `sounddevice` was replaced by `miniaudio` for better cross-platform low-latency support without external dependencies like PortAudio)*

### Running the Emulator

**Default (48K Mode):**
```bash
python3 emulator.py games/chuckieegg1.tap
```

**128K Mode:**
```bash
python3 emulator.py games/Fuxoft_Soundtrack_1_(Original_Tape).tap --128
```

**Stereo Mixing Modes (AY-3-8912):**
- Default: Mono (centered)
- `--abc`: Channel A=Left, B=Center, C=Right
- `--acb`: Channel A=Left, C=Center, B=Right (Common in demos)

### Controls
- **Keyboard:** Standard Spectrum mapping (Q, A, O, P, Space).
- **F8:** Toggle Debugger (Pause/Step/Resume).

## Current Status
The project has moved beyond initialization and is now functional for playing games and running demos.
- [x] CPU Instruction Set (including undocumented)
- [x] Accurate Timing (50.08Hz / 50.02Hz)
- [x] Memory Paging (128K)
- [x] High-Quality Audio Engine
- [x] Tape Loading (Traps)

---
*Maintained by Saturnin & The Architect Agent.*
