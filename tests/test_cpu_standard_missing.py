import unittest
from src.cpu import Z80
from src.memory import Memory

class TestStandardMissing(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = Z80(self.memory)
        
    def test_rlca(self):
        # RLCA: Rotate Left Circular passed bit 7 to bit 0 and Carry
        self.cpu.a = 0x81 # 1000 0001
        self.cpu.f = 0
        self.cpu._rlca()
        # 1000 0001 << 1 = 0000 0010 | 1 = 0000 0011 (0x03)
        # Carry should be 1 (old bit 7)
        self.assertEqual(self.cpu.a, 0x03)
        self.assertEqual(self.cpu.f & 1, 1) # Carry set
        
        self.cpu.a = 0x01
        self.cpu._rlca()
        # 0000 0001 << 1 = 0000 0010 (0x02)
        # Carry should be 0
        self.assertEqual(self.cpu.a, 0x02)
        self.assertEqual(self.cpu.f & 1, 0)
        
    def test_rrca(self):
        # RRCA: Rotate Right Circular passed bit 0 to bit 7 and Carry
        self.cpu.a = 0x01 # 0000 0001
        self.cpu.f = 0
        self.cpu._rrca()
        # 0000 0001 >> 1 = 0000 0000 | (1<<7) = 1000 0000 (0x80)
        # Carry should be 1
        self.assertEqual(self.cpu.a, 0x80)
        self.assertEqual(self.cpu.f & 1, 1)
        
    def test_rla(self):
        # RLA: Rotate Left through Carry
        # Old Carry -> Bit 0, Bit 7 -> New Carry
        self.cpu.a = 0x80 # 1000 0000
        self.cpu.f = 1 # Carry set
        self.cpu._rla()
        # 1000 0000 << 1 = 0000 0000 | 1 (Old C) = 0000 0001 (0x01)
        # New Carry = 1 (Old Bit 7)
        self.assertEqual(self.cpu.a, 0x01)
        self.assertEqual(self.cpu.f & 1, 1)
        
    def test_rra(self):
        # RRA: Rotate Right through Carry
        # Old Carry -> Bit 7, Bit 0 -> New Carry
        self.cpu.a = 0x01 # 0000 0001
        self.cpu.f = 1 # Carry set
        self.cpu._rra()
        # 0000 0001 >> 1 = 0000 0000 | (1<<7) = 1000 0000 (0x80)
        # New Carry = 1 (Old Bit 0)
        self.assertEqual(self.cpu.a, 0x80)
        self.assertEqual(self.cpu.f & 1, 1)
        
    def test_pop_af(self):
        # Push 0x1234, then POP AF
        # SP usually at top
        self.cpu.sp = 0xFFFE
        self.memory.write_byte(0xFFFE, 0x34) # F (Flags)
        self.memory.write_byte(0xFFFF, 0x12) # A
        
        # POP AF
        self.cpu._pop_qq('af')
        
        self.assertEqual(self.cpu.a, 0x12)
        self.assertEqual(self.cpu.f, 0x34)
        self.assertEqual(self.cpu.sp, 0x0000) # Wrapped to 0
        
        # Verify F register behavior implies low byte
        self.cpu.af = 0xABCD
        self.assertEqual(self.cpu.a, 0xAB)
        self.assertEqual(self.cpu.f, 0xCD)

if __name__ == '__main__':
    unittest.main()
