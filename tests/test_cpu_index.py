import unittest
from src.cpu import Z80
from src.memory import Memory

class TestCPUIndex(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = Z80(self.memory)
        self.cpu.sp = 0xFFFF

    def test_ix_registers(self):
        # LD IX, nn - DD 21 nn nn
        self.memory.write_byte(0x8000, 0xDD)
        self.memory.write_byte(0x8001, 0x21)
        self.memory.write_word(0x8002, 0x1234)
        
        self.cpu.pc = 0x8000
        self.cpu.step()
        self.assertEqual(self.cpu.ix, 0x1234)
        
        # LD SP, IX - DD F9
        self.memory.write_byte(0x8010, 0xDD)
        self.memory.write_byte(0x8011, 0xF9)
        
        self.cpu.pc = 0x8010
        self.cpu.step()
        self.assertEqual(self.cpu.sp, 0x1234)

    def test_iy_registers(self):
        # LD IY, nn - FD 21 nn nn
        self.memory.write_byte(0x8000, 0xFD)
        self.memory.write_byte(0x8001, 0x21)
        self.memory.write_word(0x8002, 0x5678)
        
        self.cpu.pc = 0x8000
        self.cpu.step()
        self.assertEqual(self.cpu.iy, 0x5678)

    def test_indexed_addressing_load(self):
        # LD A, (IX+d) - DD 7E d
        self.cpu.ix = 0x9000
        self.memory.write_byte(0x9005, 0xAA) # (IX+5)
        
        self.memory.write_byte(0x8000, 0xDD)
        self.memory.write_byte(0x8001, 0x7E)
        self.memory.write_byte(0x8002, 0x05) # d = 5
        
        self.cpu.pc = 0x8000
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0xAA)
        
        # Negative displacement
        # LD B, (IX-5) - DD 46 d
        self.memory.write_byte(0x8FFB, 0xBB) # (IX-5) = 9000 - 5 = 8FFB
        
        self.memory.write_byte(0x8010, 0xDD)
        self.memory.write_byte(0x8011, 0x46)
        self.memory.write_byte(0x8012, 0xFB) # d = -5 (251)
        
        self.cpu.pc = 0x8010
        self.cpu.step()
        self.assertEqual(self.cpu.b, 0xBB)

    def test_indexed_addressing_store(self):
        # LD (IY+d), C - FD 71 d
        self.cpu.iy = 0x9000
        self.cpu.c = 0xCC
        
        self.memory.write_byte(0x8000, 0xFD)
        self.memory.write_byte(0x8001, 0x71)
        self.memory.write_byte(0x8002, 0x10) # d = 16
        
        self.cpu.pc = 0x8000
        self.cpu.step()
        self.assertEqual(self.memory.read_byte(0x9010), 0xCC)

    def test_indexed_arithmetic(self):
        # ADD IX, DE - DD 19
        self.cpu.ix = 0x1000
        self.cpu.de = 0x0500
        
        self.memory.write_byte(0x8000, 0xDD)
        self.memory.write_byte(0x8001, 0x19)
        
        self.cpu.pc = 0x8000
        self.cpu.step()
        self.assertEqual(self.cpu.ix, 0x1500)
        
        # INC IY - FD 23
        self.cpu.iy = 0xFFFF
        
        self.memory.write_byte(0x8010, 0xFD)
        self.memory.write_byte(0x8011, 0x23)
        
        self.cpu.pc = 0x8010
        self.cpu.step()
        self.assertEqual(self.cpu.iy, 0x0000)

if __name__ == '__main__':
    unittest.main()
