import unittest
from src.cpu import Z80
from src.memory import Memory

class TestCPU_16BitLoads(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = Z80(self.memory)

    def test_ld_dd_nn(self):
        """Test LD dd, nn (0x01, 0x11, 0x21, 0x31)"""
        # LD BC, 0x1234
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0x01)
        self.memory.write_byte(0x8001, 0x34)
        self.memory.write_byte(0x8002, 0x12)
        
        self.cpu.step()
        self.assertEqual(self.cpu.bc, 0x1234)
        self.assertEqual(self.cpu.b, 0x12)
        self.assertEqual(self.cpu.c, 0x34)

        # LD SP, 0x5678
        self.cpu.pc = 0x8010
        self.memory.write_byte(0x8010, 0x31)
        self.memory.write_byte(0x8011, 0x78)
        self.memory.write_byte(0x8012, 0x56)
        
        self.cpu.step()
        self.assertEqual(self.cpu.sp, 0x5678)

    def test_ld_nn_hl(self):
        """Test LD (nn), HL (0x22)"""
        self.cpu.hl = 0xABCD
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0x22)
        self.memory.write_byte(0x8001, 0x00)
        self.memory.write_byte(0x8002, 0x90) # Address 0x9000 (safe RAM)
        
        self.cpu.step()
        
        # Z80 is little-endian. Low byte at addr, High byte at addr+1
        self.assertEqual(self.memory.read_byte(0x9000), 0xCD)
        self.assertEqual(self.memory.read_byte(0x9001), 0xAB)

    def test_ld_hl_nn_indir(self):
        """Test LD HL, (nn) (0x2A)"""
        self.memory.write_byte(0x9000, 0x55)
        self.memory.write_byte(0x9001, 0xAA)
        
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0x2A)
        self.memory.write_byte(0x8001, 0x00)
        self.memory.write_byte(0x8002, 0x90) # Address 0x9000
        
        self.cpu.step()
        self.assertEqual(self.cpu.hl, 0xAA55)

    def test_ld_sp_hl(self):
        """Test LD SP, HL (0xF9)"""
        self.cpu.hl = 0x1000
        self.cpu.sp = 0xFFFF
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xF9)
        
        self.cpu.step()
        self.assertEqual(self.cpu.sp, 0x1000)

if __name__ == '__main__':
    unittest.main()
