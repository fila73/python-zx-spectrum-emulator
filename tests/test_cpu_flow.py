import unittest
from src.cpu import Z80
from src.memory import Memory

class TestCPU_Flow(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = Z80(self.memory)
        self.cpu.sp = 0xFFFF

    def test_jp_nn(self):
        """Test JP nn (0xC3)"""
        # JP 0x8050
        self.cpu.pc = 0x4000
        self.memory.write_byte(0x4000, 0xC3)
        self.memory.write_byte(0x4001, 0x50)
        self.memory.write_byte(0x4002, 0x80)
        
        self.cpu.step()
        self.assertEqual(self.cpu.pc, 0x8050)

    def test_jp_hl(self):
        """Test JP (HL) (0xE9)"""
        self.cpu.hl = 0x1234
        self.cpu.pc = 0x4000
        self.memory.write_byte(0x4000, 0xE9)
        
        self.cpu.step()
        self.assertEqual(self.cpu.pc, 0x1234)

    def test_jr_e_positive(self):
        """Test JR e (0x18) with positive offset"""
        # JR +5
        self.cpu.pc = 0x4000
        self.memory.write_byte(0x4000, 0x18)
        self.memory.write_byte(0x4001, 0x05)
        
        # PC should be: 4000 + 2 (instr len) + 5 = 4007
        self.cpu.step()
        self.assertEqual(self.cpu.pc, 0x4007)

    def test_jr_e_negative(self):
        """Test JR e (0x18) with negative offset"""
        # JR -3 (0xFD)
        self.cpu.pc = 0x4010
        self.memory.write_byte(0x4010, 0x18)
        self.memory.write_byte(0x4011, 0xFD) # -3 signed
        
        # PC should be: 4010 + 2 (instr len) - 3 = 400F
        self.cpu.step()
        self.assertEqual(self.cpu.pc, 0x400F)

    def test_call_ret(self):
        """Test CALL nn (0xCD) and RET (0xC9)"""
        # CALL 0x8000
        self.cpu.pc = 0x4000
        self.cpu.sp = 0xFFFF
        self.memory.write_byte(0x4000, 0xCD)
        self.memory.write_byte(0x4001, 0x00)
        self.memory.write_byte(0x4002, 0x80)
        
        self.cpu.step()
        self.assertEqual(self.cpu.pc, 0x8000)
        # Stack should contain return address (0x4003)
        # SP decrements by 2. FFFD=low(03), FFFE=high(40)
        self.assertEqual(self.cpu.sp, 0xFFFD)
        self.assertEqual(self.memory.read_byte(0xFFFD), 0x03)
        self.assertEqual(self.memory.read_byte(0xFFFE), 0x40)
        
        # RET from 0x8000
        self.memory.write_byte(0x8000, 0xC9)
        self.cpu.step()
        self.assertEqual(self.cpu.pc, 0x4003)
        self.assertEqual(self.cpu.sp, 0xFFFF)

    def test_jp_z_taken(self):
        """Test JP Z, nn taken"""
        self.cpu.f |= 0x40 # Set Z flag
        self.cpu.pc = 0x4000
        self.memory.write_byte(0x4000, 0xCA) # JP Z, nn
        self.memory.write_byte(0x4001, 0x50)
        self.memory.write_byte(0x4002, 0x80)
        
        self.cpu.step()
        self.assertEqual(self.cpu.pc, 0x8050)

    def test_jp_z_not_taken(self):
        """Test JP Z, nn not taken"""
        self.cpu.f &= ~0x40 # Clear Z flag
        self.cpu.pc = 0x4000
        self.memory.write_byte(0x4000, 0xCA) # JP Z, nn
        self.memory.write_byte(0x4001, 0x50)
        self.memory.write_byte(0x4002, 0x80)
        
        self.cpu.step()
        self.assertEqual(self.cpu.pc, 0x4003) # Next instruction

    def test_rst_38(self):
        """Test RST 38H (0xFF)"""
        self.cpu.pc = 0x4000
        self.memory.write_byte(0x4000, 0xFF) # RST 38H
        
        self.cpu.step()
        self.assertEqual(self.cpu.pc, 0x0038)
        # Stack check
        self.assertEqual(self.memory.read_byte(self.cpu.sp), 0x01) # Low byte of return addr (4001)
        self.assertEqual(self.memory.read_byte(self.cpu.sp+1), 0x40)

if __name__ == '__main__':
    unittest.main()
