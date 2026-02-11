
import unittest
import sys
import os

# Add src to path
sys.path.append('/home/fila/projects/vscode/python/python-zx-spectrum-emulator/src')

from cpu import Z80
from memory import Memory

class TestMissingStandard(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = Z80(self.memory)
        self.cpu.sp = 0xFFFF
        self.CODE_ADDR = 0x8000
        self.cpu.pc = self.CODE_ADDR

    def test_accumulator_rotates(self):
        # RLCA (0x07)
        # bit 7 -> C, bit 7 -> bit 0
        self.cpu.a = 0x81 # 1000 0001
        self.memory.write_byte(self.CODE_ADDR, 0x07)
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0x03) # 0000 0011
        self.assertEqual(self.cpu.f & 0x01, 1) # Carry set

        # RRCA (0x0F)
        # bit 0 -> C, bit 0 -> bit 7
        self.cpu.a = 0x81 # 1000 0001
        self.memory.write_byte(self.CODE_ADDR + 1, 0x0F)
        self.cpu.pc = self.CODE_ADDR + 1
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0xC0) # 1100 0000
        self.assertEqual(self.cpu.f & 0x01, 1) # Carry set

        # RLA (0x17)
        # bit 7 -> C, old C -> bit 0
        self.cpu.a = 0x80 # 1000 0000
        self.cpu.f = 0x01 # C = 1
        self.memory.write_byte(self.CODE_ADDR + 2, 0x17)
        self.cpu.pc = self.CODE_ADDR + 2
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0x01) # 0000 0001
        self.assertEqual(self.cpu.f & 0x01, 1) # Carry set

        # RRA (0x1F)
        # bit 0 -> C, old C -> bit 7
        self.cpu.a = 0x01 # 0000 0001
        self.cpu.f = 0x01 # C = 1
        self.memory.write_byte(self.CODE_ADDR + 3, 0x1F)
        self.cpu.pc = self.CODE_ADDR + 3
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0x80) # 1000 0000
        self.assertEqual(self.cpu.f & 0x01, 1) # Carry set

    def test_push_af(self):
        # PUSH AF (0xF5)
        # A=0x55, F=0x42 -> SP-1 = 0x55, SP-2 = 0x42
        self.cpu.sp = 0x9000
        self.cpu.a = 0x55
        self.cpu.f = 0x42
        self.memory.write_byte(self.CODE_ADDR, 0xF5)
        self.memory.write_byte(self.CODE_ADDR + 1, 0x00) # NOP
        
        pc_before = self.cpu.pc
        self.cpu.step()
        
        self.assertEqual(self.cpu.pc, pc_before + 1)
        self.assertEqual(self.memory.read_byte(0x8FFF), 0x55) # High
        self.assertEqual(self.memory.read_byte(0x8FFE), 0x42) # Low
        self.assertEqual(self.cpu.sp, 0x8FFE)

if __name__ == '__main__':
    unittest.main()
