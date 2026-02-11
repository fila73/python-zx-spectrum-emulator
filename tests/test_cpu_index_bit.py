import unittest
from src.cpu import Z80
from src.memory import Memory

class TestCPUIndexBit(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = Z80(self.memory)
        self.cpu.sp = 0xFFFF

    def test_ddcb_rotate(self):
        # RLC (IX+d) -> DD CB d 06
        # Rotates (IX+d) left circular.
        self.cpu.ix = 0x9000
        self.memory.write_byte(0x9005, 0x80) # (IX+5) = 10000000 -> Rotate Left -> 00000001 (0x01), C=1
        
        self.memory.write_byte(0x8000, 0xDD)
        self.memory.write_byte(0x8001, 0xCB)
        self.memory.write_byte(0x8002, 0x05) # d = 5
        self.memory.write_byte(0x8003, 0x06) # Opcode for RLC (HL) is CB 06. Here it is DD CB d 06.
        
        self.cpu.pc = 0x8000
        self.cpu.step()
        
        self.assertEqual(self.memory.read_byte(0x9005), 0x01)
        self.assertTrue(self.cpu.f & 0x01) # Carry set

    def test_fdcb_bit(self):
        # BIT 0, (IY+d) -> FD CB d 46
        # Test bit 0 of (IY+d)
        self.cpu.iy = 0x9000
        self.memory.write_byte(0x8FF0, 0x01) # (IY-16) = 00000001
        
        self.memory.write_byte(0x8000, 0xFD)
        self.memory.write_byte(0x8001, 0xCB)
        self.memory.write_byte(0x8002, 0xF0) # d = -16 (240)
        self.memory.write_byte(0x8003, 0x46) # BIT 0, (HL) is CB 46
        
        self.cpu.pc = 0x8000
        self.cpu.step()
        
        # Z flag is set if bit is 0. Here bit 0 is 1. So Z should be 0.
        self.assertFalse(self.cpu.f & 0x40) # Z flag (bit 6) should be 0
        
        # Test BIT 1 (should be 0) -> Z set
        self.memory.write_byte(0x8010, 0xFD)
        self.memory.write_byte(0x8011, 0xCB)
        self.memory.write_byte(0x8012, 0xF0)
        self.memory.write_byte(0x8013, 0x4E) # BIT 1, (HL) is CB 4E
        
        self.cpu.pc = 0x8010
        self.cpu.step()
        self.assertTrue(self.cpu.f & 0x40) # Z flag set

    def test_ddcb_set_res(self):
        # SET 7, (IX+d) -> DD CB d FE
        self.cpu.ix = 0x9100
        self.memory.write_byte(0x9102, 0x00)
        
        self.memory.write_byte(0x8000, 0xDD)
        self.memory.write_byte(0x8001, 0xCB)
        self.memory.write_byte(0x8002, 0x02) # d = 2
        self.memory.write_byte(0x8003, 0xFE) # SET 7, (HL)
        
        self.cpu.pc = 0x8000
        self.cpu.step()
        
        self.assertEqual(self.memory.read_byte(0x9102), 0x80)
        
        # RES 7, (IX+d) -> DD CB d BE
        self.memory.write_byte(0x8010, 0xDD)
        self.memory.write_byte(0x8011, 0xCB)
        self.memory.write_byte(0x8012, 0x02)
        self.memory.write_byte(0x8013, 0xBE) # RES 7, (HL)
        
        self.cpu.pc = 0x8010
        self.cpu.step()
        
        self.assertEqual(self.memory.read_byte(0x9102), 0x00)

if __name__ == '__main__':
    unittest.main()
