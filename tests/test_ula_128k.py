import pytest
import numpy as np
from src.memory import Memory
from src.ula import ULA
from src.hardware_128k import Hardware128K

def test_ula_128k_shadow_screen():
    mem = Memory(is_128k=True)
    ula = ULA(mem, is_128k=True)
    hw = Hardware128K(mem)
    
    # Default screen is Bank 5
    assert mem.screen_bank == 5
    
    # Fill bank 5 and bank 7 with different values
    bank5 = mem.get_bank_data(5)
    bank7 = mem.get_bank_data(7)
    
    bank5[0x1800] = 1 # Attribute at (0,0) in Bank 5
    bank7[0x1800] = 2 # Attribute at (0,0) in Bank 7
    
    # Render with Bank 5 (default)
    screen = ula.render_screen()
    # screen[32:40, 32:40] is first character block (including border)
    # The palette index for paper should be the attribute value if ink is 0 (which it is)
    # Actually, attributes are: bit 0-2 ink, 3-5 paper, 6 bright, 7 flash
    # If attr is 1: ink=1 (Blue), paper=0 (Black)
    # If attr is 2: ink=2 (Red), paper=0 (Black)
    
    # Let's check a pixel in the first character block
    # It should be ink color if bitmap is set, but bitmap is all 0, so paper color.
    # Paper color is (attr >> 3) & 0x07.
    # For attr=1: paper=0 (Black)
    # For attr=0x08: paper=1 (Blue)
    
    bank5[0x1800] = 0x08 # Paper = Blue
    bank7[0x1800] = 0x10 # Paper = Red
    
    # Render with Bank 5
    hw.write_port(0x7FFD, 0) # Bit 4 = 0 -> Bank 5
    screen = ula.render_screen()
    # Check pixel (32, 32) which is first pixel of main screen
    # Blue is (0, 0, 0xD7)
    assert tuple(screen[32, 32]) == (0, 0, 0xD7)
    
    # Switch to Bank 7
    hw.write_port(0x7FFD, 0x10) # Bit 4 = 1 -> Bank 7
    assert mem.screen_bank == 7
    screen = ula.render_screen()
    # Red is (0xD7, 0, 0)
    assert tuple(screen[32, 32]) == (0xD7, 0, 0)

def test_ula_128k_timing():
    mem = Memory(is_128k=True)
    ula_128k = ULA(mem, is_128k=True)
    ula_48k = ULA(mem, is_128k=False)
    
    assert ula_128k.CYCLES_PER_FRAME == 70908
    assert ula_48k.CYCLES_PER_FRAME == 69888
    
    assert ula_128k.CYCLES_PER_LINE == 228
    assert ula_48k.CYCLES_PER_LINE == 224
