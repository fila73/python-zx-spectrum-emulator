import sys
import os
import pygame
try:
    from src.cpu import Z80
    from src.memory import Memory
    from src.io import IOBus
    from src.ula import ULA
    from src.tape import Tape
    from src.hardware_128k import Hardware128K
    print('--- Hey Saturnin: Startuji emulátor ---', file=sys.stderr, flush=True)
except Exception as e:
    print(f'CRITICAL ERROR: Import failed: {e}', file=sys.stderr, flush=True)
    sys.exit(1)

import time

SCALE = 3
SCREEN_WIDTH = 256 + 64 # Total with border
SCREEN_HEIGHT = 192 + 64
WINDOW_WIDTH = SCREEN_WIDTH * SCALE
WINDOW_HEIGHT = SCREEN_HEIGHT * SCALE

# Audio settings
SAMPLE_RATE = 44100
TARGET_FPS = 50.08
FRAME_DURATION = 1.0 / TARGET_FPS
CYCLES_PER_FRAME = 69888
SAMPLES_PER_FRAME = int(SAMPLE_RATE / TARGET_FPS)

KEY_MAP = {
    pygame.K_LSHIFT: (0xFE, 0), pygame.K_z: (0xFE, 1), pygame.K_x: (0xFE, 2), pygame.K_c: (0xFE, 3), pygame.K_v: (0xFE, 4),
    pygame.K_a: (0xFD, 0), pygame.K_s: (0xFD, 1), pygame.K_d: (0xFD, 2), pygame.K_f: (0xFD, 3), pygame.K_g: (0xFD, 4),
    pygame.K_q: (0xFB, 0), pygame.K_w: (0xFB, 1), pygame.K_e: (0xFB, 2), pygame.K_r: (0xFB, 3), pygame.K_t: (0xFB, 4),
    pygame.K_1: (0xF7, 0), pygame.K_2: (0xF7, 1), pygame.K_3: (0xF7, 2), pygame.K_4: (0xF7, 3), pygame.K_5: (0xF7, 4),
    pygame.K_KP1: (0xF7, 0), pygame.K_KP2: (0xF7, 1), pygame.K_KP3: (0xF7, 2), pygame.K_KP4: (0xF7, 3), pygame.K_KP5: (0xF7, 4),
    pygame.K_0: (0xEF, 0), pygame.K_9: (0xEF, 1), pygame.K_8: (0xEF, 2), pygame.K_7: (0xEF, 3), pygame.K_6: (0xEF, 4),
    pygame.K_KP0: (0xEF, 0), pygame.K_KP9: (0xEF, 1), pygame.K_KP8: (0xEF, 2), pygame.K_KP7: (0xEF, 3), pygame.K_KP6: (0xEF, 4),
    pygame.K_p: (0xDF, 0), pygame.K_o: (0xDF, 1), pygame.K_i: (0xDF, 2), pygame.K_u: (0xDF, 3), pygame.K_y: (0xDF, 4),
    pygame.K_RETURN: (0xBF, 0), pygame.K_KP_ENTER: (0xBF, 0), pygame.K_l: (0xBF, 1), pygame.K_k: (0xBF, 2), pygame.K_j: (0xBF, 3), pygame.K_h: (0xBF, 4),
    pygame.K_SPACE: (0x7F, 0), pygame.K_RSHIFT: (0xFE, 0), pygame.K_m: (0x7F, 2), pygame.K_n: (0x7F, 3), pygame.K_b: (0x7F, 4)
}

EXTENDED_KEY_MAP = {
    pygame.K_BACKSPACE: [(0xFE, 0), (0xEF, 0)], # CS + 0 (Delete)
    pygame.K_TAB: [(0xFE, 0), (0xF7, 0)],       # CS + 1 (Edit)
    pygame.K_LEFT: [(0xFE, 0), (0xF7, 4)],      # CS + 5 (Left)
    pygame.K_DOWN: [(0xFE, 0), (0xEF, 4)],      # CS + 6 (Down)
    pygame.K_UP: [(0xFE, 0), (0xEF, 3)],        # CS + 7 (Up)
    pygame.K_RIGHT: [(0xFE, 0), (0xEF, 2)],     # CS + 8 (Right)
    pygame.K_ESCAPE: [(0xFE, 0), (0x7F, 0)],    # CS + Space (Break)
    pygame.K_CAPSLOCK: [(0xFE, 0), (0xF7, 1)],  # CS + 2 (Caps Lock)
    pygame.K_LALT: [(0x7F, 1)],                 # Symbol Shift (alias)
    pygame.K_RALT: [(0x7F, 1)],                 # Symbol Shift (alias)
    pygame.K_LCTRL: [(0x7F, 1)],                # Symbol Shift (alias)
    pygame.K_RCTRL: [(0x7F, 1)],                # Symbol Shift (alias)
}

