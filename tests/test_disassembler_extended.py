import unittest
from src.disassembler import Disassembler

class MockMemory:
    def __init__(self, data, start_addr=0):
        self.data = data
        self.start_addr = start_addr
        
    def read_byte(self, addr):
        offset = addr - self.start_addr
        if 0 <= offset < len(self.data):
            return self.data[offset]
        return 0

class TestDisassemblerExtended(unittest.TestCase):
    def setUp(self):
        self.dis = Disassembler()
        
    def test_ix_displacement(self):
        # DD 7E 05 -> LD A, (IX+5)
        # 7E is LD A, (HL) in standard
        data = [0xDD, 0x7E, 0x05]
        mem = MockMemory(data, 0x100)
        mnemonic, length, bytes_str = self.dis.disassemble(mem, 0x100)
        self.assertEqual(mnemonic, "LD A, (IX+5)")
        self.assertEqual(length, 3)
        
    def test_iy_displacement_negative(self):
        # FD 7E FF -> LD A, (IY-1)
        data = [0xFD, 0x7E, 0xFF]
        mem = MockMemory(data, 0x100)
        mnemonic, length, bytes_str = self.dis.disassemble(mem, 0x100)
        self.assertEqual(mnemonic, "LD A, (IY-1)")
        self.assertEqual(length, 3)
        
    def test_ix_literal_load(self):
        # DD 36 05 10 -> LD (IX+5), 0x10
        # 36 is LD (HL), n
        data = [0xDD, 0x36, 0x05, 0x10]
        mem = MockMemory(data, 0x100)
        mnemonic, length, bytes_str = self.dis.disassemble(mem, 0x100)
        self.assertEqual(mnemonic, "LD (IX+5), 0x10")
        self.assertEqual(length, 4)
        
    def test_ix_register_replace(self):
        # DD 21 00 10 -> LD IX, 0x1000
        # 21 is LD HL, nn
        data = [0xDD, 0x21, 0x00, 0x10]
        mem = MockMemory(data, 0x100)
        mnemonic, length, bytes_str = self.dis.disassemble(mem, 0x100)
        self.assertEqual(mnemonic, "LD IX, 0x1000")
        self.assertEqual(length, 4)
        
    def test_ix_add(self):
        # DD 09 -> ADD IX, BC
        # 09 is ADD HL, BC
        data = [0xDD, 0x09]
        mem = MockMemory(data, 0x100)
        mnemonic, length, bytes_str = self.dis.disassemble(mem, 0x100)
        self.assertEqual(mnemonic, "ADD IX, BC")
        self.assertEqual(length, 2)
        
    def test_ddcb_bit(self):
        # DD CB 05 46 -> BIT 0, (IX+5)
        # CB 46 is BIT 0, (HL) in standard CB map
        data = [0xDD, 0xCB, 0x05, 0x46]
        mem = MockMemory(data, 0x100)
        mnemonic, length, bytes_str = self.dis.disassemble(mem, 0x100)
        self.assertEqual(mnemonic, "BIT 0, (IX+5)")
        self.assertEqual(length, 4)
        
    def test_ed_load_16bit(self):
        # ED 43 00 20 -> LD (0x2000), BC
        # 43 is LD (nn), BC (Standard ED)
        data = [0xED, 0x43, 0x00, 0x20]
        mem = MockMemory(data, 0x100)
        mnemonic, length, bytes_str = self.dis.disassemble(mem, 0x100)
        self.assertEqual(mnemonic, "LD (0x2000), BC")
        self.assertEqual(length, 4)

    def test_ed_block_io(self):
        # ED B3 -> OTIR
        data = [0xED, 0xB3]
        mem = MockMemory(data, 0x100)
        mnemonic, length, _ = self.dis.disassemble(mem, 0x100)
        self.assertEqual(mnemonic, "OTIR")
        self.assertEqual(length, 2)

    def test_ed_special_loads(self):
        # ED 57 -> LD A, I
        data = [0xED, 0x57]
        mem = MockMemory(data, 0x100)
        mnemonic, length, _ = self.dis.disassemble(mem, 0x100)
        self.assertEqual(mnemonic, "LD A, I")
        self.assertEqual(length, 2)

    def test_ddcb_copy_undocumented(self):
        # DD CB 05 00 -> RLC (IX+5), B
        # Op 00 is RLC B. In DDCB, it does (IX+5) and copies to B.
        data = [0xDD, 0xCB, 0x05, 0x00]
        mem = MockMemory(data, 0x100)
        mnemonic, length, _ = self.dis.disassemble(mem, 0x100)
        self.assertEqual(mnemonic, "RLC (IX+5), B")
        self.assertEqual(length, 4)

    def test_fd_ld_iy_nn(self):
        # FD 21 34 12 -> LD IY, 0x1234
        data = [0xFD, 0x21, 0x34, 0x12]
        mem = MockMemory(data, 0x100)
        mnemonic, length, _ = self.dis.disassemble(mem, 0x100)
        self.assertEqual(mnemonic, "LD IY, 0x1234")
        self.assertEqual(length, 4)
        
if __name__ == '__main__':
    unittest.main()
