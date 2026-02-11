import unittest
from src.cpu import Z80
from src.memory import Memory

class TestCPUExtended(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = Z80(self.memory, None)
        self.CODE_ADDR = 0x8000
        self.cpu.pc = self.CODE_ADDR

    def test_indirect_loads_store(self):
        # LD (BC), A (0x02)
        base = self.CODE_ADDR
        self.cpu.b = 0x90 # BC = 0x9000
        self.cpu.c = 0x00
        self.cpu.a = 0x42
        self.memory.write_byte(base, 0x02)
        self.cpu.step()
        self.assertEqual(self.memory.read_byte(0x9000), 0x42)
        
        # LD (DE), A (0x12)
        self.cpu.d = 0x90
        self.cpu.e = 0x01
        self.cpu.a = 0x55
        self.memory.write_byte(base + 1, 0x12)
        self.cpu.pc = base + 1
        self.cpu.step()
        self.assertEqual(self.memory.read_byte(0x9001), 0x55)
        
        # LD (nn), A (0x32)
        self.cpu.a = 0x99
        self.memory.write_byte(base + 2, 0x32)
        self.memory.write_word(base + 3, 0x9002)
        self.cpu.pc = base + 2
        self.cpu.step()
        self.assertEqual(self.memory.read_byte(0x9002), 0x99)
        
        # LD (HL), n (0x36)
        self.cpu.h = 0x90
        self.cpu.l = 0x03
        self.memory.write_byte(base + 5, 0x36)
        self.memory.write_byte(base + 6, 0x77)
        self.cpu.pc = base + 5
        self.cpu.step()
        self.assertEqual(self.memory.read_byte(0x9003), 0x77)

    def test_indirect_loads_load(self):
        base = self.CODE_ADDR
        # LD A, (BC) (0x0A)
        self.memory.write_byte(0x9100, 0xAA)
        self.cpu.b = 0x91
        self.cpu.c = 0x00
        self.memory.write_byte(base, 0x0A)
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0xAA)
        
        # LD A, (DE) (0x1A)
        self.memory.write_byte(0x9101, 0xBB)
        self.cpu.d = 0x91
        self.cpu.e = 0x01
        self.memory.write_byte(base + 1, 0x1A)
        self.cpu.pc = base + 1
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0xBB)
        
        # LD A, (nn) (0x3A)
        self.memory.write_byte(0x9102, 0xCC)
        self.memory.write_byte(base + 2, 0x3A)
        self.memory.write_word(base + 3, 0x9102)
        self.cpu.pc = base + 2
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0xCC)

    def test_alu_reg_add(self):
        base = self.CODE_ADDR
        # ADD A, B (0x80)
        self.cpu.a = 10
        self.cpu.b = 20
        self.memory.write_byte(base, 0x80)
        self.cpu.step()
        self.assertEqual(self.cpu.a, 30)
        
        # ADD A, (HL) (0x86)
        self.cpu.a = 10
        self.cpu.hl = 0x9200
        self.memory.write_byte(0x9200, 5)
        self.memory.write_byte(base + 1, 0x86)
        self.cpu.pc = base + 1
        self.cpu.step()
        self.assertEqual(self.cpu.a, 15)

    def test_alu_reg_sub(self):
        base = self.CODE_ADDR
        # SUB C (0x91)
        self.cpu.a = 50
        self.cpu.c = 20
        self.memory.write_byte(base, 0x91)
        self.cpu.step()
        self.assertEqual(self.cpu.a, 30)
        
    def test_alu_reg_and(self):
        base = self.CODE_ADDR
        # AND D (0xA2)
        self.cpu.a = 0xFF
        self.cpu.d = 0x0F
        self.memory.write_byte(base, 0xA2)
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0x0F)
        self.assertTrue(self.cpu.f & 0x10) # H=1
        
    def test_alu_reg_xor(self):
        base = self.CODE_ADDR
        # XOR E (0xAB)
        self.cpu.a = 0xAA
        self.cpu.e = 0x55
        self.memory.write_byte(base, 0xAB)
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0xFF)
        
    def test_alu_reg_or(self):
        base = self.CODE_ADDR
        # OR H (0xB4)
        self.cpu.a = 0xF0
        self.cpu.h = 0x0F
        self.memory.write_byte(base, 0xB4)
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0xFF)
        
    def test_alu_reg_cp(self):
        base = self.CODE_ADDR
        # CP L (0xBD)
        self.cpu.a = 20
        self.cpu.l = 20
        self.memory.write_byte(base, 0xBD)
        self.cpu.step()
        self.assertEqual(self.cpu.a, 20) # A unchanged
        self.assertTrue(self.cpu.f & 0x40) # Z=1

    def test_misc_ops(self):
        base = self.CODE_ADDR
        # SCF (0x37)
        self.memory.write_byte(base, 0x37)
        self.cpu.step()
        self.assertTrue(self.cpu.f & 0x01) # C=1
        
        # CCF (0x3F)
        self.memory.write_byte(base + 1, 0x3F)
        self.cpu.pc = base + 1
        self.cpu.step()
        self.assertFalse(self.cpu.f & 0x01) # C=0 (flipped)
        self.assertTrue(self.cpu.f & 0x10) # H = old C (1)
        
        # CPL (0x2F)
        self.cpu.a = 0xAA # 10101010
        self.memory.write_byte(base + 2, 0x2F)
        self.cpu.pc = base + 2
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0x55) # 01010101
        self.assertTrue(self.cpu.f & 0x12) # H=1, N=1
        
    def test_daa(self):
        base = self.CODE_ADDR
        # DAA (0x27)
        # ADD A, A -> 9 + 1 = 10 (0x0A) -> DAA -> 0x10 (BCD)
        self.cpu.a = 0x09
        self.cpu.b = 0x01
        self.memory.write_byte(base, 0x80) # ADD A, B -> A=10 (0x0A)
        self.memory.write_byte(base + 1, 0x27) # DAA
        self.cpu.step() # ADD
        self.assertEqual(self.cpu.a, 0x0A)
        self.cpu.step() # DAA
        self.assertEqual(self.cpu.a, 0x10) # 10 decimal in BCD

    def test_halt(self):
        base = self.CODE_ADDR
        # HALT (0x76)
        self.memory.write_byte(base, 0x00) # NOP
        self.memory.write_byte(base + 1, 0x76) # HALT
        self.memory.write_byte(base + 2, 0x00) # NOP
        
        self.cpu.pc = base + 1
        self.cpu.step()
        self.assertTrue(self.cpu.halted)
        self.assertEqual(self.cpu.pc, base + 2) # PC should point to next instruction
        
        self.cpu.step()
        self.assertEqual(self.cpu.pc, base + 2) # Still halted

    def test_ld_8bit_group(self):
        base = self.CODE_ADDR
        # LD B, C (0x41)
        self.cpu.c = 0x55
        self.memory.write_byte(base, 0x41)
        self.cpu.step()
        self.assertEqual(self.cpu.b, 0x55)

        # LD A, H (0x7C)
        self.cpu.h = 0xAA
        self.memory.write_byte(base + 1, 0x7C)
        self.cpu.pc = base + 1
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0xAA)
        
        # LD (HL), B (0x70)
        self.cpu.hl = 0x9500
        self.cpu.b = 0x99
        self.memory.write_byte(base + 2, 0x70)
        self.cpu.pc = base + 2
        self.cpu.step()
        self.assertEqual(self.memory.read_byte(0x9500), 0x99)
        
        # LD C, (HL) (0x4E)
        self.memory.write_byte(0x9501, 0x88)
        self.cpu.hl = 0x9501
        self.memory.write_byte(base + 3, 0x4E)
        self.cpu.pc = base + 3
        self.cpu.step()
        self.assertEqual(self.cpu.c, 0x88)
        
    def test_inc_dec_8bit(self):
        base = self.CODE_ADDR
        # INC B (0x04)
        self.cpu.b = 0x10
        self.memory.write_byte(base, 0x04)
        self.cpu.step()
        self.assertEqual(self.cpu.b, 0x11)
        
        # DEC B (0x05)
        self.memory.write_byte(base + 1, 0x05)
        self.cpu.pc = base + 1
        self.cpu.step()
        self.assertEqual(self.cpu.b, 0x10)
        
        # INC (HL) (0x34)
        self.cpu.hl = 0x9600
        self.memory.write_byte(0x9600, 0x20)
        self.memory.write_byte(base + 2, 0x34)
        self.cpu.pc = base + 2
        self.cpu.step()
        self.assertEqual(self.memory.read_byte(0x9600), 0x21)
        
        # Test Flag preservation (C is preserved)
        self.cpu.f = 0x01 # Set Carry
        self.cpu.a = 0xFF
        # INC A (0x3C) -> 0x00, Z=1, C should remain 1
        self.memory.write_byte(base + 3, 0x3C)
        self.cpu.pc = base + 3
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0x00)
        self.assertTrue(self.cpu.f & 0x40) # Z set
        self.assertTrue(self.cpu.f & 0x01) # C preserved

    def test_djnz(self):
        base = self.CODE_ADDR
        # DJNZ e (0x10)
        # Case 1: B != 1 (Jump)
        self.cpu.b = 0x02
        self.memory.write_byte(base, 0x10)
        self.memory.write_byte(base + 1, 0x05) # JR +5
        self.cpu.step()
        self.assertEqual(self.cpu.b, 0x01)
        self.assertEqual(self.cpu.pc, base + 2 + 5)
        
        # Case 2: B == 1 (No Jump)
        self.cpu.pc = base + 10 # Some address
        self.cpu.b = 0x01
        self.memory.write_byte(base + 10, 0x10)
        self.memory.write_byte(base + 11, 0xFE) # JR -2
        self.cpu.step()
        self.assertEqual(self.cpu.b, 0x00)
    def test_index_ix_iy(self):
        base = self.CODE_ADDR
        # LD IX, nn (DD 21 nn)
        self.memory.write_byte(base, 0xDD)
        self.memory.write_byte(base + 1, 0x21)
        self.memory.write_word(base + 2, 0x5000)
        self.cpu.step() # Executes prefix + LD
        self.assertEqual(self.cpu.ix, 0x5000)
        
        # LD IY, nn (FD 21 nn)
        self.memory.write_byte(base + 4, 0xFD)
        self.memory.write_byte(base + 5, 0x21)
        self.memory.write_word(base + 6, 0x6000)
        self.cpu.pc = base + 4
        self.cpu.step()
        self.assertEqual(self.cpu.iy, 0x6000)
        
        # ADD IX, BC (DD 09)
        self.cpu.bc = 0x1000
        self.memory.write_byte(base + 8, 0xDD)
        self.memory.write_byte(base + 9, 0x09)
        self.cpu.pc = base + 8
        self.cpu.step()
        self.assertEqual(self.cpu.ix, 0x6000) # 5000 + 1000

    def test_index_displacement(self):
        base = self.CODE_ADDR
        self.cpu.ix = 0x8000
        # LD (IX+d), n (DD 36 d n)
        # d = 5, n = 0xAA
        # Addr = 8005 -> 0xAA
        self.memory.write_byte(base, 0xDD)
        self.memory.write_byte(base + 1, 0x36)
        self.memory.write_byte(base + 2, 0x05) # d
        self.memory.write_byte(base + 3, 0xAA) # n
        
        self.cpu.step()
        self.assertEqual(self.memory.read_byte(0x8005), 0xAA)
        
        # LD B, (IX+d) (DD 46 d)
        # d = -2 (0xFE), Addr = 7FFE
        self.memory.write_byte(0x7FFE, 0xBB)
        self.memory.write_byte(base + 4, 0xDD)
        self.memory.write_byte(base + 5, 0x46)
        self.memory.write_byte(base + 6, 0xFE)
    def test_extended_ed(self):
        base = self.CODE_ADDR
        # LD (nn), BC (ED 43 nn)
        self.cpu.bc = 0x1234
        self.memory.write_byte(base, 0xED)
        self.memory.write_byte(base + 1, 0x43)
        self.memory.write_word(base + 2, 0x8000)
        self.cpu.step()
        self.assertEqual(self.memory.read_word(0x8000), 0x1234)
        
        # LD DE, (nn) (ED 5B nn)
        self.memory.write_word(0x8002, 0x5678)
        self.memory.write_byte(base + 4, 0xED)
        self.memory.write_byte(base + 5, 0x5B)
        self.memory.write_word(base + 6, 0x8002)
        self.cpu.pc = base + 4
        self.cpu.step()
        self.assertEqual(self.cpu.de, 0x5678)
        
        # NEG (ED 44) - Negate A
        self.cpu.a = 0x05
        self.memory.write_byte(base + 8, 0xED)
        self.memory.write_byte(base + 9, 0x44)
        self.cpu.pc = base + 8
        self.cpu.step()
        self.assertEqual(self.cpu.a, 0xFB) # -5 in 2's complement
        
        # IM 1 (ED 56)
        self.memory.write_byte(base + 10, 0xED)
        self.memory.write_byte(base + 11, 0x56)
        self.cpu.pc = base + 10
        self.cpu.step()
        self.assertEqual(self.cpu.im, 1)

        # LDI (ED A0) - Block Transfer
        # (DE) <- (HL), DE++, HL++, BC--
        self.cpu.hl = 0x9000
        self.cpu.de = 0x9100
        self.cpu.bc = 0x0001
        self.memory.write_byte(0x9000, 0xCC)
        self.memory.write_byte(base + 12, 0xED)
        self.memory.write_byte(base + 13, 0xA0)
        self.cpu.pc = base + 12
        self.cpu.step()
        
        self.assertEqual(self.memory.read_byte(0x9100), 0xCC)
        self.assertEqual(self.cpu.hl, 0x9001)
        self.assertEqual(self.cpu.de, 0x9101)
        self.assertEqual(self.cpu.bc, 0x0000)
        # P/V set to 0 because BC is 0? LDI specs: P/V=1 if BC!=0, 0 if BC==0
        self.assertFalse(self.cpu.f & 0x04) # P/V clear

