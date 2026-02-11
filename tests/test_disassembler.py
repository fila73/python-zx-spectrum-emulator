import unittest
from src.memory import Memory
from src.disassembler import Disassembler

class TestDisassembler(unittest.TestCase):
    def setUp(self):
        self.d = Disassembler()
        self.memory = Memory()

    def test_nop(self):
        self.memory.write_byte(0x8000, 0x00)
        mnem, length, bytes_str = self.d.disassemble(self.memory, 0x8000)
        self.assertEqual(mnem, "NOP")
        self.assertEqual(length, 1)

    def test_ld_registers(self):
        # LD A, B (0x78)
        self.memory.write_byte(0x8000, 0x78)
        mnem, length, _ = self.d.disassemble(self.memory, 0x8000)
        self.assertEqual(mnem, "LD A, B")

    def test_immediate(self):
        # LD A, n (0x3E 0x05)
        self.memory.write_byte(0x8000, 0x3E)
        self.memory.write_byte(0x8001, 0x05)
        mnem, length, bytes_str = self.d.disassemble(self.memory, 0x8000)
        self.assertEqual(mnem, "LD A, 0x05")
        self.assertEqual(length, 2)
        self.assertIn("3E", bytes_str)
        self.assertIn("05", bytes_str)

    def test_extended_jumps(self):
        # JP nn (0xC3 0x00 0x80) -> JP 0x8000
        self.memory.write_byte(0x8000, 0xC3)
        self.memory.write_byte(0x8001, 0x00)
        self.memory.write_byte(0x8002, 0x80)
        mnem, length, _ = self.d.disassemble(self.memory, 0x8000)
        self.assertEqual(mnem, "JP 0x8000")
        self.assertEqual(length, 3)

    def test_cb_prefix(self):
        # RLC B (CB 00)
        self.memory.write_byte(0x8000, 0xCB)
        self.memory.write_byte(0x8001, 0x00)
        mnem, length, _ = self.d.disassemble(self.memory, 0x8000)
        self.assertEqual(mnem, "RLC B")
        self.assertEqual(length, 2)

    def test_ed_prefix(self):
        # LDIR (ED B0)
        self.memory.write_byte(0x8000, 0xED)
        self.memory.write_byte(0x8001, 0xB0)
        mnem, length, _ = self.d.disassemble(self.memory, 0x8000)
        self.assertEqual(mnem, "LDIR")
        self.assertEqual(length, 2)

    def test_jr_displacement(self):
        # JR -2 (0x18 0xFE)
        self.memory.write_byte(0x8000, 0x18)
        self.memory.write_byte(0x8001, 0xFE) # -2
        mnem, length, _ = self.d.disassemble(self.memory, 0x8000)
        # 0xFE is 254. 254-256 = -2.
        self.assertEqual(mnem, "JR -2")
        
if __name__ == '__main__':
    unittest.main()
