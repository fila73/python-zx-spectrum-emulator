import unittest
from src.cpu import Z80
from src.memory import Memory

class TestCPU(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = Z80(self.memory)

    def test_initial_state(self):
        """Test initial CPU state (registers zeroed)."""
        self.assertEqual(self.cpu.pc, 0)
        self.assertEqual(self.cpu.sp, 0)
        self.assertEqual(self.cpu.a, 0)

    def test_nop(self):
        """Test NOP instruction (0x00)."""
        # Load NOP at 0x0000 (RAM/ROM) - actually we can't write to ROM area easily without bypass
        # But we can simulate memory content or just write to RAM and set PC there
        
        # Method 1: Write to RAM and set PC
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0x00) # NOP
        
        self.cpu.step()
        self.assertEqual(self.cpu.pc, 0x8001)

    def test_di_ei(self):
        """Test DI (0xF3) and EI (0xFB) instructions."""
        # DI
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xF3)
        self.cpu.iff1 = 1
        self.cpu.iff2 = 1
        
        self.cpu.step()
        self.assertEqual(self.cpu.pc, 0x8001)
        self.assertEqual(self.cpu.iff1, 0)
        self.assertEqual(self.cpu.iff2, 0)

        # EI
        self.memory.write_byte(0x8001, 0xFB)
        self.cpu.step()
        self.assertEqual(self.cpu.pc, 0x8002)
        self.assertEqual(self.cpu.iff1, 1)
        self.assertEqual(self.cpu.iff2, 1)

    def test_ld_r_n(self):
        """Test LD r, n instruction (e.g., LD A, 0x55)."""
        # Opcode for LD A, n is 0x3E
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0x3E)
        self.memory.write_byte(0x8001, 0x55)
        
        self.cpu.step()
        
        self.assertEqual(self.cpu.pc, 0x8002)
        self.assertEqual(self.cpu.a, 0x55)
        
    def test_ld_r_r(self):
        """Test LD r, r' instruction (e.g., LD A, B)."""
        # Opcode for LD A, B is 0x78
        self.cpu.pc = 0x8000
        self.cpu.b = 0x99
        self.cpu.a = 0x00
        self.memory.write_byte(0x8000, 0x78)
        
        self.cpu.step()
        
        self.assertEqual(self.cpu.pc, 0x8001)
        self.assertEqual(self.cpu.a, 0x99)

if __name__ == '__main__':
    unittest.main()
