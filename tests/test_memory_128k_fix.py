import unittest
from src.memory import Memory

class TestMemory128KFix(unittest.TestCase):
    def setUp(self):
        self.memory = Memory(is_128k=True)

    def test_port_7ffd_bit_logic(self):
        # Default state
        self.assertEqual(self.memory.current_ram_bank, 0)
        self.assertEqual(self.memory.current_rom_bank, 0)
        self.assertEqual(self.memory.screen_bank, 5)
        
        # Test RAM Bank Select (Bits 0-2)
        # 0x01 -> Bank 1
        self.memory.write_port_7ffd(0x01)
        self.assertEqual(self.memory.current_ram_bank, 1)
        
        # Test Screen Select (Bit 3)
        # 0x08 -> Shadow Screen (Bank 7)
        self.memory.write_port_7ffd(0x08)
        self.assertEqual(self.memory.screen_bank, 7)
        self.assertEqual(self.memory.current_ram_bank, 0) # Reset ram bank to 0
        
        # 0x00 -> Normal Screen (Bank 5)
        self.memory.write_port_7ffd(0x00)
        self.assertEqual(self.memory.screen_bank, 5)
        
        # Test ROM Select (Bit 4)
        # 0x10 -> ROM 1 (48K BASIC)
        self.memory.write_port_7ffd(0x10)
        self.assertEqual(self.memory.current_rom_bank, 1)
        
        # 0x00 -> ROM 0 (128K Editor)
        self.memory.write_port_7ffd(0x00)
        self.assertEqual(self.memory.current_rom_bank, 0)
        
        # Test Combined
        # 0x1B (0001 1011) -> RAM 3, Screen 1 (Shadow), ROM 1
        self.memory.write_port_7ffd(0x1B)
        self.assertEqual(self.memory.current_ram_bank, 3)
        self.assertEqual(self.memory.screen_bank, 7)
        self.assertEqual(self.memory.current_rom_bank, 1)

if __name__ == '__main__':
    unittest.main()
