import unittest
from src.cpu import Z80
from src.memory import Memory

class TestCPU_Block(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = Z80(self.memory)

    def test_ex_de_hl(self):
        """Test EX DE, HL (0xEB)"""
        self.cpu.de = 0x1234
        self.cpu.hl = 0x5678
        
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xEB)
        
        self.cpu.step()
        self.assertEqual(self.cpu.de, 0x5678)
        self.assertEqual(self.cpu.hl, 0x1234)

    def test_ex_af_af_alt(self):
        """Test EX AF, AF' (0x08)"""
        self.cpu.af = 0x1234
        self.cpu.a_alt = 0x56
        self.cpu.f_alt = 0x78
        
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0x08)
        
        self.cpu.step()
        self.assertEqual(self.cpu.af, 0x5678)
        self.assertEqual(self.cpu.a_alt, 0x12)
        self.assertEqual(self.cpu.f_alt, 0x34) # Check low byte

    def test_exx(self):
        """Test EXX (0xD9)"""
        self.cpu.bc = 0x1111
        self.cpu.de = 0x2222
        self.cpu.hl = 0x3333
        
        self.cpu.b_alt = 0x44; self.cpu.c_alt = 0x44
        self.cpu.d_alt = 0x55; self.cpu.e_alt = 0x55
        self.cpu.h_alt = 0x66; self.cpu.l_alt = 0x66
        
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xD9)
        
        self.cpu.step()
        
        self.assertEqual(self.cpu.bc, 0x4444)
        self.assertEqual(self.cpu.de, 0x5555)
        self.assertEqual(self.cpu.hl, 0x6666)
        
        # Check alternates implicitly by swapping back
        self.cpu.pc = 0x8000 # execute EXX again
        self.cpu.step()
        
        self.assertEqual(self.cpu.bc, 0x1111)

    def test_ex_sp_hl(self):
        """Test EX (SP), HL (0xE3)"""
        self.cpu.hl = 0x1234
        self.cpu.sp = 0x9000
        self.memory.write_byte(0x9000, 0x78)
        self.memory.write_byte(0x9001, 0x56) # Stack has 0x5678
        
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xE3)
        
        self.cpu.step()
        
        self.assertEqual(self.cpu.hl, 0x5678)
        self.assertEqual(self.memory.read_byte(0x9000), 0x34)
        self.assertEqual(self.memory.read_byte(0x9001), 0x12)

    def test_ldi(self):
        """Test LDI (0xED 0xA0)"""
        # copy byte from HL to DE, inc HL, inc DE, dec BC
        self.cpu.hl = 0x9000
        self.cpu.de = 0x9100
        self.cpu.bc = 0x0001
        
        self.memory.write_byte(0x9000, 0xAA)
        
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xED)
        self.memory.write_byte(0x8001, 0xA0)
        
        self.cpu.step()
        
        self.assertEqual(self.memory.read_byte(0x9100), 0xAA)
        self.assertEqual(self.cpu.hl, 0x9001)
        self.assertEqual(self.cpu.de, 0x9101)
        self.assertEqual(self.cpu.bc, 0x0000)
        # P/V flag is reset if BC=0
        self.assertFalse(self.cpu.f & 0x04)

    def test_ldir(self):
        """Test LDIR (0xED 0xB0)"""
        # Copy 3 bytes
        self.cpu.hl = 0x9000
        self.cpu.de = 0x9100
        self.cpu.bc = 0x0003
        
        self.memory.write_byte(0x9000, 0x11)
        self.memory.write_byte(0x9001, 0x22)
        self.memory.write_byte(0x9002, 0x33)
        
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xED)
        self.memory.write_byte(0x8001, 0xB0)
        
        # LDIR acts like a loop. One step executes one LDI and decrements PC by 2 if BC!=0
        
        # Step 1
        self.cpu.step() 
        self.assertEqual(self.memory.read_byte(0x9100), 0x11)
        self.assertEqual(self.cpu.bc, 0x0002)
        self.assertEqual(self.cpu.pc, 0x8000) # PC should point back to LDIR
        
        # Step 2
        self.cpu.step()
        self.assertEqual(self.memory.read_byte(0x9101), 0x22)
        self.assertEqual(self.cpu.bc, 0x0001)
        self.assertEqual(self.cpu.pc, 0x8000)
        
        # Step 3
        self.cpu.step()
        self.assertEqual(self.memory.read_byte(0x9102), 0x33)
        self.assertEqual(self.cpu.bc, 0x0000)
        self.assertEqual(self.cpu.pc, 0x8002) # PC should advance
        
    # TODO: Add CPI/CPD/CPIR tests if needed, but LDI/LDIR are most critical for now.

if __name__ == '__main__':
    unittest.main()
