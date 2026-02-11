import numpy as np

class ULA:
    def __init__(self, memory, is_128k=False):
        """
        ULA (Uncommitted Logic Array) Chip.
        Handle I/O port 0xFE (Border, Beeper, Keyboard) and Video Rendering.
        Obsluha V/V portu 0xFE (Okraj, Pípák, Klávesnice) a vykreslování videa.
        """
        self.memory = memory
        self.is_128k = is_128k
        self.border_color = 0
        self.last_frame_border_color = 0
        self.mic = 0
        self.beeper = 0
        
        # ... (rest of palette initialization)
        self.palette = [
            (0x00, 0x00, 0x00), # 0: Black
            (0x00, 0x00, 0xD7), # 1: Blue
            (0xD7, 0x00, 0x00), # 2: Red
            (0xD7, 0x00, 0xD7), # 3: Magenta
            (0x00, 0xD7, 0x00), # 4: Green
            (0x00, 0xD7, 0xD7), # 5: Cyan
            (0xD7, 0xD7, 0x00), # 6: Yellow
            (0xD7, 0xD7, 0xD7), # 7: White
            
            (0x00, 0x00, 0x00), # 8: Bright Black
            (0x00, 0x00, 0xFF), # 9: Bright Blue
            (0xFF, 0x00, 0x00), # 10: Bright Red
            (0xFF, 0x00, 0xFF), # 11: Bright Magenta
            (0x00, 0xFF, 0x00), # 12: Bright Green
            (0x00, 0xFF, 0xFF), # 13: Bright Cyan
            (0xFF, 0xFF, 0x00), # 14: Bright Yellow
            (0xFF, 0xFF, 0xFF), # 15: Bright White
        ]
        self.np_palette = np.array(self.palette, dtype=np.uint8)
        
        # Pre-allocate screen buffer
        self.screen_width = 256 + 64
        self.screen_height = 192 + 64
        self.screen_buffer = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)

        # Pre-calculate VRAM scanline addresses
        # Předvýpočet adres skenovacích řádků VRAM
        self.line_addresses = np.zeros(192, dtype=np.uint16)
        for y in range(192):
            section = (y >> 6) & 0x03
            char_row = (y >> 3) & 0x07
            pixel_row = y & 0x07
            # In 128K, we address relative to the bank start (0x0000-0x3FFF)
            # but for 48K it's absolute (0x4000-0x7FFF)
            # Actually, let's keep it relative to bank start if we use get_bank_data
            hi = (section << 3) | pixel_row
            self.line_addresses[y] = (hi << 8) | (char_row << 5)

        # Keyboard matrix state
        self.keyboard_rows = {
            0xFE: 0x1F, # SHIFT, Z, X, C, V
            0xFD: 0x1F, # A, S, D, F, G
            0xFB: 0x1F, # Q, W, E, R, T
            0xF7: 0x1F, # 1, 2, 3, 4, 5
            0xEF: 0x1F, # 0, 9, 8, 7, 6
            0xDF: 0x1F, # P, O, I, U, Y
            0xBF: 0x1F, # ENTER, L, K, J, H
            0x7F: 0x1F  # SPACE, SYM, M, N, B
        }
        
        # Audio state
        self.cpu = None
        self.audio_events = [] # List of (cycle, speaker_val) tuples
        self.border_events = [] # List of (cycle, color) tuples
        self.last_audio_cycle = 0
        self.render_beeper_state = 0 # Track state for rendering continuity
        
        # Video state
        self.flash_counter = 0

        # Timing constants
        if is_128k:
            # 128K Spectrum
            self.CYCLES_PER_FRAME = 70908
            self.CYCLES_PER_LINE = 228
            self.LINES_BEFORE_SCREEN = 63
        else:
            # 48K Spectrum
            self.CYCLES_PER_FRAME = 69888
            self.CYCLES_PER_LINE = 224
            self.LINES_BEFORE_SCREEN = 64
            
        self.SCREEN_START_CYCLE = self.LINES_BEFORE_SCREEN * self.CYCLES_PER_LINE
        self.CONTENTION_PATTERN = [6, 5, 4, 3, 2, 1, 0, 0]

    def set_cpu(self, cpu):
        """
        Link CPU to ULA for cycle timing.
        Propojení CPU s ULA pro časování.
        """
        self.cpu = cpu

    def get_contention(self, cycle, address, is_io=False):
        """
        Calculate contention delay for a given cycle and address.
        48K: RAM between 0x4000 and 0x7FFF is contended.
        128K: Banks 1, 3, 5, 7 are contended.
        I/O: Ports with bit 0 = 0, or ports in contended range.
        """
        if not is_io:
            is_contended = False
            if not self.is_128k:
                if 0x4000 <= (address & 0xFFFF) <= 0x7FFF:
                    is_contended = True
            else:
                addr = address & 0xFFFF
                if 0x4000 <= addr < 0x8000:
                    # Bank 5 is always here and it is contended
                    is_contended = True
                elif addr >= 0xC000:
                    # Bankable RAM
                    bank = self.memory.current_ram_bank
                    if bank in [1, 3, 5, 7]:
                        is_contended = True
                        
            if not is_contended:
                return 0
                
            return self._calculate_contention(cycle)
        else:
            # I/O Contention
            port = address & 0xFFFF
            is_contended = False
            
            if (port & 0x0001) == 0:
                # ULA port is always contended
                is_contended = True
            else:
                # Non-ULA port might be contended if in contended RAM range
                if not self.is_128k:
                    if 0x4000 <= port <= 0x7FFF: # Wait, high byte 0x40-0x7F
                        is_contended = True
                else:
                    # 128K I/O contention is more complex, but usually same range check
                    if 0x4000 <= port < 0x8000:
                        is_contended = True
                    elif port >= 0xC000:
                        bank = self.memory.current_ram_bank
                        if bank in [1, 3, 5, 7]:
                            is_contended = True
            
            if not is_contended:
                return 0
                
            # I/O contention adds 4 cycles of potential delay
            # T1, T2, T3, T4
            delay = 0
            curr_cycle = cycle
            for _ in range(4):
                d = self._calculate_contention(curr_cycle)
                delay += d
                curr_cycle += d + 1
            return delay

    def _calculate_contention(self, cycle):
        """Internal helper to calculate contention for a single cycle."""
        rel_cycle = cycle % self.CYCLES_PER_FRAME
        
        # Is it in the screen area?
        if rel_cycle < self.SCREEN_START_CYCLE:
            return 0
            
        screen_cycle = rel_cycle - self.SCREEN_START_CYCLE
        line = screen_cycle // self.CYCLES_PER_LINE
        
        if line >= 192:
            return 0
            
        line_cycle = screen_cycle % self.CYCLES_PER_LINE
        
        # First 128 cycles of each line are contended
        if line_cycle < 128:
            return self.CONTENTION_PATTERN[line_cycle % 8]
            
        return 0

    def get_floating_bus_value(self, cycle):
        """
        Get the value currently on the floating bus.
        Returns the byte being read by the ULA, or 0xFF if idle.
        Získá hodnotu aktuálně na plovoucí sběrnici.
        Vrací bajt právě čtený ULA nebo 0xFF, pokud je nečinná.
        """
        rel_cycle = cycle % self.CYCLES_PER_FRAME
        
        if rel_cycle < self.SCREEN_START_CYCLE:
            return 0xFF
            
        screen_cycle = rel_cycle - self.SCREEN_START_CYCLE
        line = screen_cycle // self.CYCLES_PER_LINE
        
        if line >= 192:
            return 0xFF
            
        line_cycle = screen_cycle % self.CYCLES_PER_LINE
        
        # ULA fetches 2 bytes every 8 cycles:
        # T=0: Bitmap, T=1: Attribute, T=2: Bitmap, T=3: Attribute ... NO.
        # Fetch pattern:
        # T=0: Bitmap
        # T=1: Attribute
        # T=2: Bitmap (of next char?) No.
        # Correct fetch pattern for 48K:
        # Each 8 cycles (one character):
        # 0: Bitmap
        # 1: Attribute
        # 2: Bitmap (same char, redundant?) No, it fetches for the NEXT pair of pixels?
        # Actually:
        # 0: Bitmap
        # 1: Attribute
        # 2: Bitmap
        # 3: Attribute
        # ... it fetches 2 bytes every 4 cycles?
        # Chris Smith:
        # T=0: Bitmap
        # T=1: Attribute
        # T=2: Idle
        # T=3: Idle
        # T=4: Bitmap
        # T=5: Attribute
        # T=6: Idle
        # T=7: Idle
        
        if line_cycle >= 128:
            return 0xFF
            
        phase = line_cycle % 8
        
        # Determine which bank ULA is reading from
        if self.is_128k:
            vram_bank = self.memory.get_bank_data(self.memory.screen_bank)
        else:
            vram_bank = self.memory.memory[0x4000:0x8000]

        if phase == 0 or phase == 4:
            # Fetch bitmap
            char_x = line_cycle // 4
            addr = self.line_addresses[line] + char_x
            return vram_bank[addr]
        elif phase == 1 or phase == 5:
            # Fetch attribute
            char_x = line_cycle // 4
            char_y = line >> 3
            # Attribute start at 0x1800 relative to bank start
            addr = 0x1800 + (char_y * 32) + char_x
            return vram_bank[addr]
            
        return 0xFF

    def read_port(self, port):
        """
        Read from port.
        Respond to even ports (bit 0 = 0).
        """
        if (port & 1) == 0:
            high_byte = (port >> 8) & 0xFF
            result = 0x1F # Start with all keys released
            
            for row_mask, row_state in self.keyboard_rows.items():
                is_selected = False
                # Row selection logic: bit in high byte corresponding to row is 0
                if row_mask == 0xFE and not (high_byte & 0x01): is_selected = True
                elif row_mask == 0xFD and not (high_byte & 0x02): is_selected = True
                elif row_mask == 0xFB and not (high_byte & 0x04): is_selected = True
                elif row_mask == 0xF7 and not (high_byte & 0x08): is_selected = True
                elif row_mask == 0xEF and not (high_byte & 0x10): is_selected = True
                elif row_mask == 0xDF and not (high_byte & 0x20): is_selected = True
                elif row_mask == 0xBF and not (high_byte & 0x40): is_selected = True
                elif row_mask == 0x7F and not (high_byte & 0x80): is_selected = True
                
                if is_selected:
                    result &= row_state
            
            result |= 0xA0 # Set bits 5 and 7 to 1
            return result
        return None

    def write_port(self, port, value):
        """
        Write to port.
        Respond to even ports (bit 0 = 0).
        """
        if (port & 1) == 0:
            # Record state change for audio
            # Speaker state depends on MIC and EAR/Beeper bit
            # Bit 4: Beeper/EAR
            # Bit 3: MIC
            new_beeper = (value >> 4) & 0x01
            new_mic = (value >> 3) & 0x01
            
            if new_beeper != self.beeper or new_mic != self.mic:
                # Value changed, record event
                current_cycle = self.cpu.cycles if self.cpu else 0
                
                # Combine bits for 4 levels
                # Levels: 00 -> 40, 01 -> 80, 10 -> 160, 11 -> 200
                level = 40
                if new_beeper and new_mic: level = 200
                elif new_beeper: level = 160
                elif new_mic: level = 80
                
                self.audio_events.append((current_cycle, level))
            
            current_cycle = self.cpu.cycles if self.cpu else 0
            new_border = value & 0x07
            if new_border != self.border_color:
                # Record relative cycle in frame
                rel_cycle = current_cycle % self.CYCLES_PER_FRAME
                self.border_events.append((rel_cycle, new_border))
            
            self.border_color = new_border
            self.mic = new_mic
            self.beeper = new_beeper

    def set_key(self, row_addr, key_bit, pressed):
        """
        Simulate key press/release.
        """
        if row_addr in self.keyboard_rows:
            mask = 1 << key_bit
            if pressed:
                self.keyboard_rows[row_addr] &= ~mask
            else:
                self.keyboard_rows[row_addr] |= mask

    def render_audio(self, samples_per_frame, cycles_per_frame, ay=None):
        """
        Generate audio samples for the current frame.
        Generovat audio vzorky pro aktuální snímek.
        
        :param samples_per_frame: Number of samples to generate.
        :param cycles_per_frame: Total CPU cycles in this frame.
        :param ay: Optional AY38910 instance for 128K sound.
        :return: bytes object with unsigned 8-bit PCM data.
        """
        start_cycle = self.last_audio_cycle
        end_cycle = start_cycle + cycles_per_frame
        
        # Avoid division by zero if no cycles executed
        if cycles_per_frame <= 0:
            return b'\x00' * samples_per_frame        
        # Avoid division by zero if no cycles executed
        if cycles_per_frame <= 0:
            return b'\x00' * samples_per_frame
        
        # We use floats for mixing
        beeper_samples = np.zeros(samples_per_frame, dtype=np.float32)
        
        # State at start of frame is the last rendered state
        state = self.render_beeper_state
        
        # Collect relevant events
        relevant_events = []
        for e in self.audio_events:
            if e[0] < end_cycle:
                relevant_events.append(e)
        
        # Sort events by cycle
        relevant_events.sort(key=lambda x: x[0])
        
        # Add a sentinel event at the end cycle to fill the last span
        relevant_events.append((end_cycle, state))
        
        sample_idx = 0
        for cycle, next_state in relevant_events:
            event_cycle = max(cycle, start_cycle)
            next_sample_idx = int((event_cycle - start_cycle) * samples_per_frame / cycles_per_frame)
            next_sample_idx = max(sample_idx, min(next_sample_idx, samples_per_frame))
                
            # Fill buffer with current state until this event
            # Normalize beeper to 0.0 - 1.0 range
            beeper_samples[sample_idx:next_sample_idx] = (state / 255.0)
                
            sample_idx = next_sample_idx
            state = next_state
            
        # Update state for next frame
        self.render_beeper_state = state
        self.last_audio_cycle = end_cycle
        
        # Remove processed events
        self.audio_events = [e for e in self.audio_events if e[0] >= end_cycle]
        
        if ay:
            ay_samples = ay.render_audio(samples_per_frame, 22050)
            
            if ay_samples.ndim == 2:
                # Stereo mixing
                mixed = np.zeros((samples_per_frame, 2), dtype=np.float32)
                # Beeper is mono, so copy it to both channels
                mixed[:, 0] = (beeper_samples * 0.5) + (ay_samples[:, 0] * 0.5)
                mixed[:, 1] = (beeper_samples * 0.5) + (ay_samples[:, 1] * 0.5)
            else:
                # Mono mixing expanded to Stereo
                mixed = np.zeros((samples_per_frame, 2), dtype=np.float32)
                combined = (beeper_samples * 0.5) + (ay_samples * 0.5)
                mixed[:, 0] = combined
                mixed[:, 1] = combined
        else:
            # Beeper Only - Expand to Stereo
            mixed = np.zeros((samples_per_frame, 2), dtype=np.float32)
            mixed[:, 0] = beeper_samples
            mixed[:, 1] = beeper_samples
            
        # Return float32 array (0.0 - 1.0)
        return mixed

    def render_screen(self):
        """
        Render the Spectrum screen to a buffer.
        Uses border_events for cycle-accurate border rendering.
        Returns raw RGB data 320x256 (including 32px border).
        """
        # Reuse pre-allocated buffer
        buffer = self.screen_buffer
        
        # Sort border events just in case
        self.border_events.sort(key=lambda x: x[0])
        
        # Pre-calculate border color for each scanline
        line_border_colors = np.zeros(self.screen_height, dtype=np.uint8)
        current_event_idx = 0
        current_color = self.last_frame_border_color
        
        for y in range(self.screen_height):
            # Approximate cycle for this scanline
            line_cycle = y * self.CYCLES_PER_LINE
            
            while current_event_idx < len(self.border_events) and self.border_events[current_event_idx][0] <= line_cycle:
                current_color = self.border_events[current_event_idx][1]
                current_event_idx += 1
            line_border_colors[y] = current_color

        # Fill buffer with line colors (Border)
        for y in range(self.screen_height):
            buffer[y, :] = self.np_palette[line_border_colors[y]]
        
        # Update for next frame
        self.last_frame_border_color = current_color
        self.border_events = []
        
        # Handle flash timing
        flash_active = (self.flash_counter >> 4) & 1
        self.flash_counter = (self.flash_counter + 1) % 32
        
        # Get correct VRAM data
        if self.is_128k:
            vram_bank = self.memory.get_bank_data(self.memory.screen_bank)
        else:
            # For 48K, video is at 0x4000 offset in memory.memory
            vram_bank = self.memory.memory[0x4000:0x8000]
            
        vram = np.frombuffer(vram_bank, dtype=np.uint8)
        
        # Attributes are 32x24 (768 bytes starting at 0x1800 relative to bank start)
        attr_data = vram[0x1800:0x1800+768].reshape((24, 32))
        
        ink = attr_data & 0x07
        paper = (attr_data >> 3) & 0x07
        bright = (attr_data >> 6) & 0x01
        flash = (attr_data >> 7) & 0x01
        
        if flash_active:
            flash_mask = (flash != 0)
            tmp_ink = ink.copy()
            ink[flash_mask] = paper[flash_mask]
            paper[flash_mask] = tmp_ink[flash_mask]
            
        ink = ink + (bright << 3)
        paper = paper + (bright << 3)
        
        border_size = 32
        screen_view = buffer[border_size:border_size+192, border_size:border_size+256]
        
        for y in range(192):
            char_y = y >> 3
            line_addr = self.line_addresses[y]
            line_data = vram[line_addr:line_addr+32]
            
            bits = np.unpackbits(line_data)
            line_ink = ink[char_y].repeat(8)
            line_paper = paper[char_y].repeat(8)
            
            color_indices = np.where(bits, line_ink, line_paper)
            screen_view[y] = self.np_palette[color_indices]
            
        return buffer
