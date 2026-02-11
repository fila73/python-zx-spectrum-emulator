# Core Architecture Documentation

## Memory Map (48K Model)
| Address Range | Size | Description |
|---------------|------|-------------|
| 0x0000 - 0x3FFF | 16 KB | ROM (Read-only) |
| 0x4000 - 0x5AFF | 6.75 KB | Video RAM (Pixels & Attributes) |
| 0x5B00 - 0xFFFF | 41.25 KB | System & User RAM |

## Video Rendering (ULA)
The display is 256x192 pixels with a 32x24 attribute grid.
- **Interleaved Bitmap:** Memory at 0x4000 is not linear. It is divided into three sections, with lines interleaved to simplify hardware counters.
- **Attributes:** One byte at 0x5800 controls colors for each 8x8 block (INK, PAPER, BRIGHT, FLASH).
- **Implementation:** `ULA.render_screen()` handles the translation from interleaved Spectrum memory to a linear RGB buffer.

## CPU (Zilog Z80)
The implementation aims for cycle-accuracy.
- **Clock Speed:** 3.5 MHz
- **Interrupts:** 50Hz maskable interrupts (Mode 1) triggered by ULA during V-Blank.

## I/O Bus
All I/O operations are routed through the `IOBus` class, which dispatches to registered devices like the `ULA`.
- **Port 0xFE:** Handled by `ULA` for border color, beeper, and keyboard scanning.

## ROM Images
Stored in `roms/`. Original binary blobs are used for system logic.
- `48.rom`: Standard Sinclair ZX Spectrum 48K ROM.

---
*Last updated: 2026-02-09*
