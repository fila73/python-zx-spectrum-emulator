import unittest
from src.ula import ULA

class TestULA(unittest.TestCase):
    def setUp(self):
        from src.memory import Memory
        self.memory = Memory()
        self.ula = ULA(self.memory)

    def test_border_color(self):
        # Write to bits 0-2 of 0xFE sets border
        self.ula.write_port(0xFE, 0x03) # Magenta
        self.assertEqual(self.ula.border_color, 3)
        self.assertEqual(self.ula.mic, 0)
        self.assertEqual(self.ula.beeper, 0)

    def test_beeper_mic(self):
        # Bit 3 = MIC, Bit 4 = Beeper
        self.ula.write_port(0xFE, 0x18) # MIC=1, Beeper=1
        self.assertEqual(self.ula.mic, 1)
        self.assertEqual(self.ula.beeper, 1)

    def test_keyboard_scan_no_press(self):
        # Read port 0xFEFE (Shift-V row selected)
        # Expect 0x1F (all keys released 11111) in lower 5 bits case
        # bits 5,7=1, bit 6=0 (EAR) -> 10111111 ? 
        # My implementation returns 0xA0 | keys.
        # keys=0x1F. 0xA0 | 0x1F = 0xBF.
        
        # bit 0-4: 11111 (all released)
        # bit 5: 1
        # bit 6: 0 (EAR)
        # bit 7: 1
        # Result: 11011111 = 0xDF? 
        # Wait, implementation says: result |= 0xA0.
        # 0xA0 is 10100000.
        # If keys are 0x1F (00011111).
        # Result: 10111111 = 0xBF.
        
        val = self.ula.read_port(0xFEFE)
        self.assertEqual(val & 0x1F, 0x1F)

    def test_keyboard_press(self):
        # Press Z (Row 0xFE, bit 1)
        self.ula.set_key(0xFE, 1, True)
        
        # Read row 0xFE
        val = self.ula.read_port(0xFEFE)
        # Bit 1 should be 0. 0x1F & ~0x02 = 0x1D.
        self.assertEqual(val & 0x1F, 0x1D)
        
        # Read another row, e.g. 0x7F (Space..)
        val_other = self.ula.read_port(0x7FFE)
        # Should be unnafected (0x1F)
        self.assertEqual(val_other & 0x1F, 0x1F)

    def test_keyboard_multi_row(self):
        # Press Z (Row 0xFE) and SPACE (Row 0x7F)
        self.ula.set_key(0xFE, 1, True) # Z
        self.ula.set_key(0x7F, 0, True) # Space
        
        # Select both rows: port 0x7EFE (Binary high byte 01111110)
        # 0x7E = 01111110. Bit 0 (FE) is 0. Bit 7 (7F) is 0.
        # So both rows selected.
        # Result should be AND of both rows.
        # Row FE: 11101 (Z pressed)
        # Row 7F: 11110 (Space pressed)
        # AND:    11100
        
        val = self.ula.read_port(0x7EFE)
        self.assertEqual(val & 0x1F, 0x1C) # 0x1D & 0x1E = 0x1C

if __name__ == '__main__':
    unittest.main()