UNICODE_MAP = {
    '!': [(0x7F, 1), (0xF7, 0)], '@': [(0x7F, 1), (0xF7, 1)],
    '#': [(0x7F, 1), (0xF7, 2)], '$': [(0x7F, 1), (0xF7, 3)],
    '%': [(0x7F, 1), (0xF7, 4)], '&': [(0x7F, 1), (0xEF, 4)],
    "'": [(0x7F, 1), (0xEF, 3)], '(': [(0x7F, 1), (0xEF, 2)],
    ')': [(0x7F, 1), (0xEF, 1)], '_': [(0x7F, 1), (0xEF, 0)],
    '-': [(0x7F, 1), (0xBF, 3)], '+': [(0x7F, 1), (0xBF, 2)],
    '=': [(0x7F, 1), (0xBF, 1)], ',': [(0x7F, 1), (0x7F, 3)],
    '.': [(0x7F, 1), (0x7F, 2)], '*': [(0x7F, 1), (0x7F, 4)],
    '/': [(0x7F, 1), (0xFE, 4)], ';': [(0x7F, 1), (0xDF, 1)],
    '"': [(0x7F, 1), (0xDF, 0)], '?': [(0x7F, 1), (0xFE, 3)],
    ':': [(0x7F, 1), (0xFE, 1)], '<': [(0x7F, 1), (0xFB, 3)],
    '>': [(0x7F, 1), (0xFB, 4)], '^': [(0x7F, 1), (0xBF, 4)]
}

def load_test_pattern(memory):
    for x in range(32):
        color = x % 8
        attr = (color << 3) | 7
        memory.write_byte(0x5800 + x, attr)
    for i in range(256):
        memory.write_byte(0x4000 + i, i & 0xFF)

