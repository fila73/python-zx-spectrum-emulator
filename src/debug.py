import pygame

class Debugger:
    def __init__(self, surface, font, x, y):
        self.surface = surface
        self.font = font
        self.x = x
        self.y = y
        self.line_height = 20
        self.text_color = (255, 255, 255) # White
        self.bg_color = (30, 30, 30) # Dark Gray
        self.hl_color = (60, 60, 60) # Highlight Gray
        
        from src.disassembler import Disassembler
        self.disassembler = Disassembler()
        
        # Execution State
        self.paused = False
        self.step_requested = False

    def handle_input(self, event):
        """
        Handle input events for the debugger.
        Zpracování vstupních událostí pro debugger.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAUSE or event.key == pygame.K_BREAK:
                self.paused = not self.paused
            elif event.key == pygame.K_F5:
                self.paused = False
            elif event.key == pygame.K_F10 or event.key == pygame.K_F11: # Step
                self.paused = True
                self.step_requested = True
                
    def draw(self, cpu, memory, ula=None):
        """
        Render all debug information.
        Vykreslit veškeré ladicí informace.
        """
        # Clear debug area (Full height)
        debug_rect = pygame.Rect(self.x, self.y, 300, self.surface.get_height()) 
        pygame.draw.rect(self.surface, self.bg_color, debug_rect)
        
        current_y = self.y + 10
        x_offset = self.x + 10

        # Title / Toolbar
        status_color = (255, 0, 0) if self.paused else (0, 255, 0)
        status_text = "PAUSED" if self.paused else "RUNNING"
        title = self.font.render(f"DEBUGGER [{status_text}]", True, status_color)
        self.surface.blit(title, (x_offset, current_y))
        current_y += 30

        help_text = "F5: Run  F10: Step  Pause: Break"
        self._draw_text(help_text, x_offset, current_y, (150, 150, 150))
        current_y += 30

        # 1. Registers
        self._draw_text(f"PC: {hex(cpu.pc)}  SP: {hex(cpu.sp)}", x_offset, current_y)
        current_y += self.line_height
        
        self._draw_text(f"AF: {hex(cpu.af)}  BC: {hex(cpu.bc)}", x_offset, current_y)
        current_y += self.line_height
        
        self._draw_text(f"DE: {hex(cpu.de)}  HL: {hex(cpu.hl)}", x_offset, current_y)
        current_y += self.line_height
        
        self._draw_text(f"IX: {hex(cpu.ix)}  IY: {hex(cpu.iy)}", x_offset, current_y)
        current_y += self.line_height
        
        self._draw_text(f"I:  {hex(cpu.i)}   R:  {hex(cpu.r)}", x_offset, current_y)
        current_y += self.line_height + 10

        # 2. Flags
        # SZ5H3PNC
        flags = cpu.f
        flag_str = "S Z 5 H 3 P N C"
        val_str = ""
        for i in range(7, -1, -1):
            bit = (flags >> i) & 1
            val_str += str(bit) + " "
            
        self._draw_text("FLAGS:", x_offset, current_y, (200, 200, 200))
        current_y += self.line_height
        self._draw_text(flag_str, x_offset, current_y, (150, 150, 150))
        current_y += self.line_height
        self._draw_text(val_str, x_offset, current_y)
        current_y += self.line_height + 10
        
        # 3. Code View (Disassembler)
        self._draw_text("CODE:", x_offset, current_y, (200, 200, 200))
        current_y += self.line_height
        
        pc = cpu.pc
        for i in range(10): # Show next 10 instructions
            mnemonic, length, bytes_str = self.disassembler.disassemble(memory, pc)
            
            # Highlight current PC
            if i == 0:
                rect = pygame.Rect(self.x, current_y, 300, self.line_height)
                pygame.draw.rect(self.surface, self.hl_color, rect)
                
            text = f"{hex(pc)[2:].zfill(4)}: {bytes_str.ljust(10)} {mnemonic}"
            self._draw_text(text, x_offset, current_y)
            current_y += self.line_height
            pc = (pc + length) & 0xFFFF
            
        current_y += 10

        # 4. Keyboard State
        if ula:
            self._draw_text("KEYBOARD ROWS (0=Pressed):", x_offset, current_y, (200, 200, 200))
            current_y += self.line_height
            
            # Sort keys for consistent display
            for row in sorted(ula.keyboard_rows.keys(), reverse=True):
                val = ula.keyboard_rows[row]
                # Convert to binary string of 5 bits
                bits = bin(val)[2:].zfill(5)[-5:]
                self._draw_text(f"{hex(row).upper()}: {bits}", x_offset, current_y)
                current_y += self.line_height
            current_y += 10

        # 5. Stack
        self._draw_text("STACK (Top 8):", x_offset, current_y, (200, 200, 200))
        current_y += self.line_height
        
        sp = cpu.sp
        for i in range(0, 16, 2):
            addr = (sp + i) & 0xFFFF
            try:
                # Read word (little endian)
                low = memory.read_byte(addr)
                high = memory.read_byte((addr + 1) & 0xFFFF)
                word = (high << 8) | low
                self._draw_text(f"{hex(addr)}: {hex(word)}", x_offset, current_y)
            except:
                self._draw_text(f"{hex(addr)}: ????", x_offset, current_y)
            current_y += self.line_height

        # 6. State
        current_y += 10
        self._draw_text(f"IM: {cpu.im}  IFF1: {cpu.iff1} IFF2: {cpu.iff2}", x_offset, current_y)
        current_y += self.line_height
        self._draw_text(f"T-States: {cpu.cycles}", x_offset, current_y)
        
        # 7. Memory Banks (128K only)
        if hasattr(memory, 'is_128k') and memory.is_128k:
            current_y += 10
            self._draw_text("128K BANKING:", x_offset, current_y, (200, 200, 200))
            current_y += self.line_height
            rom = "ROM 1 (48K)" if memory.current_rom_bank else "ROM 0 (128K)"
            self._draw_text(f"ROM:  {rom}", x_offset, current_y)
            current_y += self.line_height
            self._draw_text(f"RAM:  Bank {memory.current_ram_bank} at 0xC000", x_offset, current_y)
            current_y += self.line_height
            screen = "Bank 7" if memory.screen_bank == 7 else "Bank 5"
            self._draw_text(f"SCR:  {screen}", x_offset, current_y)
            current_y += self.line_height
            lock = "LOCKED" if memory.paging_locked else "UNLOCKED"
            self._draw_text(f"PAGING: {lock}", x_offset, current_y)
            current_y += self.line_height

    def _draw_text(self, text, x, y, color=None):
        if color is None:
            color = self.text_color
        surface = self.font.render(text, True, color)
        self.surface.blit(surface, (x, y))
