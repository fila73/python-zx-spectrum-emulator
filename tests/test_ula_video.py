import unittest
from src.memory import Memory
from src.ula import ULA

class TestULAVideo(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.ula = ULA(self.memory)

    def test_render_bitmap_pattern(self):
        # Write a pattern to VRAM (Bitmap)
        # Address 0x4000 is top-left corner
        # Write 0xFF (all pixels on)
        self.memory.write_byte(0x4000, 0xFF)
        
        # Attribute for this block (0,0) is at 0x5800
        # Ink: Blue (1), Paper: Yellow (6), Bright: 0, Flash: 0
        # Attr: 00 001 110 = 0x0E? No.
        # Format: F B PPP III
        # Paper 6 (110), Ink 1 (001) -> 00 110 001 = 0x31
        self.memory.write_byte(0x5800, 0x31)
        self.memory.write_byte(0x5801, 0x31) # Set for second byte too
        
        buffer = self.ula.render_screen()
        
        # Buffer is bytearray RGB
        # Top-left of MAIN SCREEN (at offset 32, 32)
        # Width including border is 320
        border_offset = 32
        width = 320
        
        # Check first pixel of main screen
        # buffer is (256, 320, 3)
        pixel = buffer[border_offset, border_offset]
        r, g, b = pixel[0], pixel[1], pixel[2]
        self.assertEqual((r, g, b), (0x00, 0x00, 0xD7)) # Blue
        
        # Check 8th pixel of main screen
        pixel8 = buffer[border_offset, border_offset + 7]
        r, g, b = pixel8[0], pixel8[1], pixel8[2]
        self.assertEqual((r, g, b), (0x00, 0x00, 0xD7)) # Blue
        
        # Check next set of pixels (which are 0 in VRAM -> PAPER color)
        # Address 0x4001, value 0x00
        self.memory.write_byte(0x4001, 0x00)
        
        # Re-render
        buffer = self.ula.render_screen()
        
        # Pixel at x=8 (next byte)
        pixel_x8 = buffer[border_offset, border_offset + 8]
        r, g, b = pixel_x8[0], pixel_x8[1], pixel_x8[2]
        self.assertEqual((r, g, b), (0xD7, 0xD7, 0x00)) # Yellow

    def test_buffer_size(self):
        buffer = self.ula.render_screen()
        # 320 x 256 x 3
        self.assertEqual(buffer.shape, (256, 320, 3))

if __name__ == '__main__':
    unittest.main()
