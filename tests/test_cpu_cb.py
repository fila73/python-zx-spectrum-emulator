import unittest
from src.cpu import Z80
from src.memory import Memory

class TestCPU_CB(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = Z80(self.memory)

    def test_rlc_a(self):
        """Test RLC A (CB 07)"""
        # Rotate Left Circular: 10000001 -> 00000011, Carry=1
        self.cpu.a = 0x81
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xCB)
        self.memory.write_byte(0x8001, 0x07)
        
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0x03)
        self.assertTrue(self.cpu.f & 0x01) # Carry set

    def test_rrc_b(self):
        """Test RRC B (CB 08)"""
        # Rotate Right Circular: 00000011 -> 10000001, Carry=1
        self.cpu.b = 0x03
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xCB)
        self.memory.write_byte(0x8001, 0x08)
        
        self.cpu.step()
        self.assertEqual(self.cpu.b, 0x81)
        self.assertTrue(self.cpu.f & 0x01) # Carry set

    def test_rl_c(self):
        """Test RL C (CB 11)"""
        # Rotate Left through Carry: C=1, 00000001 -> 00000011, C=0
        self.cpu.c = 0x01
        self.cpu.f = 0x01 # Set Carry
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xCB)
        self.memory.write_byte(0x8001, 0x11)
        
        self.cpu.step()
        self.assertEqual(self.cpu.c, 0x03)
        self.assertFalse(self.cpu.f & 0x01) # Carry cleared (bit 7 was 0)

    def test_rr_d(self):
        """Test RR D (CB 1A)"""
        # Rotate Right through Carry: C=1, 00000010 -> 10000001, C=0
        self.cpu.d = 0x02
        self.cpu.f = 0x01 # Set Carry
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xCB)
        self.memory.write_byte(0x8001, 0x1A)
        
        self.cpu.step()
        self.assertEqual(self.cpu.d, 0x81)
        self.assertFalse(self.cpu.f & 0x01) # Carry cleared

    def test_sla_e(self):
        """Test SLA E (CB 23)"""
        # Shift Left Arithmetic: 11111111 -> 11111110, C=1
        self.cpu.e = 0xFF
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xCB)
        self.memory.write_byte(0x8001, 0x23)
        
        self.cpu.step()
        self.assertEqual(self.cpu.e, 0xFE)
        self.assertTrue(self.cpu.f & 0x01)

    def test_sra_h(self):
        """Test SRA H (CB 2C)"""
        # Shift Right Arithmetic: 10000000 -> 11000000 (sign ext), C=0
        self.cpu.h = 0x80
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xCB)
        self.memory.write_byte(0x8001, 0x2C)
        
        self.cpu.step()
        self.assertEqual(self.cpu.h, 0xC0)
        self.assertFalse(self.cpu.f & 0x01)

    def test_srl_l(self):
        """Test SRL L (CB 3D)"""
        # Shift Right Logical: 10000001 -> 01000000, C=1
        self.cpu.l = 0x81
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xCB)
        self.memory.write_byte(0x8001, 0x3D)
        
        self.cpu.step()
        self.assertEqual(self.cpu.l, 0x40)
        self.assertTrue(self.cpu.f & 0x01)

    def test_bit_0_a(self):
        """Test BIT 0, A (CB 47)"""
        # A=0x01 (00000001). Bit 0 is 1. Z flag should be 0 (Not Zero).
        self.cpu.a = 0x01
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xCB)
        self.memory.write_byte(0x8001, 0x47)
        
        self.cpu.step()
        self.assertFalse(self.cpu.f & 0x40) # Z=0

        # A=0xFE (11111110). Bit 0 is 0. Z flag should be 1 (Zero).
        self.cpu.a = 0xFE
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xCB)
        self.memory.write_byte(0x8001, 0x47)
        
        self.cpu.step()
        self.assertTrue(self.cpu.f & 0x40) # Z=1

    def test_set_7_hl(self):
        """Test SET 7, (HL) (CB FE)"""
        self.cpu.hl = 0x9000
        self.memory.write_byte(0x9000, 0x00)
        
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xCB)
        self.memory.write_byte(0x8001, 0xFE)
        
        self.cpu.step()
        self.assertEqual(self.memory.read_byte(0x9000), 0x80)

    def test_res_3_a(self):
        """Test RES 3, A (CB 9F)"""
        # A=0xFF -> 11110111 (F7)
        self.cpu.a = 0xFF
        self.cpu.pc = 0x8000
        self.memory.write_byte(0x8000, 0xCB)
        self.memory.write_byte(0x8001, 0x9F)
        
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0xF7)

if __name__ == '__main__':
    unittest.main()
