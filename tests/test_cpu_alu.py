import unittest
from src.cpu import Z80
from src.memory import Memory

class TestCPU_ALU(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = Z80(self.memory)

    def test_add_a_n(self):
        """Test ADD A, n (0xC6)"""
        # 20 + 30 = 50
        self.cpu.a = 20
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xC6) # ADD A, n
        self.memory.write_byte(0x8001, 30)
        self.cpu.step()
        
        self.assertEqual(self.cpu.a, 50)
        self.assertEqual(self.cpu.f & 0x80, 0) # S (Sign) not set
        self.assertEqual(self.cpu.f & 0x40, 0) # Z (Zero) not set
        self.assertEqual(self.cpu.f & 0x01, 0) # C (Carry) not set

    def test_add_overflow(self):
        """Test ADD A, n with overflow/carry"""
        # 255 + 1 = 0 (Carry)
        self.cpu.a = 255
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xC6)
        self.memory.write_byte(0x8001, 1)
        self.cpu.step()
        
        self.assertEqual(self.cpu.a, 0)
        self.assertTrue(self.cpu.f & 0x01) # Carry set
        self.assertTrue(self.cpu.f & 0x40) # Zero set

    def test_sub_a_n(self):
        """Test SUB n (0xD6)"""
        # 50 - 30 = 20
        self.cpu.a = 50
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xD6) # SUB n
        self.memory.write_byte(0x8001, 30)
        self.cpu.step()
        
        self.assertEqual(self.cpu.a, 20)
        self.assertEqual(self.cpu.f & 0x01, 0) # No Carry/Borrow

    def test_sub_borrow(self):
        """Test SUB n with borrow"""
        # 10 - 20 = -10 (246)
        self.cpu.a = 10
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xD6)
        self.memory.write_byte(0x8001, 20)
        self.cpu.step()
        
        self.assertEqual(self.cpu.a, 246)
        self.assertTrue(self.cpu.f & 0x01) # Carry/Borrow set
        self.assertTrue(self.cpu.f & 0x80) # Sign set

    def test_and_a_n(self):
        """Test AND n (0xE6)"""
        # 0b1100 & 0b1010 = 0b1000 (8)
        self.cpu.a = 0b1100
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xE6) # AND n
        self.memory.write_byte(0x8001, 0b1010)
        self.cpu.step()
        
        self.assertEqual(self.cpu.a, 8)
        self.assertTrue(self.cpu.f & 0x10) # H flag is set for AND ops

    def test_or_a_n(self):
        """Test OR n (0xF6)"""
        # 0b1100 | 0b0011 = 0b1111 (15)
        self.cpu.a = 0b1100
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xF6) # OR n
        self.memory.write_byte(0x8001, 0b0011)
        self.cpu.step()
        
        self.assertEqual(self.cpu.a, 15)

    def test_xor_a_n(self):
        """Test XOR n (0xEE)"""
        # 0b1100 ^ 0b1111 = 0b0011 (3)
        self.cpu.a = 0b1100
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xEE) # XOR n
        self.memory.write_byte(0x8001, 0b1111)
        self.cpu.step()
        
        self.assertEqual(self.cpu.a, 3)

    def test_inc_r(self):
        """Test INC A (0x3C)"""
        # 10 -> 11
        self.cpu.a = 10
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0x3C) # INC A
        self.cpu.step()
        
        self.assertEqual(self.cpu.a, 11)
        # Verify Carry is NOT affected by INC (Z80 spec)
        # We'll set carry first
        self.cpu.f = 0x01
        self.cpu.a = 10
        self.cpu.pc = 0x8000
        self.cpu.step()
        self.assertTrue(self.cpu.f & 0x01)

    def test_dec_r(self):
        """Test DEC A (0x3D)"""
        # 10 -> 9
        self.cpu.a = 10
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0x3D) # DEC A
        self.cpu.step()
        
        self.assertEqual(self.cpu.a, 9)

if __name__ == '__main__':
    unittest.main()
