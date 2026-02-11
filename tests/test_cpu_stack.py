import unittest
from src.cpu import Z80
from src.memory import Memory

class TestCPU_Stack(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = Z80(self.memory)
        # Set SP to a safe RAM area for stack tests
        self.cpu.sp = 0xFFFF 

    def test_add_hl_bc(self):
        """Test ADD HL, BC (0x09)"""
        # HL = 0x1000, BC = 0x2000 -> HL = 0x3000
        self.cpu.hl = 0x1000
        self.cpu.bc = 0x2000
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0x09) # ADD HL, BC
        self.cpu.step()
        
        self.assertEqual(self.cpu.hl, 0x3000)
        # ADD HL, ss affects N (reset) and C (carry), but NOT Z, S, P/V
        self.assertEqual(self.cpu.f & 0x02, 0) # N reset

    def test_add_hl_overflow(self):
        """Test ADD HL, HL with carry"""
        # HL = 0x8000. 0x8000 + 0x8000 = 0x0000 (Carry)
        self.cpu.hl = 0x8000
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0x29) # ADD HL, HL
        self.cpu.step()
        
        self.assertEqual(self.cpu.hl, 0x0000)
        self.assertTrue(self.cpu.f & 0x01) # Carry set

    def test_inc_de_16(self):
        """Test INC DE (0x13)"""
        # DE = 0x12FF -> 0x1300
        self.cpu.de = 0x12FF
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0x13) # INC DE
        self.cpu.step()
        
        self.assertEqual(self.cpu.de, 0x1300)
        # 16-bit INC does NOT affect flags
        self.assertEqual(self.cpu.f, 0)

    def test_push_pop_bc(self):
        """Test PUSH BC and POP BC"""
        self.cpu.bc = 0x1234
        self.cpu.sp = 0xF000
        
        # PUSH BC (0xC5)
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xC5)
        self.cpu.step()
        
        self.assertEqual(self.cpu.sp, 0xEFFE) # Decremented by 2
        # Check memory (Little Endian? No, Z80 stacks push high byte then low byte -> Low address has low byte)
        # Wait, Z80 PUSH rr:
        # SP-1 <- high byte
        # SP-2 <- low byte
        # SP <- SP-2
        # So at SP (EFFE) is low byte (34), at SP+1 (EFFF) is high byte (12)
        self.assertEqual(self.memory.read_byte(0xEFFE), 0x34)
        self.assertEqual(self.memory.read_byte(0xEFFF), 0x12)
        
        # Clear BC
        self.cpu.bc = 0x0000
        
        # POP BC (0xC1)
        self.cpu.pc = 0x8001
        self.memory.write_byte(0x8001, 0xC1)
        self.cpu.step()
        
        self.assertEqual(self.cpu.sp, 0xF000)
        self.assertEqual(self.cpu.bc, 0x1234)

if __name__ == '__main__':
    unittest.main()