def main():
    print('--- Hey Saturnin: Startuji emulátor ---')
    pygame.init()
    
    from src.audio_engine import AudioEngine
    audio_engine = AudioEngine(sample_rate=SAMPLE_RATE, buffer_size=4096)
    audio_engine.start()
    print("DEBUG: AudioEngine initialized.")
        
    pygame.font.init()
    debug_font = pygame.font.SysFont('Consolas', 14)
    
    # Increase window width for debug panel
    WINDOW_WIDTH_DEBUG = WINDOW_WIDTH + 300
    
    # Start with standard width (Debugger disabled by default)
    current_width = WINDOW_WIDTH
    screen = pygame.display.set_mode((current_width, WINDOW_HEIGHT))
    
    pygame.display.set_caption('ZX Spectrum Emulator')
    
    model = "48K"
    if "--+3" in sys.argv: model = "+3"
    elif "--zx81" in sys.argv: model = "ZX81"
    elif "--zx80" in sys.argv: model = "ZX80"
    elif "--16" in sys.argv: model = "16K"
    elif "--+2" in sys.argv: model = "+2"
    elif "--128" in sys.argv: model = "128K"
    
    is_128k = model in ["128K", "+2"]
    is_plus3 = model == "+3"
    
    mixing_mode = 'mono'
    if "--abc" in sys.argv: mixing_mode = 'abc'
    elif "--acb" in sys.argv: mixing_mode = 'acb'

    memory = Memory(model=model)
    
    # 1. NAČTENÍ ROM
    if model == "+3":
        rom_path = "roms/128+3.rom"
        rom_name = "+3"
    elif model == "ZX81":
        rom_path = "roms/zx81.rom"
        rom_name = "ZX81"
    elif model == "ZX80":
        rom_path = "roms/zx80.rom"
        rom_name = "ZX80"
    elif model == "+2":
        rom_path = "roms/128+2.rom"
        rom_name = "+2"
    elif model == "128K":
        rom_path = "roms/128.rom"
        rom_name = "128K"
    else:
        rom_path = "roms/48.rom"
        rom_name = model

    try:
        with open(rom_path, "rb") as f:
            rom_data = f.read()
            if is_plus3:
                memory.load_rom(rom_data[0:16384], bank=0)
                memory.load_rom(rom_data[16384:32768], bank=1)
                memory.load_rom(rom_data[32768:49152], bank=2)
                memory.load_rom(rom_data[49152:65536], bank=3)
            elif is_128k:
                memory.load_rom(rom_data[0:16384], bank=0)
                memory.load_rom(rom_data[16384:32768], bank=1)
            else:
                memory.load_rom(rom_data)
        print(f"--- Saturnin: ROM {rom_name} úspěšně načtena ze {rom_path} ---")
    except FileNotFoundError:
        print(f"CRITICAL ERROR: Soubor {rom_path} nebyl nalezen!")
        audio_engine.stop()
        pygame.quit()
        return

    io_bus = IOBus()
    ula = ULA(memory, is_128k=(is_128k or is_plus3))
    io_bus.add_device(ula)
    
    if is_128k or is_plus3:
        hw128 = Hardware128K(memory, mixing_mode=mixing_mode)
        io_bus.add_device(hw128)
    
    # Timing constants
    if is_128k or is_plus3:
        frame_cycles = 70908
        target_fps = 50.021 # 3.5469 MHz / 70908
    else:
        frame_cycles = 69888
        target_fps = 50.08  # 3.5 MHz / 69888

    frame_duration_ns = int(1_000_000_000 / target_fps)
    
    # 2. INICIALIZACE CPU
    cpu = Z80(memory, io_bus)
    cpu.ula = ula
    cpu.pc = 0x0000 
    
    # 3. TAPE LOADING
    tape = Tape()
    #tape_path = "games/arkanoid.tap" # Default
    #tape_path = "games/jetpac.tap"
    tape_path = "games/Chuckieegg1.zip"
    
    # Parse arguments for tape path (skip flags)
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            tape_path = arg
    
    if os.path.exists(tape_path):
        if tape.load_file(tape_path):
            cpu.tape = tape
            print(f"--- Saturnin: Tape {tape_path} attached ---")
    else:
        print(f"--- Saturnin: No tape found at {tape_path} ---")
    
    # Link CPU to ULA for audio timing
    ula.set_cpu(cpu)

    # Initialize Debugger
    from src.debug import Debugger
    debugger = Debugger(screen, debug_font, WINDOW_WIDTH, 0)
    debug_enabled = False

    print('--- Saturnin: Vstupuji do hlavní smyčky ---')
    print(f"DEBUG: Timing Target: {target_fps:.2f} FPS, {frame_cycles} cycles/frame")

    running = True
    keyboard_mode = "TYPING"
    pygame.display.set_caption(f"ZX Spectrum Emulator - {keyboard_mode} MODE")
    held_physical_keys = {}
    start_real_time = time.perf_counter()
    next_frame_time_ns = time.perf_counter_ns()
    
    total_samples_rendered = 0
    
    while running:
        loop_start = time.perf_counter()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F4:
                keyboard_mode = "GAME" if keyboard_mode == "TYPING" else "TYPING"
                pygame.display.set_caption(f"ZX Spectrum Emulator - {keyboard_mode} MODE")
                print(f"--- Saturnin: Klávesnice přepnuta do režimu {keyboard_mode} ---")
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F8:
                debug_enabled = not debug_enabled
                current_width = WINDOW_WIDTH_DEBUG if debug_enabled else WINDOW_WIDTH
                screen = pygame.display.set_mode((current_width, WINDOW_HEIGHT))
                pygame.display.set_caption(f"ZX Spectrum Emulator - {keyboard_mode} MODE")
                debugger.surface = screen # Update surface reference
                if not debug_enabled:
                    debugger.paused = False # Resume if disabling debugger
            
            # Pass events to debugger only if enabled
            if debug_enabled:
                debugger.handle_input(event)
            
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                pressed = (event.type == pygame.KEYDOWN)
                if pressed:
                    mappings = []
                    is_number_row = (pygame.K_0 <= event.key <= pygame.K_9)
                    
                    if keyboard_mode == "TYPING" and not is_number_row and hasattr(event, 'unicode') and event.unicode in UNICODE_MAP:
                        mappings = UNICODE_MAP[event.unicode]
                    elif event.key in EXTENDED_KEY_MAP:
                        mappings = EXTENDED_KEY_MAP[event.key]
                    elif event.key in KEY_MAP:
                        mappings = [KEY_MAP[event.key]]
                    
                    if mappings:
                        held_physical_keys[event.key] = mappings
                else:
                    if event.key in held_physical_keys:
                        del held_physical_keys[event.key]
                
                # Přepočítáme celou matici klávesnice pro vyřešení konfliktů a aliasů
                for row_addr in ula.keyboard_rows:
                    ula.keyboard_rows[row_addr] = 0x1F
                
                # Zjištění, jestli nedržíme nějaký alias obsahující Symbol Shift
                has_ss_alias = False
                for mappings in held_physical_keys.values():
                    for row, bit in mappings:
                        if (row, bit) == (0x7F, 1):
                            has_ss_alias = True
                            break
                            
                # Aplikace všech aktuálně stisknutých kláves
                for mappings in held_physical_keys.values():
                    for row, bit in mappings:
                        # Pokud píšeme znak přes alias s SS, fyzický Shift (CS) se musí "zamlčet"
                        if has_ss_alias and (row, bit) == (0xFE, 0):
                            continue
                        ula.set_key(row, bit, True)
        
        # Execution Logic
        t0 = time.perf_counter()
        cycles_before = cpu.cycles
        if debug_enabled and debugger.paused:
            if debugger.step_requested:
                try:
                    # Execute one instruction (step)
                    cpu.step()
                except Exception as e:
                    print(f'CPU Error (Step): {e}')
                    debugger.paused = True # Remain paused on error
                debugger.step_requested = False
            else:
                # Idle (no CPU cycles)
                pass
        else:
            # Normal Execution
            # Vytvoření I/O událostí včetně VBLANK přerušení
            # Na ZX Spectru se maskovatelné přerušení generuje automaticky
            target_cycles = cpu.cycles + frame_cycles
            try:
                while cpu.cycles < target_cycles:
                    cpu.step()
            except Exception as e:
                print(f'CPU Error: {e}')
                if debug_enabled:
                    debugger.paused = True
            # Hardware timers specific behavior at end of frame
            if hasattr(memory, 'is_zx80') and memory.is_zx80:
                frames = memory.read_word(16414)
                memory.write_word(16414, (frames - 1) & 0xFFFF)
            elif hasattr(memory, 'is_zx81') and memory.is_zx81:
                frames = memory.read_word(16436)
                memory.write_word(16436, (frames - 1) & 0xFFFF)
            elif cpu.iff1:
                cpu.interrupt()
            
            # Zpracování zvuku pro aktuální snímek:
        
        actual_cycles = cpu.cycles - cycles_before
        t_cpu = (time.perf_counter() - t0) * 1000
                
        # Audio Rendering
        # Calculate samples needed for this frame to maintain long-term sync
        if not hasattr(main, 'frame_count'): main.frame_count = 0
        main.frame_count += 1
        
        target_total_samples = int(main.frame_count * SAMPLE_RATE / target_fps)
        samples_to_render = target_total_samples - total_samples_rendered
        
        ay_obj = hw128.ay if is_128k else None
        audio_buffer = ula.render_audio(samples_to_render, actual_cycles, ay=ay_obj)
        total_samples_rendered += samples_to_render
        
        if not (debug_enabled and debugger.paused):
            audio_engine.add_samples(audio_buffer)
        
        t1 = time.perf_counter()
        buffer = ula.render_screen()
        t_render = (time.perf_counter() - t1) * 1000
        
        surface = pygame.image.frombuffer(buffer, (SCREEN_WIDTH, SCREEN_HEIGHT), 'RGB')
        scaled = pygame.transform.scale(surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.blit(scaled, (0, 0))
        
        # Draw Debug Info
        if debug_enabled:
            debugger.draw(cpu, memory, ula)
        
        pygame.display.flip()
        
        # Frame Rate Limiter (Precise 50Hz)
        now_ns = time.perf_counter_ns()
        elapsed_ns = now_ns - next_frame_time_ns
        
        if elapsed_ns < 0:
            # We are ahead, sleep
            sleep_sec = -elapsed_ns / 1_000_000_000.0
            if sleep_sec > 0.002:
                time.sleep(sleep_sec - 0.001)
            
            # Busy wait for the last bit
            while time.perf_counter_ns() < next_frame_time_ns:
                pass
            
            next_frame_time_ns += frame_duration_ns
        else:
             # We are behind
            if elapsed_ns > frame_duration_ns * 5:
                # We are VERY behind (more than 5 frames), reset logic to avoid fast-forward
                next_frame_time_ns = time.perf_counter_ns() + frame_duration_ns
            else:
                # Just catch up by scheduling next frame normally (drift correction)
                next_frame_time_ns += frame_duration_ns

        t_total = (time.perf_counter() - loop_start) * 1000
        
        # Log performance every 100 frames
        if main.frame_count % 100 == 0:
            real_elapsed = time.perf_counter() - start_real_time
            emulated_elapsed = cpu.cycles / 3500000.0
            ratio = emulated_elapsed / real_elapsed if real_elapsed > 0 else 1.0
            print(f"PERF: CPU: {t_cpu:.2f}ms, Render: {t_render:.2f}ms, Total: {t_total:.2f}ms")
            print(f"TIME: Real: {real_elapsed:.2f}s, Emulated: {emulated_elapsed:.2f}s, Ratio: {ratio:.2%}")

    audio_engine.stop()
    pygame.quit()

if __name__ == '__main__':
    print("DEBUG: Script is running as main. Calling main()...")
    
    has_error = False
    try:
        main()
    except Exception as e:
        has_error = True
        import traceback
        traceback.print_exc()
        print(f"DEBUG: Exception in main(): {e}")
    
    if has_error:
        try:
            input("DEBUG: Execution finished with error. Press Enter to exit.")
        except (EOFError, KeyboardInterrupt):
            pass
            
    import os
    os._exit(0)
