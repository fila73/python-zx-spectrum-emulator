import unittest
from src.memory import Memory

class TestMemory(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()

    def test_initialization(self):
        """Test that memory is initialized to 64KB of zeros."""
        self.assertEqual(len(self.memory.memory), 65536)
        self.assertEqual(self.memory.read_byte(0), 0)
        self.assertEqual(self.memory.read_byte(0xFFFF), 0)

    def test_load_rom_valid(self):
        """Test loading a valid ROM."""
        rom_data = b'\x01\x02\x03\x04'
        self.memory.load_rom(rom_data)
        self.assertEqual(self.memory.read_byte(0), 1)
        self.assertEqual(self.memory.read_byte(3), 4)

    def test_load_rom_too_large(self):
        """Test loading a ROM larger than 16KB raises ValueError."""
        large_rom = bytearray(16385) # 16K + 1
        with self.assertRaises(ValueError):
            self.memory.load_rom(large_rom)

    def test_rom_write_protection(self):
        """Test that writing to ROM area (0x0000-0x3FFF) fails (silently or otherwise)."""
        # Load some ROM data first
        self.memory.load_rom(b'\xAA')
        self.assertEqual(self.memory.read_byte(0), 0xAA)
        
        # Try to write to ROM address
        self.memory.write_byte(0, 0xFF)
        
        # Should still be original value
        self.assertEqual(self.memory.read_byte(0), 0xAA)

    def test_ram_read_write(self):
        """Test reading and writing to RAM area."""
        ram_addr = 0x8000
        self.memory.write_byte(ram_addr, 0x55)
        self.assertEqual(self.memory.read_byte(ram_addr), 0x55)

if __name__ == '__main__':
    unittest.main()
