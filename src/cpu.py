class Z80:
    def __init__(self, memory, io_bus=None):
        self.memory = memory
        self.io_bus = io_bus
        self.ula = None
        
        # Main register set
        # Hlavní sada registrů
        self.a = 0
        self._f = 0
        self.b = 0
        self.c = 0
        self.d = 0
        self.e = 0
        self.h = 0
        self.l = 0
        
        # Alternate register set
        # Alternativní sada registrů
        self.a_alt = 0
        self._f_alt = 0
        self.b_alt = 0
        self.c_alt = 0
        self.d_alt = 0
        self.e_alt = 0
        self.h_alt = 0
        self.l_alt = 0
        
        # Index registers
        # Indexové registry
        self.ix = 0
        self.iy = 0
        
        # Special purpose registers
        # Speciální registry
        self.pc = 0
        self.sp = 0
        self.i = 0
        self.r = 0
        self.wz = 0 # Internal register MEMPTR
        
        # Flags
        # Příznaky
        self.iff1 = 0
        self.iff2 = 0
        self.im = 0
        self.halted = False
        self.cycles = 0
        self.tape = None
        self.q = 0 # Internal register for flag logic (ProcessorTests)
        self._flags_updated = False
        
        self.opcodes = [self._unimplemented_opcode] * 256
        self._init_opcodes()

    @property
    def f(self):
        return self._f

    @f.setter
    def f(self, value):
        self._f = value
        self._flags_updated = True

    @property
    def f_alt(self):
        return self._f_alt

    @f_alt.setter
    def f_alt(self, value):
        self._f_alt = value
        # Note: shadow flags update doesn't usually affect Q in the same way? 
        # But ProcessorTests might expect it. LD A, I affects flags and sets Q.
        # EX AF, AF' swaps them.
        pass

    def _init_opcodes(self):
        self.opcodes[0x00] = self._nop
        self.opcodes[0xF3] = self._di
        self.opcodes[0xFB] = self._ei
        
        # LD r, n (Immediate load) 8-bit
        # LD r, n (Přímé načtení) 8-bitový
        self.opcodes[0x3E] = lambda: self._ld_r_n('a')
        self.opcodes[0x06] = lambda: self._ld_r_n('b')
        self.opcodes[0x0E] = lambda: self._ld_r_n('c')
        self.opcodes[0x16] = lambda: self._ld_r_n('d')
        self.opcodes[0x1E] = lambda: self._ld_r_n('e')
        self.opcodes[0x26] = lambda: self._ld_r_n('h')
        self.opcodes[0x2E] = lambda: self._ld_r_n('l')

        # LD r, r' (Register to Register)
        # LD r, r' (Registr do registru)
        self.opcodes[0x78] = lambda: self._ld_r_r('a', 'b')
        self.opcodes[0x79] = lambda: self._ld_r_r('a', 'c')
        # ... (more LD instructions would go here)
        
        # 16-bit Load Instructions
        # 16bitové instrukce načítání

        # LD dd, nn
        # BC(01), DE(11), HL(21), SP(31)
        self.opcodes[0x01] = lambda: self._ld_dd_nn('bc')
        self.opcodes[0x11] = lambda: self._ld_dd_nn('de')
        self.opcodes[0x21] = lambda: self._ld_dd_nn('hl')
        self.opcodes[0x31] = lambda: self._ld_dd_nn('sp')

        # LD HL, (nn) (2A)
        self.opcodes[0x2A] = self._ld_hl_nn_indir
        # LD (nn), HL (22)
        self.opcodes[0x22] = lambda: self._ld_nn_indir_dd('hl')

        # LD SP, HL (F9)
        self.opcodes[0xF9] = self._ld_sp_hl
        
        # Arithmetic - ADD A, n
        # Aritmetika - ADD A, n
        self.opcodes[0xC6] = lambda: self._add_a_n(False)
        # Arithmetic - ADC A, n
        # Aritmetika - ADC A, n
        self.opcodes[0xCE] = lambda: self._add_a_n(True)
        # Arithmetic - SUB n
        # Aritmetika - SUB n
        self.opcodes[0xD6] = lambda: self._sub_a_n(False)
        # Arithmetic - SBC A, n
        # Aritmetika - SBC A, n
        self.opcodes[0xDE] = lambda: self._sub_a_n(True)
        
        # Logic - AND n
        # Logika - AND n
        self.opcodes[0xE6] = self._and_n
        # Logic - OR n
        # Logika - OR n
        self.opcodes[0xF6] = self._or_n
        # Logic - XOR n
        # Logika - XOR n
        self.opcodes[0xEE] = self._xor_n
        # Logic - CP n
        # Logika - CP n
        self.opcodes[0xFE] = self._cp_n
        
        # INC r
        # INC r (Inkrementace)
        self.opcodes[0x3C] = lambda: self._inc_r('a')
        # DEC r
        # DEC r (Dekrementace)
        self.opcodes[0x3D] = lambda: self._dec_r('a')

        # 16-bit Arithmetic - ADD HL, ss
        # 16bitová aritmetika - ADD HL, ss
        # ss: BC (0x09), DE (0x19), HL (0x29), SP (0x39)
        self.opcodes[0x09] = lambda: self._add_16('hl', 'bc')
        self.opcodes[0x19] = lambda: self._add_16('hl', 'de')
        self.opcodes[0x29] = lambda: self._add_16('hl', 'hl')
        self.opcodes[0x39] = lambda: self._add_16('hl', 'sp')

        # ... (rest of init_opcodes) ...

        # Index Prefixes
        # Indexové předpony
        self.opcodes[0xDD] = self._prefix_dd
        self.opcodes[0xFD] = self._prefix_fd
        
        # Indirect 8-bit Loads
        self.opcodes[0x02] = self._ld_bc_a
        self.opcodes[0x12] = self._ld_de_a
        self.opcodes[0x32] = self._ld_nn_a
        self.opcodes[0x0A] = self._ld_a_bc_indir
        self.opcodes[0x1A] = self._ld_a_de_indir
        self.opcodes[0x3A] = self._ld_a_nn_indir
        self.opcodes[0x36] = self._ld_hl_n
        
        # ALU Register Operations (0x80 - 0xBF)
        # 0x80 - 0x87: ADD A, r
        # 0x88 - 0x8F: ADC A, r
        # 0x90 - 0x97: SUB r
        # 0x98 - 0x9F: SBC A, r
        # 0xA0 - 0xA7: AND r
        # 0xA8 - 0xAF: XOR r
        # 0xB0 - 0xB7: OR r
        # 0xB8 - 0xBF: CP r
        
        regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl_indir', 'a']
        
        for i in range(8):
            r = regs[i]
            # Capture loop variable 'r' and 'i' with default args or helper
            # Python closures bind late, so use partial or default arg hack
            
            # ADD A, r
            self.opcodes[0x80 + i] = (lambda reg=r: self._alu_op(0, reg))
            # ADC A, r
            self.opcodes[0x88 + i] = (lambda reg=r: self._alu_op(1, reg))
            # SUB r
            self.opcodes[0x90 + i] = (lambda reg=r: self._alu_op(2, reg))
            # SBC A, r
            self.opcodes[0x98 + i] = (lambda reg=r: self._alu_op(3, reg))
            # AND r
            self.opcodes[0xA0 + i] = (lambda reg=r: self._alu_op(4, reg))
            # XOR r
            self.opcodes[0xA8 + i] = (lambda reg=r: self._alu_op(5, reg))
            # OR r
            self.opcodes[0xB0 + i] = (lambda reg=r: self._alu_op(6, reg))
            # CP r
            self.opcodes[0xB8 + i] = (lambda reg=r: self._alu_op(7, reg))

        # Misc Instructions
        self.opcodes[0x27] = self._daa  # DAA
        self.opcodes[0x2F] = self._cpl  # CPL
        self.opcodes[0x37] = self._scf  # SCF
        self.opcodes[0x3F] = self._ccf  # CCF
        self.opcodes[0x76] = self._halt # HALT
        
        # I/O Instructions
        # Vstupně-výstupní instrukce
        self.opcodes[0xDB] = self._in_a_n
        self.opcodes[0xD3] = self._out_n_a

        # ... (rest of init_opcodes continues below)


        # 16-bit INC ss
        # 16bitová INC ss
        # BC (0x03), DE (0x13), HL (0x23), SP (0x33)
        self.opcodes[0x03] = lambda: self._inc_ss('bc')
        self.opcodes[0x13] = lambda: self._inc_ss('de')
        self.opcodes[0x23] = lambda: self._inc_ss('hl')
        self.opcodes[0x33] = lambda: self._inc_ss('sp')

        # 16-bit DEC ss
        # 16bitová DEC ss
        # BC (0x0B), DE (0x1B), HL (0x2B), SP (0x3B)
        self.opcodes[0x0B] = lambda: self._dec_ss('bc')
        self.opcodes[0x1B] = lambda: self._dec_ss('de')
        self.opcodes[0x2B] = lambda: self._dec_ss('hl')
        self.opcodes[0x3B] = lambda: self._dec_ss('sp')
        
        # PUSH qq
        # PUSH qq (Uložení na zásobník)
        # BC (0xC5), DE (0xD5), HL (0xE5), AF (0xF5)
        self.opcodes[0xC5] = lambda: self._push_qq('bc')
        self.opcodes[0xD5] = lambda: self._push_qq('de')
        self.opcodes[0xE5] = lambda: self._push_qq('hl')
        self.opcodes[0xF5] = lambda: self._push_qq('af')
        
        # POP qq
        # POP qq (Výběr ze zásobníku)
        # BC (0xC1), DE (0xD1), HL (0xE1), AF (0xF1)
        self.opcodes[0xC1] = lambda: self._pop_qq('bc')
        self.opcodes[0xD1] = lambda: self._pop_qq('de')
        self.opcodes[0xE1] = lambda: self._pop_qq('hl')
        self.opcodes[0xF1] = lambda: self._pop_qq('af')

        # Accumulator Rotates
        self.opcodes[0x07] = self._rlca
        self.opcodes[0x0F] = self._rrca
        self.opcodes[0x17] = self._rla
        self.opcodes[0x1F] = self._rra
    # ... (existing opcodes) ...

        # Unconditional Jumps
        self.opcodes[0xC3] = lambda: self._jp_nn()       # JP nn
        self.opcodes[0xE9] = lambda: self._jp_hl()       # JP (HL)
        self.opcodes[0x18] = lambda: self._jr_e()        # JR e

        # Conditional Jumps - JP cc, nn
        # NZ(0xC2), Z(0xCA), NC(0xD2), C(0xDA), PO(0xE2), PE(0xEA), P(0xF2), M(0xFA)
        self.opcodes[0xC2] = lambda: self._jp_cc_nn('NZ')
        self.opcodes[0xCA] = lambda: self._jp_cc_nn('Z')
        self.opcodes[0xD2] = lambda: self._jp_cc_nn('NC')
        self.opcodes[0xDA] = lambda: self._jp_cc_nn('C')
        self.opcodes[0xE2] = lambda: self._jp_cc_nn('PO')
        self.opcodes[0xEA] = lambda: self._jp_cc_nn('PE')
        self.opcodes[0xF2] = lambda: self._jp_cc_nn('P')
        self.opcodes[0xFA] = lambda: self._jp_cc_nn('M')

        # Conditional Jumps - JR cc, e
        # NZ(0x20), Z(0x28), NC(0x30), C(0x38)
        self.opcodes[0x20] = lambda: self._jr_cc_e('NZ')
        self.opcodes[0x28] = lambda: self._jr_cc_e('Z')
        self.opcodes[0x30] = lambda: self._jr_cc_e('NC')
        self.opcodes[0x38] = lambda: self._jr_cc_e('C')

        # Calls and Returns
        self.opcodes[0xCD] = lambda: self._call_nn()     # CALL nn
        self.opcodes[0xC9] = lambda: self._ret()         # RET
        # Conditional RET - NZ(C0), Z(C8), NC(D0), C(D8), PO(E0), PE(E8), P(F0), M(F8)
        self.opcodes[0xC0] = lambda: self._ret_cc('NZ')
        self.opcodes[0xC8] = lambda: self._ret_cc('Z')
        self.opcodes[0xD0] = lambda: self._ret_cc('NC')
        self.opcodes[0xD8] = lambda: self._ret_cc('C')
        self.opcodes[0xE0] = lambda: self._ret_cc('PO')
        self.opcodes[0xE8] = lambda: self._ret_cc('PE')
        self.opcodes[0xF0] = lambda: self._ret_cc('P')
        self.opcodes[0xF8] = lambda: self._ret_cc('M')
        
        # Conditional CALL - NZ(C4), Z(CC), NC(D4), C(DC), PO(E4), PE(EC), P(F4), M(FC)
        self.opcodes[0xC4] = lambda: self._call_cc_nn('NZ')
        self.opcodes[0xCC] = lambda: self._call_cc_nn('Z')
        self.opcodes[0xD4] = lambda: self._call_cc_nn('NC')
        self.opcodes[0xDC] = lambda: self._call_cc_nn('C')
        self.opcodes[0xE4] = lambda: self._call_cc_nn('PO')
        self.opcodes[0xEC] = lambda: self._call_cc_nn('PE')
        self.opcodes[0xF4] = lambda: self._call_cc_nn('P')
        self.opcodes[0xFC] = lambda: self._call_cc_nn('M')

        # Restarts (RST)
        # 00(C7), 08(CF), 10(D7), 18(DF), 20(E7), 28(EF), 30(F7), 38(FF)
        self.opcodes[0xC7] = lambda: self._rst(0x00)
        self.opcodes[0xCF] = lambda: self._rst(0x08)
        self.opcodes[0xD7] = lambda: self._rst(0x10)
        self.opcodes[0xDF] = lambda: self._rst(0x18)
        self.opcodes[0xE7] = lambda: self._rst(0x20)
        self.opcodes[0xEF] = lambda: self._rst(0x28)
        self.opcodes[0xF7] = lambda: self._rst(0x30)
        self.opcodes[0xFF] = lambda: self._rst(0x38)

        # ... (calls and returns) ...
        
        # Exchange Instructions
        # Instrukce výměny (Exchange)
        
        # EX DE, HL (EB)
        self.opcodes[0xEB] = self._ex_de_hl
        
        # EX AF, AF' (08)
        self.opcodes[0x08] = self._ex_af_af_alt
        
        # EXX (D9) - Exchange BC, DE, HL with shadow registers
        # EXX (D9) - Výměna BC, DE, HL za stínové registry
        # EXX (D9) - Exchange BC, DE, HL with shadow registers
        # EXX (D9) - Výměna BC, DE, HL za stínové registry
        self.opcodes[0xD9] = self._exx
        
        # 8-bit Load Block (0x40 - 0x7F)
        # LD r, r'
        regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl_indir', 'a']
        for dest_i in range(8):
            for src_i in range(8):
                opcode = 0x40 + (dest_i << 3) + src_i
                if opcode == 0x76: continue # HALT exception
                
                dest = regs[dest_i]
                src = regs[src_i]
                self.opcodes[opcode] = (lambda d=dest, s=src: self._ld_r_r(d, s))
                
        # 8-bit Arithmetic (INC/DEC)
        for i in range(8):
            r = regs[i]
            # INC r (x0 xxx (dest) 100) -> 0x04, 0x0C ...
            # INC codes: 0x04, 0x0C, 0x14, 0x1C, 0x24, 0x2C, 0x34, 0x3C
            inc_opcode = 0x04 + (i << 3)
            self.opcodes[inc_opcode] = (lambda reg=r: self._inc_r(reg))
            
            # DEC r (x0 xxx (dest) 101) -> 0x05, 0x0D ...
            # DEC codes: 0x05, 0x0D, 0x15, 0x1D, 0x25, 0x2D, 0x35, 0x3D
            dec_opcode = 0x05 + (i << 3)
            self.opcodes[dec_opcode] = (lambda reg=r: self._dec_r(reg))
            
        # Control Flow
        self.opcodes[0x10] = self._djnz_e
        
        # EX (SP), HL (E3)
        self.opcodes[0xE3] = self._ex_sp_hl
        
        # Extended Instructions (ED prefix)
        # Rozšířené instrukce (předpona ED)
        self.opcodes[0xED] = self._prefix_ed
        
        # Bit Manipulation and Rotates (CB prefix)
        # Manipulace s bity a rotace (předpona CB)
        self.opcodes[0xCB] = self._prefix_cb

    def read_byte(self, addr):
        """
        Read a byte from memory with cycle penalty and contention.
        Přečte bajt z paměti s penalizací taktů a zohledněním kolizí.
        """
        if self.ula:
            self.cycles += self.ula.get_contention(self.cycles, addr)
        self.cycles += 3
        return self.memory.read_byte(addr)

    def write_byte(self, addr, val):
        """
        Write a byte to memory with cycle penalty and contention.
        Zapíše bajt do paměti s penalizací taktů a zohledněním kolizí.
        """
        if self.ula:
            self.cycles += self.ula.get_contention(self.cycles, addr)
        self.cycles += 3
        self.memory.write_byte(addr, val)

    def read_word(self, addr):
        """
        Read a word from memory with cycle penalty.
        """
        low = self.read_byte(addr)
        high = self.read_byte((addr + 1) & 0xFFFF)
        return (high << 8) | low

    def write_word(self, addr, val):
        """
        Write a word to memory with cycle penalty.
        """
        self.write_byte(addr, val & 0xFF)
        self.write_byte((addr + 1) & 0xFFFF, (val >> 8) & 0xFF)

    @property
    def hl_indir(self):
        return self.read_byte(self.hl)
        
    @hl_indir.setter
    def hl_indir(self, value):
        self.write_byte(self.hl, value)

    @property
    def hl_indir(self):
        return self.read_byte(self.hl)
        
    @hl_indir.setter
    def hl_indir(self, value):
        self.write_byte(self.hl, value)

    def _djnz_e(self):
        # DJNZ e (10 e)
        # B = B - 1
        # If B != 0, JR e
        offset = self._read_byte_pc_signed()
        
        self.b = (self.b - 1) & 0xFF
        if self.b != 0:
            target = (self.pc + offset) & 0xFFFF
            self.pc = target
            self.wz = target
            self.cycles += 13 # Jump taken
        else:
            self.cycles += 8 # Jump not taken
        


    # --- Exchange Helpers ---

    def _ex_de_hl(self):
        """
        Exchange DE and HL registers.
        Výměna registrů DE a HL.
        """
        self.de, self.hl = self.hl, self.de

    def _ex_af_af_alt(self):
        """
        Exchange AF and AF' registers.
        Výměna registrů AF a AF'.
        """
        self.a, self.a_alt = self.a_alt, self.a
        self.f, self.f_alt = self.f_alt, self.f

    def _exx(self):
        """
        Exchange BC, DE, HL with shadow registers.
        Výměna BC, DE, HL za stínové registry.
        """
        self.b, self.b_alt = self.b_alt, self.b
        self.c, self.c_alt = self.c_alt, self.c
        self.d, self.d_alt = self.d_alt, self.d
        self.e, self.e_alt = self.e_alt, self.e
        self.h, self.h_alt = self.h_alt, self.h
        self.l, self.l_alt = self.l_alt, self.l

    def _ex_sp_hl(self):
        """
        Exchange HL with value at (SP).
        Výměna HL s hodnotou na (SP).
        """
        val_sp = self._read_word_sp()
        
        # Write HL to Stack
        # Zápis HL na zásobník
        old_hl = self.hl
        self._write_word_sp(old_hl)
        
        # Set HL to old SP value
        # Nastavení HL na starou hodnotu SP
        self.hl = val_sp
        self.wz = self.hl

    def _read_word_sp(self):
        """
        Read 16-bit word from (SP) without popping.
        Přečte 16bitové slovo z (SP) bez výběru ze zásobníku.
        """
        low = self.read_byte(self.sp)
        high = self.read_byte((self.sp + 1) & 0xFFFF)
        return (high << 8) | low

    def _write_word_sp(self, val):
        """
        Write 16-bit word to (SP) without pushing.
        Zapíše 16bitové slovo na (SP) bez uložení na zásobník.
        """
        high = (val >> 8) & 0xFF
        low = val & 0xFF
        self.write_byte(self.sp, low)
        self.write_byte((self.sp + 1) & 0xFFFF, high)
    
    def _prefix_ed(self):
        """
        Handle extended instructions with ED prefix.
        Obsluha rozšířených instrukcí s předponou ED.
        """
        opcode = self._fetch_opcode()
        
        # Block Transfer
        # Blokové přenosy
        # Block Transfer
        # Blokové přenosy
        if opcode == 0xA0: self._ldi()
        elif opcode == 0xB0: self._ldir()
        elif opcode == 0xA8: self._ldd()
        elif opcode == 0xB8: self._lddr()
        
        # Block Compare
        # Blokové porovnání
        elif opcode == 0xA1: self._cpi()
        elif opcode == 0xB1: self._cpir()
        elif opcode == 0xA9: self._cpd()
        elif opcode == 0xB9: self._cpdr()
        
        # Extended Loads
        # Rozšířené načítání
        elif opcode == 0x4B: self._ld_dd_indir_nn('bc')
        elif opcode == 0x5B: self._ld_dd_indir_nn('de')
        elif opcode == 0x6B: self._ld_dd_indir_nn('hl')
        elif opcode == 0x7B: self._ld_dd_indir_nn('sp')
        elif opcode == 0x43: self._ld_nn_indir_dd('bc')
        elif opcode == 0x53: self._ld_nn_indir_dd('de')
        elif opcode == 0x63: self._ld_nn_indir_dd('hl')
        elif opcode == 0x73: self._ld_nn_indir_dd('sp')
        
        elif opcode == 0x57: self._ld_a_i()
        elif opcode == 0x47: self._ld_i_a()
        elif opcode == 0x5F: self._ld_a_r()
        elif opcode == 0x4F: self._ld_r_a()
        
        # Extended Arithmetic
        # Rozšířená aritmetika
        elif opcode == 0x4A: self._adc_hl_ss('bc')
        elif opcode == 0x5A: self._adc_hl_ss('de')
        elif opcode == 0x6A: self._adc_hl_ss('hl')
        elif opcode == 0x7A: self._adc_hl_ss('sp')
        elif opcode == 0x42: self._sbc_hl_ss('bc')
        elif opcode == 0x52: self._sbc_hl_ss('de')
        elif opcode == 0x62: self._sbc_hl_ss('hl')
        elif opcode == 0x72: self._sbc_hl_ss('sp')
        
        elif opcode in [0x44, 0x4C, 0x54, 0x5C, 0x64, 0x6C, 0x74, 0x7C]: 
            self._neg()
            
        # Interrupts
        # Přerušení
        elif opcode in [0x46, 0x4E, 0x66, 0x6E]: self._im(0)
        elif opcode in [0x56, 0x76]: self._im(1)
        elif opcode in [0x5E, 0x7E]: self._im(2)
        
        elif opcode == 0x4D: self._reti()
        elif opcode in [0x45, 0x55, 0x5D, 0x65, 0x6D, 0x75, 0x7D]: self._retn()
        
        # Digit Rotates
        # Rotace číslic
        elif opcode == 0x6F: self._rld()
        elif opcode == 0x67: self._rrd()
        
        # Extended I/O
        # Rozšířené V/V
        elif opcode == 0x40: self._in_r_c('b')
        elif opcode == 0x48: self._in_r_c('c')
        elif opcode == 0x50: self._in_r_c('d')
        elif opcode == 0x58: self._in_r_c('e')
        elif opcode == 0x60: self._in_r_c('h')
        elif opcode == 0x68: self._in_r_c('l')
        elif opcode == 0x78: self._in_r_c('a')
        elif opcode == 0x70: self._in_r_c('f') # Reads to flags/dummy? Documentation says '0' or flags. Usually reads to F or dummy.
        
        elif opcode == 0x41: self._out_c_r('b')
        elif opcode == 0x49: self._out_c_r('c')
        elif opcode == 0x51: self._out_c_r('d')
        elif opcode == 0x59: self._out_c_r('e')
        elif opcode == 0x61: self._out_c_r('h')
        elif opcode == 0x69: self._out_c_r('l')
        elif opcode == 0x79: self._out_c_r('a')
        elif opcode == 0x71: self._out_c_r('0')
        
        # Block I/O
        # Blokové V/V
        elif opcode == 0xA2: self._ini()
        elif opcode == 0xB2: self._inir()
        elif opcode == 0xAA: self._ind()
        elif opcode == 0xBA: self._indr()
        
        elif opcode == 0xA3: self._outi()
        elif opcode == 0xB3: self._otir()
        elif opcode == 0xAB: self._outd()
        elif opcode == 0xBB: self._otdr()
        
        else:
            print(f"Unimplemented ED opcode: {hex(opcode)}")

    # --- Block Transfer Helpers ---
    
    def _ldi(self):
        """
        LDI: Load (HL) to (DE), INC HL, INC DE, DEC BC.
        Načíst (HL) do (DE), INC HL, INC DE, DEC BC.
        """
        val = self.read_byte(self.hl)
        self.write_byte(self.de, val)
        
        n = (self.a + val) & 0xFF
        
        self.hl = (self.hl + 1) & 0xFFFF
        self.de = (self.de + 1) & 0xFFFF
        self.bc = (self.bc - 1) & 0xFFFF
        
        # Flags: H=0, N=0, P/V set if BC!=0. 5 and 3 from (A + (HL))
        f = self.f & 0b11000001 # Keep S, Z, C
        if self.bc != 0: f |= 0x04 # P/V
        if n & 0x02: f |= 0x20 # Bit 5 from (A + (HL)) bit 1
        if n & 0x08: f |= 0x08 # Bit 3 from (A + (HL)) bit 3
        
        self.f = f

    def _ldir(self):
        """
        LDIR: LDI repeated until BC=0.
        LDIR: LDI opakováno dokud BC=0.
        """
        self._ldi()
        if self.bc != 0:
            self.wz = (self.pc - 1) & 0xFFFF
            self.pc = (self.pc - 2) & 0xFFFF
            # Flags 5 and 3 are set from bits 13 and 11 of the instruction address (PC)
            self.f = (self.f & 0b11010111) | ((self.pc >> 8) & 0x28)
            self.cycles += 21
        else:
            self.cycles += 16

    def _ldd(self):
        """
        LDD: Load (HL) to (DE), DEC HL, DEC DE, DEC BC.
        Načíst (HL) do (DE), DEC HL, DEC DE, DEC BC.
        """
        val = self.read_byte(self.hl)
        self.write_byte(self.de, val)
        
        n = (self.a + val) & 0xFF
        
        self.hl = (self.hl - 1) & 0xFFFF
        self.de = (self.de - 1) & 0xFFFF
        self.bc = (self.bc - 1) & 0xFFFF
        
        # Flags: H=0, N=0, P/V set if BC!=0. 5 and 3 from (A + (HL))
        f = self.f & 0b11000001
        if self.bc != 0: f |= 0x04
        if n & 0x02: f |= 0x20
        if n & 0x08: f |= 0x08
        self.f = f

    def _lddr(self):
        """
        LDDR: LDD repeated until BC=0.
        LDDR: LDD opakováno dokud BC=0.
        """
        self._ldd()
        if self.bc != 0:
            self.wz = (self.pc - 1) & 0xFFFF
            self.pc = (self.pc - 2) & 0xFFFF
            self.f = (self.f & 0b11010111) | ((self.pc >> 8) & 0x28)
            self.cycles += 21
        else:
            self.cycles += 16

    # --- Block Compare Helpers ---

    def _cpi(self):
        """
        CPI: Compare A with (HL), INC HL, DEC BC.
        Porovnat A s (HL), INC HL, DEC BC.
        """
        val = self.read_byte(self.hl)
        res = (self.a - val) & 0xFF
        
        # Undocumented flags 5 and 3 logic for CPI
        # H is borrow from bit 4
        h = (self.a & 0x0F) < (val & 0x0F)
        
        # n for bits 5 and 3: if H was set, n = res - 1, else n = res
        n = (res - 1) & 0xFF if h else res
        
        self.hl = (self.hl + 1) & 0xFFFF
        self.bc = (self.bc - 1) & 0xFFFF
        
        f = self.f & 0x01 # Keep C
        if res & 0x80: f |= 0x80 # S
        if res == 0: f |= 0x40 # Z
        if h: f |= 0x10 # H
        if self.bc != 0: f |= 0x04 # P/V
        f |= 0x02 # N set
        
        # Undocumented bits 5 and 3
        if n & 0x02: f |= 0x20 # F5
        if n & 0x08: f |= 0x08 # F3
        
        self.f = f
        # CPI also updates WZ: WZ = WZ + 1? No.
        # Reference: CPI sets WZ = (initial WZ) + 1? No.
        # Actually: CPI sets WZ = WZ + 1. Correct.
        self.wz = (self.wz + 1) & 0xFFFF

    def _cpir(self):
        """
        CPIR: CPI repeated until BC=0 or Z=1.
        CPIR: CPI opakováno dokud BC=0 nebo Z=1.
        """
        self._cpi()
        if self.bc != 0 and not (self.f & 0x40): # If BC!=0 and Not Z
            self.wz = (self.pc - 1) & 0xFFFF
            self.pc = (self.pc - 2) & 0xFFFF
            self.f = (self.f & 0b11010111) | ((self.pc >> 8) & 0x28)
            self.cycles += 21
        else:
            self.cycles += 16

    def _cpd(self):
        """
        CPD: Compare A with (HL), DEC HL, DEC BC.
        Porovnat A s (HL), DEC HL, DEC BC.
        """
        val = self.read_byte(self.hl)
        res = (self.a - val) & 0xFF
        h = (self.a & 0x0F) < (val & 0x0F)
        n = (res - 1) & 0xFF if h else res
        
        self.hl = (self.hl - 1) & 0xFFFF
        self.bc = (self.bc - 1) & 0xFFFF
        
        f = self.f & 0x01
        if res & 0x80: f |= 0x80
        if res == 0: f |= 0x40
        if h: f |= 0x10
        if self.bc != 0: f |= 0x04
        f |= 0x02
        if n & 0x02: f |= 0x20
        if n & 0x08: f |= 0x08
        self.f = f
        
        self.wz = (self.wz - 1) & 0xFFFF

    def _cpdr(self):
        """
        CPDR: CPD repeated until BC=0 or Z=1.
        CPDR: CPD opakováno dokud BC=0 nebo Z=1.
        """
        self._cpd()
        if self.bc != 0 and not (self.f & 0x40):
            self.wz = (self.pc - 1) & 0xFFFF
            self.pc = (self.pc - 2) & 0xFFFF
            self.f = (self.f & 0b11010111) | ((self.pc >> 8) & 0x28)
            self.cycles += 21
        else:
            self.cycles += 16

    # ... step ...

    # --- Flow Control Helpers ---

    def _read_word_pc(self):
        """
        Read a 16-bit word from PC and increment PC by 2.
        Přečte 16bitové slovo z PC a zvýší PC o 2.
        """
        low = self.read_byte(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        high = self.read_byte(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return (high << 8) | low

    def _read_signed_byte_pc(self):
        """
        Read a signed byte from PC and increment PC.
        Přečte znaménkový bajt z PC a zvýší PC.
        """
        val = self.read_byte(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        if val > 127:
            val -= 256
        return val

    def _check_condition(self, cc):
        """
        Check if a condition is met based on flags.
        Zkontroluje, zda je splněna podmínka na základě příznaků.
        """
        # NZ (Non-Zero), Z (Zero), NC (No Carry), C (Carry)
        # PO (Parity Odd/No Overflow), PE (Parity Even/Overflow), P (Plus), M (Minus)
        flags = self.f
        if cc == 'NZ': return not (flags & 0x40)
        if cc == 'Z':  return (flags & 0x40)
        if cc == 'NC': return not (flags & 0x01)
        if cc == 'C':  return (flags & 0x01)
        if cc == 'PO': return not (flags & 0x04)
        if cc == 'PE': return (flags & 0x04)
        if cc == 'P':  return not (flags & 0x80)
        if cc == 'M':  return (flags & 0x80)
        return False

    # --- Flow Instructions ---

    def _jp_nn(self):
        """
        Jump to absolute address nn.
        Skok na absolutní adresu nn.
        """
        addr = self._read_word_pc()
        self.pc = addr
        self.wz = addr

    def _jp_hl(self):
        """
        Jump to address in HL.
        Skok na adresu v HL.
        """
        self.pc = self.hl

    def _jr_e(self):
        """
        Jump relative to PC + e.
        Skok relativně k PC + e.
        """
        offset = self._read_signed_byte_pc()
        # PC is already incremented in _read_signed_byte_pc (points to next instr)
        # Z80: JR e calculates from instruction start + 2.
        # But here self.pc has advanced past opcode by 1, and past operand by 1.
        # So self.pc is at next instruction.
        # New PC = PC_current + offset. Correct.
        target = (self.pc + offset) & 0xFFFF
        self.pc = target
        self.wz = target

    def _jp_cc_nn(self, cc):
        """
        Conditional Jump Absolute.
        Podmíněný skok absolutní.
        """
        addr = self._read_word_pc()
        if self._check_condition(cc):
            self.pc = addr
            self.wz = addr
        else:
            # Note: WZ is updated even if jump is NOT taken?
            # Actually for JP cc, nn, WZ = nn (the value read from instruction)
            self.wz = addr

    def _jr_cc_e(self, cc):
        """
        Conditional Jump Relative.
        Podmíněný skok relativní.
        """
        offset = self._read_signed_byte_pc()
        if self._check_condition(cc):
            target = (self.pc + offset) & 0xFFFF
            self.pc = target
            self.wz = target
        else:
            # JR cc, e does NOT update WZ if jump not taken?
            # Reference says: "WZ is only changed if jump is taken" for JR.
            pass

    def _call_nn(self):
        """
        Call subroutine at nn.
        Volání podprogramu na nn.
        """
        addr = self._read_word_pc()
        self._push_word(self.pc) # Push return address (next instruction)
        self.pc = addr
        self.wz = addr

    def _call_cc_nn(self, cc):
        """
        Conditional Call.
        Podmíněné volání.
        """
        addr = self._read_word_pc()
        if self._check_condition(cc):
            self._push_word(self.pc)
            self.pc = addr
            self.wz = addr
        else:
            self.wz = addr

    def _ret(self):
        """
        Return from subroutine.
        Návrat z podprogramu.
        """
        addr = self._pop_word()
        self.pc = addr
        self.wz = addr

    def _ret_cc(self, cc):
        """
        Conditional Return.
        Podmíněný návrat.
        """
        if self._check_condition(cc):
            addr = self._pop_word()
            self.pc = addr
            self.wz = addr

    def _rst(self, addr):
        """
        Restart at fixed address.
        Restart na pevné adrese.
        """
        self._push_word(self.pc)
        self.pc = addr
        self.wz = addr


    @property
    def bc(self): return (self.b << 8) | self.c
    @bc.setter
    def bc(self, val):
        self.b = (val >> 8) & 0xFF
        self.c = val & 0xFF

    @property
    def de(self): return (self.d << 8) | self.e
    @de.setter
    def de(self, val):
        self.d = (val >> 8) & 0xFF
        self.e = val & 0xFF

    @property
    def hl(self): return (self.h << 8) | self.l
    @hl.setter
    def hl(self, val):
        self.h = (val >> 8) & 0xFF
        self.l = val & 0xFF

    @property
    def ixh(self): return (self.ix >> 8) & 0xFF
    @ixh.setter
    def ixh(self, val):
        self.ix = (self.ix & 0x00FF) | ((val & 0xFF) << 8)

    @property
    def ixl(self): return self.ix & 0xFF
    @ixl.setter
    def ixl(self, val):
        self.ix = (self.ix & 0xFF00) | (val & 0xFF)

    @property
    def iyh(self): return (self.iy >> 8) & 0xFF
    @iyh.setter
    def iyh(self, val):
        self.iy = (self.iy & 0x00FF) | ((val & 0xFF) << 8)

    @property
    def iyl(self): return self.iy & 0xFF
    @iyl.setter
    def iyl(self, val):
        self.iy = (self.iy & 0xFF00) | (val & 0xFF)

    @property
    def af(self): return (self.a << 8) | self.f
    @af.setter
    def af(self, val):
        self.a = (val >> 8) & 0xFF
        self.f = val & 0xFF

    def interrupt(self):
        """
        Trigger an interrupt.
        Vyvolat přerušení.
        """
        if self.iff1:
            self.iff1 = 0 # Disable interrupts
            self.iff2 = 0
            self.halted = False # Resume from HALT
            
            # Push PC
            self.sp = (self.sp - 1) & 0xFFFF
            self.write_byte(self.sp, (self.pc >> 8) & 0xFF)
            self.sp = (self.sp - 1) & 0xFFFF
            self.write_byte(self.sp, self.pc & 0xFF)
            
            if self.im == 0 or self.im == 1:
                # Mode 1: RST 38h
                self.pc = 0x0038
                self.cycles += 13
            elif self.im == 2:
                # Mode 2: Indirect vector
                # Low byte from bus (assumed 0xFF for Spectrum open bus), High byte from I
                # Spodní byte ze sběrnice (předpokládáno 0xFF), Horní byte z I
                vector = (self.i << 8) | 0xFF 
                low = self.read_byte(vector)
                high = self.read_byte((vector + 1) & 0xFFFF)
                self.pc = (high << 8) | low
                self.cycles += 19

    def _fetch_opcode(self):
        """
        Fetch next opcode byte, increment PC and R register.
        Includes contention for M1 cycle.
        Načte další bajt opkódu, zvýší PC a registr R.
        Zahrnuje kolize (contention) pro cyklus M1.
        """
        if self.ula:
            self.cycles += self.ula.get_contention(self.cycles, self.pc)
        opcode = self.memory.read_byte(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        self.r = (self.r & 0x80) | ((self.r + 1) & 0x7F)
        self.cycles += 4 # M1 cycle: 4 T-states
        return opcode

    def step(self):
        if self.halted:
            self.cycles += 4
            return

        # Trap check for fast loading
        if self.pc == 0x0556: # LD-BYTES address
            if self.check_traps():
                return
                
        self._flags_updated = False
        opcode = self._fetch_opcode()
        self.opcodes[opcode]()
        
        # After instruction execution, update internal Q register for flag logic
        if self._flags_updated:
            self.q = self._f
        else:
            self.q = 0

    def check_traps(self):
        """
        Check and execute ROM traps.
        Zkontrolovat a provést ROM pasti.
        """
        if self.pc == 0x0556: # LD-BYTES
            # Only trap in 48K ROM (Bank 1) or if not 128K mode
            # Past pouze v 48K ROM (Banka 1) nebo pokud není 128K režim
            if not self.memory.is_128k or self.memory.current_rom_bank == 1:
                return self.tape_load_trap()
        return False

    def tape_load_trap(self):
        """
        Trap for ROM LD-BYTES routine (0x0556).
        Loads a block from the tape if available.
        Past pro ROM rutinu LD-BYTES (0x0556).
        Načte blok z pásky, pokud je k dispozici.
        """
        if self.tape is None:
            return False
            
        # Get next block
        block = self.tape.get_next_block()
        if not block:
            return False
            
        # Verify block type if needed (A register holds expected flag)
        # Expected flag in A (0x00 for header, 0xFF for data)
        expected_flag = self.a
        actual_flag = block[0]
        
        # Determine destination Address (IX) and Length (DE)
        dest = self.ix
        length = self.de
        
        # Block structure: Flag + Data + Checksum
        # We need to write Data to Memory[IX...IX+Length]
        # Verify checksum later? For now assume valid tape.
        
        if len(block) < 2: # Min: Flag + Checksum
            self.f &= ~1 # Reset Carry (Error)
            self._ret()
            return True
            
        # Data to write (exclude Flag and Checksum)
        # Wait, LD-BYTES loads Length bytes from tape.
        # But tape block usually matches requested length + 2.
        
        data_len = len(block) - 2 # Minus Flag and Checksum
        if data_len > length:
             data_len = length # Truncate if requested less?
        
        # Write data
        for i in range(data_len):
            val = block[i+1] # Skip Flag
            self.memory.write_byte((dest + i) & 0xFFFF, val)
            
        # Update registers as if routine succeeded
        # Success: Carry Flag Set
        self.f |= 0x01
        
        # RET from routine
        self._ret()
        
        print(f"Trap: Loaded block len={len(block)}, dest={hex(dest)}")
        return True

    def _prefix_cb(self):
        """
        Handle bit manipulation and rotate instructions with CB prefix.
        Obsluha instrukcí pro manipulaci s bity a rotace s předponou CB.
        """
        opcode = self._fetch_opcode()
        
        # Decode instruction
        # Dekódování instrukce
        # x = (opcode >> 6) & 3
        # y = (opcode >> 3) & 7
        # z = opcode & 7
        
        x = (opcode >> 6) & 3
        y = (opcode >> 3) & 7
        z = opcode & 7
        
        # Get operand
        # Získání operandu
        val = 0
        if z == 0: val = self.b
        elif z == 1: val = self.c
        elif z == 2: val = self.d
        elif z == 3: val = self.e
        elif z == 4: val = self.h
        elif z == 5: val = self.l
        elif z == 6: val = self.read_byte(self.hl)
        elif z == 7: val = self.a
        
        res = val
        
        # Execute operation
        # Provedení operace
        if x == 0: # Rotate/Shift
            if y == 0: res = self._rlc(val)
            elif y == 1: res = self._rrc(val)
            elif y == 2: res = self._rl(val)
            elif y == 3: res = self._rr(val)
            elif y == 4: res = self._sla(val)
            elif y == 5: res = self._sra(val)
            elif y == 6: 
                # SLL (undocumented) - functionally typically SLA or set bit 0
                # Z80 docs say SLL shifts left and sets bit 0.
                res = self._sll(val)
            elif y == 7: res = self._srl(val)
        elif x == 1: # BIT
            if z == 6: # (HL)
                self._bit(y, val, bits53_val=(self.wz >> 8) & 0xFF)
            else:
                self._bit(y, val)
            return # BIT doesn't write back
        elif x == 2: # RES
            res = self._res(y, val)
        elif x == 3: # SET
            res = self._set(y, val)
            
        # Write back result
        # Zápis výsledku zpět
        if z == 0: self.b = res
        elif z == 1: self.c = res
        elif z == 2: self.d = res
        elif z == 3: self.e = res
        elif z == 4: self.h = res
        elif z == 5: self.l = res
        elif z == 6: self.write_byte(self.hl, res)
        elif z == 7: self.a = res

    # --- Bit Manipulation Helpers ---

    def _rlc(self, val):
        # Rotate Left Circular
        bit7 = (val >> 7) & 1
        res = ((val << 1) | bit7) & 0xFF
        
        f = 0
        if res & 0x80: f |= 0x80
        if res == 0: f |= 0x40
        if (res & 0x20): f |= 0x20
        if (res & 0x08): f |= 0x08
        if self._parity(res): f |= 0x04
        if bit7: f |= 0x01
        
        self.f = f
        return res

    def _rrc(self, val):
        # Rotate Right Circular
        bit0 = val & 1
        res = ((val >> 1) | (bit0 << 7)) & 0xFF
        
        f = 0
        if res & 0x80: f |= 0x80
        if res == 0: f |= 0x40
        if (res & 0x20): f |= 0x20
        if (res & 0x08): f |= 0x08
        if self._parity(res): f |= 0x04
        if bit0: f |= 0x01
        self.f = f
        return res

    def _rl(self, val):
        # Rotate Left through Carry
        old_c = self.f & 1
        bit7 = (val >> 7) & 1
        res = ((val << 1) | old_c) & 0xFF
        
        f = 0
        if res & 0x80: f |= 0x80
        if res == 0: f |= 0x40
        if (res & 0x20): f |= 0x20
        if (res & 0x08): f |= 0x08
        if self._parity(res): f |= 0x04
        if bit7: f |= 0x01
        self.f = f
        return res

    def _rr(self, val):
        # Rotate Right through Carry
        old_c = self.f & 1
        bit0 = val & 1
        res = ((val >> 1) | (old_c << 7)) & 0xFF
        
        f = 0
        if res & 0x80: f |= 0x80
        if res == 0: f |= 0x40
        if (res & 0x20): f |= 0x20
        if (res & 0x08): f |= 0x08
        if self._parity(res): f |= 0x04
        if bit0: f |= 0x01
        self.f = f
        return res

    def _sla(self, val):
        # Shift Left Arithmetic
        bit7 = (val >> 7) & 1
        res = (val << 1) & 0xFF
        
        f = 0
        if res & 0x80: f |= 0x80
        if res == 0: f |= 0x40
        if (res & 0x20): f |= 0x20
        if (res & 0x08): f |= 0x08
        if self._parity(res): f |= 0x04
        if bit7: f |= 0x01
        self.f = f
        return res

    def _sra(self, val):
        # Shift Right Arithmetic
        bit0 = val & 1
        bit7 = val & 0x80
        res = ((val >> 1) | bit7) & 0xFF
        
        f = 0
        if res & 0x80: f |= 0x80
        if res == 0: f |= 0x40
        if (res & 0x20): f |= 0x20
        if (res & 0x08): f |= 0x08
        if self._parity(res): f |= 0x04
        if bit0: f |= 0x01
        self.f = f
        return res
        
    def _sll(self, val):
        # Shift Left Logical (undocumented SLL)
        bit7 = (val >> 7) & 1
        res = ((val << 1) | 1) & 0xFF
        
        f = 0
        if res & 0x80: f |= 0x80
        if res == 0: f |= 0x40
        if (res & 0x20): f |= 0x20
        if (res & 0x08): f |= 0x08
        if self._parity(res): f |= 0x04
        if bit7: f |= 0x01
        self.f = f
        return res

    def _srl(self, val):
        # Shift Right Logical
        bit0 = val & 1
        res = (val >> 1) & 0xFF
        
        f = 0
        if res & 0x80: f |= 0x80
        if res == 0: f |= 0x40
        if (res & 0x20): f |= 0x20
        if (res & 0x08): f |= 0x08
        if self._parity(res): f |= 0x04
        if bit0: f |= 0x01
        self.f = f
        return res

    def _bit(self, bit, val, bits53_val=None):
        # Test Bit
        is_zero = not ((val >> bit) & 1)
        
        if bits53_val is None:
            bits53_val = val
            
        f = self.f & 0b00000001 # Keep C
        if is_zero: f |= 0x40
        f |= 0x10 # H set
        # Bits 5 and 3 are copied from bits53_val
        if (bits53_val & 0x20): f |= 0x20
        if (bits53_val & 0x08): f |= 0x08
        
        # S is set if bit 7 is tested and set
        if bit == 7 and not is_zero: f |= 0x80
        
        # P/V matches Z for BIT
        if is_zero: f |= 0x04
        
        self.f = f

    def _set(self, bit, val):
        res = val | (1 << bit)
        return res

    def _res(self, bit, val):
        res = val & ~(1 << bit)
        return res
        
    def _parity(self, val):
        return bin(val).count('1') % 2 == 0

    def _unimplemented_opcode(self):
        opcode = self.read_byte((self.pc - 1) & 0xFFFF)
        print(f"Unknown opcode 0x{opcode:02X} at 0x{self.pc-1:04X}")

    def _nop(self):
        pass

    def _di(self):
        self.iff1 = 0
        self.iff2 = 0

    def _ei(self):
        self.iff1 = 1
        self.iff2 = 1

    def _ld_r_n(self, r):
        val = self.read_byte(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        setattr(self, r, val)

    def _ld_r_r(self, dest, src):
        val = getattr(self, src)
        setattr(self, dest, val)

    # --- ALU Helpers ---

    def _update_flags_add(self, op1, op2, res, carry_in):
        res8 = res & 0xFF
        # S (Sign)
        s = (res8 & 0x80) != 0
        # Z (Zero)
        z = (res8 == 0)
        # H (Half Carry)
        h = ((op1 & 0x0F) + (op2 & 0x0F) + carry_in) > 0x0F
        # P/V (Overflow)
        op1_s = (op1 & 0x80) != 0
        op2_s = (op2 & 0x80) != 0
        res_s = s
        v = (op1_s == op2_s) and (res_s != op1_s)
        # N (Add/Sub)
        n = False
        # C (Carry)
        c = res > 0xFF

        f = 0
        if s: f |= 0x80
        if z: f |= 0x40
        if (res8 & 0x20): f |= 0x20 # Bit 5
        if h: f |= 0x10
        if (res8 & 0x08): f |= 0x08 # Bit 3
        if v: f |= 0x04
        if n: f |= 0x02
        if c: f |= 0x01
        self.f = f

    def _update_flags_sub(self, op1, op2, res, carry_in):
        res8 = res & 0xFF
        # S
        s = (res8 & 0x80) != 0
        # Z
        z = (res8 == 0)
        # H (Half Carry)
        h = ((op1 & 0x0F) - (op2 & 0x0F) - carry_in) < 0
        # P/V (Overflow)
        op1_s = (op1 & 0x80) != 0
        op2_s = (op2 & 0x80) != 0
        res_s = s
        v = (op1_s != op2_s) and (res_s != op1_s)
        # N
        n = True
        # C (Carry/Borrow)
        c = res < 0

        f = 0
        if s: f |= 0x80
        if z: f |= 0x40
        if (res8 & 0x20): f |= 0x20 # Bit 5
        if h: f |= 0x10
        if (res8 & 0x08): f |= 0x08 # Bit 3
        if v: f |= 0x04
        if n: f |= 0x02
        if c: f |= 0x01
        self.f = f

    def _update_flags_logic(self, res, is_and):
        s = (res & 0x80) != 0
        z = ((res & 0xFF) == 0)
        h = True if is_and else False
        p = bin(res & 0xFF).count('1') % 2 == 0
        
        f = 0
        if s: f |= 0x80
        if z: f |= 0x40
        if (res & 0x20): f |= 0x20 # Bit 5
        if h: f |= 0x10
        if (res & 0x08): f |= 0x08 # Bit 3
        if p: f |= 0x04
        # N, C are 0
        self.f = f

    # --- ALU Register/Value Engine ---
    
    def _alu_op(self, op_index, reg_name, is_val=False):
        """
        Generic ALU operation for registers (including (HL)).
        op_index: 0=ADD, 1=ADC, 2=SUB, 3=SBC, 4=AND, 5=XOR, 6=OR, 7=CP
        """
        val = 0
        if is_val:
            val = reg_name # reg_name is actually the value
        elif reg_name == 'hl_indir':
            val = self.read_byte(self.hl)
        else:
            val = getattr(self, reg_name)
        
        if op_index == 0: self._add_val(val, False)   # ADD A, r
        elif op_index == 1: self._add_val(val, True)  # ADC A, r
        elif op_index == 2: self._sub_val(val, False) # SUB r
        elif op_index == 3: self._sub_val(val, True)  # SBC A, r
        elif op_index == 4: self._and_val(val)        # AND r
        elif op_index == 5: self._xor_val(val)        # XOR r
        elif op_index == 6: self._or_val(val)         # OR r
        elif op_index == 7: self._cp_val(val)         # CP r

    def _ld_nn_indir_dd(self, dd):
        """
        LD (nn), dd (dd=BC, DE, HL, SP, IX, IY)
        """
        addr = self._read_word_pc()
        val = getattr(self, dd)
        low = val & 0xFF
        high = (val >> 8) & 0xFF
        self.write_byte(addr, low)
        self.write_byte((addr + 1) & 0xFFFF, high)
        self.wz = (addr + 1) & 0xFFFF

    # --- Misc Instructions ---
    
    def _daa(self):
        """
        Decimal Adjust Accumulator.
        Accurately adjusts A for BCD arithmetic and updates flags.
        """
        correction = 0
        carry = self.f & 0x01
        half_carry = self.f & 0x10
        n = self.f & 0x02
        
        if half_carry or (self.a & 0x0F) > 9:
            correction |= 0x06
            
        if carry or self.a > 0x99:
            correction |= 0x60
            carry = 1
        else:
            carry = 0
            
        if n:
            # H logic for subtraction
            new_h = 1 if (half_carry and (self.a & 0x0F) < 6) else 0
            self.a = (self.a - correction) & 0xFF
        else:
            # H logic for addition
            new_h = 1 if (self.a & 0x0F) > 9 else 0
            self.a = (self.a + correction) & 0xFF
            
        # Update Flags
        f = 0
        if self.a & 0x80: f |= 0x80 # S
        if self.a == 0: f |= 0x40    # Z
        if self.a & 0x20: f |= 0x20 # 5
        if new_h: f |= 0x10         # H
        if self.a & 0x08: f |= 0x08 # 3
        if self._parity(self.a): f |= 0x04 # P/V
        if n: f |= 0x02             # N
        if carry: f |= 0x01         # C
        
        self.f = f

    def _cpl(self):
        self.a = (~self.a) & 0xFF
        # Flags: H=1, N=1. Others preserved. 5 and 3 from A.
        self.f |= 0x12 # Set H and N
        self.f = (self.f & 0xD7) | (self.a & 0x28)
        
    def _scf(self):
        # C=1, H=0, N=0. 5 and 3 from ((Q ^ F) | A)
        new_f = (self.f & 0xC4) | (((self.q ^ self.f) | self.a) & 0x28) | 0x01
        self.f = new_f
        
    def _ccf(self):
        # H = old C, N = 0, C = not old C. 5 and 3 from ((Q ^ F) | A)
        old_c = self.f & 0x01
        new_f = (self.f & 0xC4) | (((self.q ^ self.f) | self.a) & 0x28) | (old_c << 4) | (1 - old_c)
        self.f = new_f
        
    def _halt(self):
        self.halted = True
        # CPU stops executing instructions until interrupt.
        # Note: In single-step tests, PC should point to the next instruction.

    # --- Accumulator Rotates ---

    def _rlca(self):
        # Rotate Accumulator Left Circular
        # Rotace akumulátoru vlevo kruhová
        # bit 7 -> C, bit 7 -> bit 0
        bit7 = (self.a >> 7) & 1
        self.a = ((self.a << 1) | bit7) & 0xFF
        # Flags: C=bit7, H=0, N=0. Others preserved. 5 and 3 from result.
        self.f = (self.f & 0xC4) | (self.a & 0x28) | bit7

    def _rrca(self):
        # Rotate Accumulator Right Circular
        # Rotace akumulátoru vpravo kruhová
        # bit 0 -> C, bit 0 -> bit 7
        bit0 = self.a & 1
        self.a = ((self.a >> 1) | (bit0 << 7)) & 0xFF
        # Flags: C=bit0, H=0, N=0. Others preserved. 5 and 3 from result.
        self.f = (self.f & 0xC4) | (self.a & 0x28) | bit0

    def _rla(self):
        # Rotate Accumulator Left through Carry
        # Rotace akumulátoru vlevo přes Carry
        # bit 7 -> C, C -> bit 0
        old_c = self.f & 1
        bit7 = (self.a >> 7) & 1
        self.a = ((self.a << 1) | old_c) & 0xFF
        # Flags: C=bit7, H=0, N=0. Others preserved. 5 and 3 from result.
        self.f = (self.f & 0xC4) | (self.a & 0x28) | bit7

    def _rra(self):
        # Rotate Accumulator Right through Carry
        # Rotace akumulátoru vpravo přes Carry
        # bit 0 -> C, C -> bit 7
        old_c = self.f & 1
        bit0 = self.a & 1
        self.a = ((self.a >> 1) | (old_c << 7)) & 0xFF
        # Flags: C=bit0, H=0, N=0. Others preserved. 5 and 3 from result.
        self.f = (self.f & 0xC4) | (self.a & 0x28) | bit0

    # --- ALU Helpers ---

    def _add_val(self, val, use_carry):
        carry = 1 if (use_carry and (self.f & 0x01)) else 0
        res_full = self.a + val + carry
        res = res_full & 0xFF
        self._update_flags_add(self.a, val, res_full, carry)
        self.a = res

    def _sub_val(self, val, use_carry):
        carry = 1 if (use_carry and (self.f & 0x01)) else 0
        res_full = self.a - val - carry
        res = res_full & 0xFF
        self._update_flags_sub(self.a, val, res_full, carry)
        self.a = res

    def _and_val(self, val):
        self.a &= val
        # Flags: S, Z, H=1, P/V, N=0, C=0
        self._update_flags_logic(self.a, is_and=True)

    def _or_val(self, val):
        self.a |= val
        # Flags: S, Z, H=0, P/V, N=0, C=0
        self._update_flags_logic(self.a, is_and=False)

    def _xor_val(self, val):
        self.a ^= val
        # Flags: S, Z, H=0, P/V, N=0, C=0
        self._update_flags_logic(self.a, is_and=False)

    def _cp_val(self, val):
        # CP is SUB but discard result
        res_full = self.a - val
        # Verify flags update for CP
        self._update_flags_sub(self.a, val, res_full, 0)
        # Undocumented: CP bits 5 and 3 are from the OPERAND
        self.f = (self.f & 0b11010111) | (val & 0x28)
        
    # --- ALU Instructions (Wrapped) ---

    def _add_a_n(self, use_carry):
        val = self._read_byte_pc()
        self._add_val(val, use_carry)

    def _sub_a_n(self, use_carry):
        val = self._read_byte_pc()
        self._sub_val(val, use_carry)

    def _and_n(self):
        val = self._read_byte_pc()
        self._and_val(val)

    def _or_n(self):
        val = self._read_byte_pc()
        self._or_val(val)

    def _xor_n(self):
        val = self._read_byte_pc()
        self._xor_val(val)

    def _cp_n(self):
        val = self._read_byte_pc()
        self._cp_val(val)
        
    # --- Indirect Loads ---
    
    def _ld_bc_a(self): # 0x02 LD (BC), A
        self.write_byte(self.bc, self.a)
        self.wz = (self.a << 8) | ((self.bc + 1) & 0xFF)
        
    def _ld_de_a(self): # 0x12 LD (DE), A
        self.write_byte(self.de, self.a)
        self.wz = (self.a << 8) | ((self.de + 1) & 0xFF)
        
    def _ld_nn_a(self): # 0x32 LD (nn), A
        addr = self._read_word_pc()
        self.write_byte(addr, self.a)
        self.wz = (self.a << 8) | ((addr + 1) & 0xFF)
        
    def _ld_a_bc_indir(self): # 0x0A LD A, (BC)
        self.a = self.read_byte(self.bc)
        self.wz = (self.bc + 1) & 0xFFFF
        
    def _ld_a_de_indir(self): # 0x1A LD A, (DE)
        self.a = self.read_byte(self.de)
        self.wz = (self.de + 1) & 0xFFFF
        
    def _ld_a_nn_indir(self): # 0x3A LD A, (nn)
        addr = self._read_word_pc()
        self.a = self.read_byte(addr)
        self.wz = (addr + 1) & 0xFFFF
        
    def _ld_hl_n(self): # 0x36 LD (HL), n
        val = self._read_byte_pc()
        self.write_byte(self.hl, val)

    def _inc_r(self, r):
        val = getattr(self, r)
        res = (val + 1) & 0xFF
        
        # INC affects flags S, Z, H, P/V, N. Does NOT affect C.
        # INC ovlivňuje příznaky S, Z, H, P/V, N. NEOVLIVŇUJE C.
        # Preserve C
        # Zachovat C
        c_flag = self.f & 0x01
        
        self._update_flags_add(val, 1, res, 0)
        
        # Restore C since ADD updates it logicallly differently for INC
        # Obnovit C, protože ADD jej logicky aktualizuje jinak pro INC
        # Actually INC doesn't set C, so we overwrite whatever _update_flags_add did to bit 0
        # Ve skutečnosti INC nenastavuje C, takže přepíšeme cokoliv, co _update_flags_add udělal s bitem 0
        self.f = (self.f & 0xFE) | c_flag
        
        setattr(self, r, res)

    def _dec_r(self, r):
        val = getattr(self, r)
        res = (val - 1) & 0xFF
        
        c_flag = self.f & 0x01
        self._update_flags_sub(val, 1, res, 0) # res here might be negative if we don't mask?
                                               # res zde může být záporné, pokud nepoužijeme masku?
                                               # _update_flags_sub expects raw res_full for carry check
                                               # _update_flags_sub očekává hrubé res_full pro kontrolu přenosu
                                               # but here we know op2 is 1.
                                               # ale zde víme, že op2 je 1.
                                               # Let's pass (val-1) as res_full
                                               # Předáme (val-1) jako res_full
        
        self.f = (self.f & 0xFE) | c_flag
        setattr(self, r, res)

    # --- 16-bit ALU Helpers ---

    def _add_hl_ss(self, ss):
        val = getattr(self, ss)
        res_full = self.hl + val
        res = res_full & 0xFFFF
        
        # Flags: N reset. H set if carry from bit 11. C set if carry from bit 15.
        # Příznaky: N reset. H nastaveno, pokud přenos z bitu 11. C nastaveno, pokud přenos z bitu 15.
        # S, Z, P/V not affected.
        # S, Z, P/V neovlivněny.
        
        # H carry check: (HL & 0xFFF) + (val & 0xFFF) > 0xFFF
        # Kontrola přenosu H: (HL & 0xFFF) + (val & 0xFFF) > 0xFFF
        h = ((self.hl & 0x0FFF) + (val & 0x0FFF)) > 0x0FFF
        c = res_full > 0xFFFF
        n = False
        
        # Preserve S, Z, P/V
        # Zachovat S, Z, P/V
        current_f = self.f
        new_f = (current_f & 0b11101000) # Keep S(7), Z(6), P/V(2). Clear others? No, 5 and 3 might change
                                         # Zachovat S(7), Z(6), P/V(2). Vymazat ostatní? Ne, 5 a 3 se mohou změnit
                                         # Typically 5 and 3 come from high byte of result
                                         # Typicky 5 a 3 pocházejí z horního bajtu výsledku
        
        # For simplicity, we just manipulate H, N, C
        # Pro jednoduchost manipulujeme pouze s H, N, C
        mask = 0b11101000 # bits we keep from old F
        
        f = (self.f & mask)
        if h: f |= 0x10
        if n: f |= 0x02
        if c: f |= 0x01
        
        self.f = f
        self.hl = res

    def _inc_ss(self, ss):
        val = getattr(self, ss)
        res = (val + 1) & 0xFFFF
        setattr(self, ss, res)
        # No flags affected
        # Žádné příznaky neovlivněny

    def _dec_ss(self, ss):
        val = getattr(self, ss)
        res = (val - 1) & 0xFFFF
        setattr(self, ss, res)
        # No flags affected
        # Žádné příznaky neovlivněny

    # --- Stack Helpers ---

    def _push_word(self, val):
        high = (val >> 8) & 0xFF
        low = val & 0xFF
        
        self.sp = (self.sp - 1) & 0xFFFF
        self.write_byte(self.sp, high)
        self.sp = (self.sp - 1) & 0xFFFF
        self.write_byte(self.sp, low)

    def _pop_word(self):
        low = self.read_byte(self.sp)
        self.sp = (self.sp + 1) & 0xFFFF
        high = self.read_byte(self.sp)
        self.sp = (self.sp + 1) & 0xFFFF
        return (high << 8) | low

    def _push_qq(self, qq):
        val = getattr(self, qq)
        self._push_word(val)

    def _pop_qq(self, qq):
        val = self._pop_word()
        setattr(self, qq, val)

    # --- 16-bit Load Helpers ---

    def _ld_dd_nn(self, dd):
        """
        Load 16-bit immediate value nn into register pair dd.
        Načte 16bitovou přímou hodnotu nn do registrového páru dd.
        """
        val = self._read_word_pc()
        setattr(self, dd, val)

    def _ld_hl_nn_indir(self):
        """
        Load HL from address (nn).
        Načte HL z adresy (nn).
        """
        addr = self._read_word_pc()
        low = self.read_byte(addr)
        high = self.read_byte((addr + 1) & 0xFFFF)
        self.hl = (high << 8) | low
        self.wz = (addr + 1) & 0xFFFF

    def _ld_nn_indir_hl(self):
        """
        Store HL to address (nn).
        Uloží HL na adresu (nn).
        """
        addr = self._read_word_pc()
        low = self.l
        high = self.h
        self.write_byte(addr, low)
        self.write_byte((addr + 1) & 0xFFFF, high)
        self.wz = (addr + 1) & 0xFFFF

    def _ld_sp_hl(self):
        """
        Load SP from HL.
        Načte SP z HL.
        """
        self.sp = self.hl

    # --- Extended Instructions (ED) Helpers ---

    def _adc_hl_ss(self, ss):
        val = getattr(self, ss)
        carry_in = 1 if (self.f & 0x01) else 0
        
        initial_hl = self.hl
        res_full = self.hl + val + carry_in
        res = res_full & 0xFFFF
        
        # Flags: S, Z, P/V, C, N=0, H
        s = (res & 0x8000) != 0
        z = (res == 0)
        # H: Set if carry from bit 11
        h = ((self.hl & 0x0FFF) + (val & 0x0FFF) + carry_in) > 0x0FFF
        # P/V: Set if overflow
        op1_s = (self.hl & 0x8000) != 0
        op2_s = (val & 0x8000) != 0
        res_s = s
        v = (op1_s == op2_s) and (res_s != op1_s)
        # N: Reset
        n = False
        # C: Set if carry from bit 15
        c = res_full > 0xFFFF
        
        f = 0
        if s: f |= 0x80
        if z: f |= 0x40
        if (res >> 8) & 0x20: f |= 0x20
        if h: f |= 0x10
        if (res >> 8) & 0x08: f |= 0x08
        if v: f |= 0x04
        if n: f |= 0x02
        if c: f |= 0x01
        
        self.f = f
        self.hl = res
        self.wz = (initial_hl + 1) & 0xFFFF

    def _sbc_hl_ss(self, ss):
        val = getattr(self, ss)
        carry_in = 1 if (self.f & 0x01) else 0
        
        initial_hl = self.hl
        res_full = self.hl - val - carry_in
        res = res_full & 0xFFFF
        
        # Flags: S, Z, P/V, C, N=1, H
        s = (res & 0x8000) != 0
        z = (res == 0)
        
        # H: Borrow from bit 12 (bit 11 check?)
        # 16-bit half carry/borrow is from bit 11 to 12
        h = ((self.hl & 0x0FFF) - (val & 0x0FFF) - carry_in) < 0
        
        # P/V: Overflow
        op1_s = (self.hl & 0x8000) != 0
        op2_s = (val & 0x8000) != 0
        res_s = s
        v = (op1_s != op2_s) and (res_s != op1_s)
        
        n = True
        c = res_full < 0
        
        f = 0
        if s: f |= 0x80
        if z: f |= 0x40
        if (res >> 8) & 0x20: f |= 0x20 # Bit 5 from high byte of result
        if h: f |= 0x10
        if (res >> 8) & 0x08: f |= 0x08 # Bit 3 from high byte of result
        if v: f |= 0x04
        if n: f |= 0x02
        if c: f |= 0x01
        
        self.f = f
        self.hl = res
        self.wz = (initial_hl + 1) & 0xFFFF

    def _neg(self):
        # A = 0 - A
        # S, Z, H, P/V, N=1, C
        val = self.a
        res_full = 0 - val
        res = res_full & 0xFF
        
        self._update_flags_sub(0, val, res_full, 0)
        self.a = res

    def _im(self, mode):
        self.im = mode

    def _ld_a_i(self):
        self.a = self.i
        # Flags: S, Z from I. H=0, N=0. P/V = IFF2. 5, 3 from I.
        f = self.f & 0b00000001 # Keep C
        if self.a & 0x80: f |= 0x80
        if self.a == 0: f |= 0x40
        if self.a & 0x20: f |= 0x20
        if self.a & 0x08: f |= 0x08
        if self.iff2: f |= 0x04
        self.f = f

    def _ld_a_r(self):
        self.a = self.r
        # Flags: S, Z from R. H=0, N=0. P/V = IFF2. 5, 3 from R.
        f = self.f & 0b00000001 # Keep C
        if self.a & 0x80: f |= 0x80
        if self.a == 0: f |= 0x40
        if self.a & 0x20: f |= 0x20
        if self.a & 0x08: f |= 0x08
        if self.iff2: f |= 0x04
        self.f = f

    def _ld_i_a(self):
        self.i = self.a

    def _ld_r_a(self):
        self.r = self.a

    def _rld(self):
        # (HL) low -> (HL) high
        # (HL) high -> A low
        # A low -> (HL) low
        
        hl_val = self.read_byte(self.hl)
        hl_low = hl_val & 0x0F
        hl_high = (hl_val >> 4) & 0x0F
        a_low = self.a & 0x0F
        
        new_hl_high = hl_low
        new_a_low = hl_high
        new_hl_low = a_low
        
        new_hl_val = (new_hl_high << 4) | new_hl_low
        self.write_byte(self.hl, new_hl_val)
        
        self.a = (self.a & 0xF0) | new_a_low
        
        # Flags: S, Z, P/V of A. H=0, N=0. 5, 3 from A.
        f = self.f & 0b00000001 # Keep C
        if self.a & 0x80: f |= 0x80
        if self.a == 0: f |= 0x40
        if self.a & 0x20: f |= 0x20
        if self.a & 0x08: f |= 0x08
        if self._parity(self.a): f |= 0x04
        
        self.f = f
        self.wz = (self.hl + 1) & 0xFFFF

    def _rrd(self):
        # (HL) low -> A low
        # A low -> (HL) high
        # (HL) high -> (HL) low
        
        hl_val = self.read_byte(self.hl)
        hl_low = hl_val & 0x0F
        hl_high = (hl_val >> 4) & 0x0F
        a_low = self.a & 0x0F
        
        new_a_low = hl_low
        new_hl_high = a_low
        new_hl_low = hl_high
        
        new_hl_val = (new_hl_high << 4) | new_hl_low
        self.write_byte(self.hl, new_hl_val)
        
        self.a = (self.a & 0xF0) | new_a_low
        
        # Flags: S, Z, P/V of A. H=0, N=0. 5, 3 from A.
        f = self.f & 0b00000001 # Keep C
        if self.a & 0x80: f |= 0x80
        if self.a == 0: f |= 0x40
        if self.a & 0x20: f |= 0x20
        if self.a & 0x08: f |= 0x08
        if self._parity(self.a): f |= 0x04
        
        self.f = f
        self.wz = (self.hl + 1) & 0xFFFF

    def _reti(self):
        # Return from Interrupt
        # Only differs from RET by signaling I/O device
        # Both RETI and RETN copy IFF2 to IFF1
        self.iff1 = self.iff2
        self._ret()
        
    def _retn(self):
        # Return from NMI
        self.iff1 = self.iff2
        self._ret()
        
    # --- 16-bit Load Helpers (ED) ---
    
    def _ld_dd_indir_nn(self, dd):
        """
        LD dd, (nn)
        """
        addr = self._read_word_pc()
        low = self.read_byte(addr)
        high = self.read_byte((addr + 1) & 0xFFFF)
        setattr(self, dd, (high << 8) | low)
        self.wz = (addr + 1) & 0xFFFF

    # --- Index Instruction Helpers ---

    def _read_byte_pc(self):
        val = self.read_byte(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return val

    def _read_byte_pc_signed(self):
        val = self._read_byte_pc()
        if val > 127:
            val -= 256
        return val

    def _get_effective_addr(self, idx_reg):
        """
        Read displacement d and calculate effective address (IX/IY + d).
        Přečte posunutí d a vypočítá efektivní adresu (IX/IY + d).
        Updates WZ to the effective address.
        """
        d = self._read_byte_pc()
        # Sign extend d
        if d & 0x80:
            d -= 256
            
        reg_val = getattr(self, idx_reg)
        addr = (reg_val + d) & 0xFFFF
        self.wz = addr # Displacement instructions update WZ
        return addr

    def _add_16(self, target, source):
        """
        ADD target, source (16-bit).
        ADD cieľ, zdroj (16bit).
        """
        val_target = getattr(self, target)
        val_source = getattr(self, source)
        
        res_full = val_target + val_source
        res = res_full & 0xFFFF
        
        # Flags: N=0, H, C. Z, S, P/V not affected.
        # Undocumented: 5 and 3 from high byte of result.
        # WZ = target_initial + 1
        
        mask = 0b11000100 # S, Z, P/V preserved
        f = (self.f & mask)
        
        if res_full > 0xFFFF: f |= 0x01 # C
        if ((val_target & 0x0FFF) + (val_source & 0x0FFF)) > 0x0FFF: f |= 0x10 # H
        
        if (res >> 8) & 0x20: f |= 0x20 # Bit 5
        if (res >> 8) & 0x08: f |= 0x08 # Bit 3
            
        self.f = f
        setattr(self, target, res)
        self.wz = (val_target + 1) & 0xFFFF

    def _prefix_dd(self):
        self._prefix_idx('ix')

    def _prefix_fd(self):
        self._prefix_idx('iy')

    def _prefix_idx(self, idx_reg):
        """
        Handle DD/FD prefix instructions.
        Obsluha instrukcí s předponou DD/FD.
        """
        opcode = self._fetch_opcode()
        
        # 16-bit Load: LD IX/IY, nn (0x21), LD (nn), IX/IY (0x22), LD IX/IY, (nn) (0x2A)
        if opcode == 0x21: self._ld_dd_nn(idx_reg)
        elif opcode == 0x22: self._ld_nn_indir_dd(idx_reg)
        elif opcode == 0x2A: self._ld_dd_indir_nn(idx_reg)
        elif opcode == 0xF9: self.sp = getattr(self, idx_reg) # LD SP, IX/IY
        
        # PUSH/POP IX/IY (0xE5/0xE1)
        elif opcode == 0xE5: self._push_qq(idx_reg)
        elif opcode == 0xE1: self._pop_qq(idx_reg)
        
        # 16-bit Arithmetic: ADD IX/IY, ss (09, 19, 29, 39)
        elif opcode == 0x09: self._add_16(idx_reg, 'bc')
        elif opcode == 0x19: self._add_16(idx_reg, 'de')
        elif opcode == 0x29: self._add_16(idx_reg, idx_reg)
        elif opcode == 0x39: self._add_16(idx_reg, 'sp')
        
        # INC/DEC IX/IY (0x23/0x2B)
        elif opcode == 0x23: self._inc_ss(idx_reg)
        elif opcode == 0x2B: self._dec_ss(idx_reg)
        
        # EX (SP), IX/IY (0xE3)
        elif opcode == 0xE3:
            val_sp = self._read_word_sp()
            old_idx = getattr(self, idx_reg)
            self._write_word_sp(old_idx)
            setattr(self, idx_reg, val_sp)
            self.wz = val_sp
        
        # JP (IX/IY) (0xE9)
        elif opcode == 0xE9: self.pc = getattr(self, idx_reg)
        
        # Bit Instructions (DDCB / FDCB)
        elif opcode == 0xCB: self._prefix_idx_cb(idx_reg)
        
        # --- Displacement Instructions (IX+d) ---
        # If opcode uses (HL), it now uses (IX+d)
        elif opcode in [0x34, 0x35, 0x36, 0x46, 0x4E, 0x56, 0x5E, 0x66, 0x6E, 0x7E, 
                        0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x77, 
                        0x86, 0x8E, 0x96, 0x9E, 0xA6, 0xAE, 0xB6, 0xBE]:
            
            addr = self._get_effective_addr(idx_reg)
            
            if opcode == 0x34: # INC (IX+d)
                val = self.read_byte(addr)
                res = (val + 1) & 0xFF
                c_flag = self.f & 0x01
                self._update_flags_add(val, 1, res, 0)
                self.f = (self.f & 0xFE) | c_flag
                self.write_byte(addr, res)
            elif opcode == 0x35: # DEC (IX+d)
                val = self.read_byte(addr)
                res = (val - 1) & 0xFF
                c_flag = self.f & 0x01
                self._update_flags_sub(val, 1, res, 0)
                self.f = (self.f & 0xFE) | c_flag
                self.write_byte(addr, res)
            elif opcode == 0x36: # LD (IX+d), n
                val = self._read_byte_pc()
                self.write_byte(addr, val)
            elif opcode == 0x46: self.b = self.read_byte(addr)
            elif opcode == 0x4E: self.c = self.read_byte(addr)
            elif opcode == 0x56: self.d = self.read_byte(addr)
            elif opcode == 0x5E: self.e = self.read_byte(addr)
            elif opcode == 0x66: self.h = self.read_byte(addr)
            elif opcode == 0x6E: self.l = self.read_byte(addr)
            elif opcode == 0x7E: self.a = self.read_byte(addr)
            elif opcode == 0x70: self.write_byte(addr, self.b)
            elif opcode == 0x71: self.write_byte(addr, self.c)
            elif opcode == 0x72: self.write_byte(addr, self.d)
            elif opcode == 0x73: self.write_byte(addr, self.e)
            elif opcode == 0x74: self.write_byte(addr, self.h)
            elif opcode == 0x75: self.write_byte(addr, self.l)
            elif opcode == 0x77: self.write_byte(addr, self.a)
            elif opcode == 0x86: self._add_val(self.read_byte(addr), False)
            elif opcode == 0x8E: self._add_val(self.read_byte(addr), True)
            elif opcode == 0x96: self._sub_val(self.read_byte(addr), False)
            elif opcode == 0x9E: self._sub_val(self.read_byte(addr), True)
            elif opcode == 0xA6: self._and_val(self.read_byte(addr))
            elif opcode == 0xAE: self._xor_val(self.read_byte(addr))
            elif opcode == 0xB6: self._or_val(self.read_byte(addr))
            elif opcode == 0xBE: self._cp_val(self.read_byte(addr))

        # --- IXH/IXL Instructions ---
        # If opcode uses H or L, it now uses IXH or IXL (or IYH/IYL)
        # Note: These don't have a displacement byte.
        else:
            idx_h = idx_reg + 'h'
            idx_l = idx_reg + 'l'
            
            # LD idx_h, r
            if 0x60 <= opcode <= 0x67: # LD IXH, B,C,D,E,IXH,IXL,(IX+d),A
                if opcode == 0x66: # LD IXH, (IX+d) - actually this opcode is LD H, (IX+d)
                    # Wait, 0x66 with DD is LD H, (IX+d). 
                    # Actually, the rule is: if the instruction uses (HL), 
                    # then H and L are NOT replaced.
                    # 0x66 is LD H, (HL). So DD 66 d is LD H, (IX+d).
                    # My displacement logic already handles 0x66.
                    pass
                else:
                    src_regs = ['b', 'c', 'd', 'e', idx_h, idx_l, None, 'a']
                    setattr(self, idx_h, getattr(self, src_regs[opcode - 0x60]))
            
            # LD idx_l, r
            elif 0x68 <= opcode <= 0x6F: # LD IXL, B,C,D,E,IXH,IXL,(IX+d),A
                if opcode == 0x6E: # LD L, (IX+d)
                    pass
                else:
                    src_regs = ['b', 'c', 'd', 'e', idx_h, idx_l, None, 'a']
                    setattr(self, idx_l, getattr(self, src_regs[opcode - 0x68]))
            
            # LD r, idx_h
            elif opcode in [0x44, 0x4C, 0x54, 0x5C, 0x64, 0x6C, 0x7C]:
                dest_regs = {0x44: 'b', 0x4C: 'c', 0x54: 'd', 0x5C: 'e', 0x64: idx_h, 0x6C: 'l', 0x7C: 'a'}
                setattr(self, dest_regs[opcode], getattr(self, idx_h))
            
            # LD r, idx_l
            elif opcode in [0x45, 0x4D, 0x55, 0x5D, 0x65, 0x6D, 0x7D]:
                dest_regs = {0x45: 'b', 0x4D: 'c', 0x55: 'd', 0x5D: 'e', 0x65: idx_h, 0x6D: idx_l, 0x7D: 'a'}
                setattr(self, dest_regs[opcode], getattr(self, idx_l))

            # INC/DEC IXH/L
            elif opcode == 0x24: self._inc_r(idx_h)
            elif opcode == 0x25: self._dec_r(idx_h)
            elif opcode == 0x26: setattr(self, idx_h, self._read_byte_pc())
            elif opcode == 0x2C: self._inc_r(idx_l)
            elif opcode == 0x2D: self._dec_r(idx_l)
            elif opcode == 0x2E: setattr(self, idx_l, self._read_byte_pc())
            
            # ALU A, idx_h/l
            elif opcode == 0x84: self._add_val(getattr(self, idx_h), False)
            elif opcode == 0x85: self._add_val(getattr(self, idx_l), False)
            elif opcode == 0x8C: self._add_val(getattr(self, idx_h), True)
            elif opcode == 0x8D: self._add_val(getattr(self, idx_l), True)
            elif opcode == 0x94: self._sub_val(getattr(self, idx_h), False)
            elif opcode == 0x95: self._sub_val(getattr(self, idx_l), False)
            elif opcode == 0x9C: self._sub_val(getattr(self, idx_h), True)
            elif opcode == 0x9D: self._sub_val(getattr(self, idx_l), True)
            elif opcode == 0xA4: self._and_val(getattr(self, idx_h))
            elif opcode == 0xA5: self._and_val(getattr(self, idx_l))
            elif opcode == 0xAC: self._xor_val(getattr(self, idx_h))
            elif opcode == 0xAD: self._xor_val(getattr(self, idx_l))
            elif opcode == 0xB4: self._or_val(getattr(self, idx_h))
            elif opcode == 0xB5: self._or_val(getattr(self, idx_l))
            elif opcode == 0xBC: self._cp_val(getattr(self, idx_h))
            elif opcode == 0xBD: self._cp_val(getattr(self, idx_l))

            else:
                 # Fallback to standard opcode if not specifically handled for index registers.
                 if self.opcodes[opcode] != self._unimplemented_opcode:
                     self.opcodes[opcode]()
                 else:
                     print(f"Unimplemented Index ({idx_reg}) opcode: {hex(opcode)}")

    def _prefix_idx_cb(self, idx_reg):
        """
        Handle DD CB d <opcode> and FD CB d <opcode>.
        Obsluha instrukcí s předponami DD CB d a FD CB d.
        Fetch displacement d, then opcode, then execute.
        Načíst posun d, poté operační kód a vykonat.
        """
        # Displacement comes BEFORE the opcode for DDCB/FDCB!
        # Posun d přichází PŘED operačním kódem u DDCB/FDCB!
        d = self._read_byte_pc()
        if d & 0x80: d -= 256
        
        sub_opcode = self._fetch_opcode()
        
        reg_val = getattr(self, idx_reg)
        addr = (reg_val + d) & 0xFFFF
        
        self._cb_memory_op(sub_opcode, addr)

    def _cb_memory_op(self, opcode, addr):
        """
        Execute CB-style bit operation on memory address.
        """
        # Decoding similar to _prefix_cb
        # RLC, RRC, RL, RR, SLA, SRA, SLL, SRL (00-3F)
        # BIT b, (HL) (40-7F)
        # RES b, (HL) (80-BF)
        # SET b, (HL) (C0-FF)
        
        val = self.read_byte(addr)
        
        # Rotates and Shifts (00-3F)
        if 0x00 <= opcode <= 0x3F:
            if opcode & 0xF8 == 0x00: val = self._rlc_val(val) # RLC
            elif opcode & 0xF8 == 0x08: val = self._rrc_val(val) # RRC
            elif opcode & 0xF8 == 0x10: val = self._rl_val(val)  # RL
            elif opcode & 0xF8 == 0x18: val = self._rr_val(val)  # RR
            elif opcode & 0xF8 == 0x20: val = self._sla_val(val) # SLA
            elif opcode & 0xF8 == 0x28: val = self._sra_val(val) # SRA
            elif opcode & 0xF8 == 0x30: val = self._sll_val(val) # SLL (Undocumented)
            elif opcode & 0xF8 == 0x38: val = self._srl_val(val) # SRL
            
            self.write_byte(addr, val)
            
        # BIT b, (HL) (40-7F)
        elif 0x40 <= opcode <= 0x7F:
            bit = (opcode >> 3) & 0x07
            self._bit(bit, val, bits53_val=(addr >> 8) & 0xFF)
            
        # RES b, (HL) (80-BF)
        elif 0x80 <= opcode <= 0xBF:
            bit = (opcode >> 3) & 0x07
            val &= ~(1 << bit)
            self.write_byte(addr, val)
            
        # SET b, (HL) (C0-FF)
        elif 0xC0 <= opcode <= 0xFF:
            bit = (opcode >> 3) & 0x07
            val |= (1 << bit)
            self.write_byte(addr, val)

    # --- Reusable ALU Helpers for Values ---
    # We need to extract logic from existing _rlc_r, etc. or just implement value versions.
    # To keep it simple and safe, I'll implement _rlc_val, etc. here locally or reuse if possible.
    # Checking existing CB logic would decrease risk, but refactoring might break things.
    # I'll implement standalone value-based helpers for now.
    
    def _rlc_val(self, val):
        bit7 = (val >> 7) & 0x01
        res = ((val << 1) & 0xFF) | bit7
        self._update_flags_rot(res, bit7)
        return res
        
    def _rrc_val(self, val):
        bit0 = val & 0x01
        res = (val >> 1) | (bit0 << 7)
        self._update_flags_rot(res, bit0)
        return res
        
    def _rl_val(self, val):
        bit7 = (val >> 7) & 0x01
        carry = 1 if (self.f & 0x01) else 0
        res = ((val << 1) & 0xFF) | carry
        self._update_flags_rot(res, bit7)
        return res
        
    def _rr_val(self, val):
        bit0 = val & 0x01
        carry = 1 if (self.f & 0x01) else 0
        res = (val >> 1) | (carry << 7)
        self._update_flags_rot(res, bit0)
        return res
        
    def _sla_val(self, val):
        bit7 = (val >> 7) & 0x01
        res = (val << 1) & 0xFF
        self._update_flags_rot(res, bit7)
        return res
        
    def _sra_val(self, val):
        bit0 = val & 0x01
        bit7 = val & 0x80
        res = (val >> 1) | bit7
        self._update_flags_rot(res, bit0)
        return res
        
    def _sll_val(self, val): # Undocumented
        bit7 = (val >> 7) & 0x01
        res = ((val << 1) & 0xFF) | 0x01
        self._update_flags_rot(res, bit7)
        return res
        
    def _srl_val(self, val):
        bit0 = val & 0x01
        res = (val >> 1)
        self._update_flags_rot(res, bit0)
        return res
        
    def _update_flags_rot(self, res, carry):
        # Flags: S, Z, H=0, P/V, N=0, C
        s = (res & 0x80) != 0
        z = (res == 0)
        p = self._parity(res)
        
        f = 0
        if s: f |= 0x80
        if z: f |= 0x40
        if p: f |= 0x04
        if carry: f |= 0x01
        # H and N are 0
        self.f = f

    def _bit_check(self, bit, val):
        is_zero = (val & (1 << bit)) == 0
        
        # BIT: Z=1 if bit is 0. H=1, N=0.
        # S, P/V ?
        # Z80 Manual: Z is set if specified bit is 0.
        # H is set. N is reset.
        # S is set if bit 7 of result is set (Wait, result involves bit?)
        # For BIT b, (HL):
        # Z set if bit is 0.
        # N=0, H=1.
        # S, P/V are unknown/undefined or specific?
        # Let's stick to core flags.
        
        f = (self.f & 0b00000001) # Keep C
        if is_zero: f |= 0x40
        f |= 0x10 # H=1
        
        # P/V as Z? Undocumented usually says P/V is same as Z for BIT?
        # Actually P/V is often "Unknown" or set to Z.
        if is_zero: f |= 0x04
        
        # S? If checking bit 7 and it is 1, S=1? 
        # If checking bit 7 and it is 0 ...
        # Standard behavior: S, Z, P/V reflect the tested byte AND 1<<b
        # So if we test bit 7 and it is 1, result is 0x80 -> S=1.
        
        res = val & (1 << bit)
        if res & 0x80: f |= 0x80
        
        self.f = f
        self.f = f

    # --- I/O Instructions ---

    def _in_a_n(self):
        """
        IN A, (n)
        Opcode: DB n
        """
        n = self._read_byte_pc()
        port = (self.a << 8) | n
        if self.ula:
            self.cycles += self.ula.get_contention(self.cycles, port, is_io=True)
        self.cycles += 4
        if self.io_bus:
            self.a = self.io_bus.read_byte(port, self.cycles)
        else:
            self.a = 0xFF
        # IN A, (n) updates WZ with 16-bit increment: (A << 8 | n) + 1
        self.wz = (port + 1) & 0xFFFF

    def _out_n_a(self):
        """
        OUT (n), A
        Opcode: D3 n
        """
        n = self._read_byte_pc()
        port = (self.a << 8) | n
        if self.ula:
            self.cycles += self.ula.get_contention(self.cycles, port, is_io=True)
        self.cycles += 4
        if self.io_bus:
            self.io_bus.write_byte(port, self.a)
        # OUT (n), A updates WZ with 8-bit increment for n: (A << 8) | ((n + 1) & 0xFF)
        self.wz = (self.a << 8) | ((n + 1) & 0xFF)

    def _in_r_c(self, r):
        """
        IN r, (C)
        """
        port = self.bc
        val = 0xFF
        if self.ula:
            self.cycles += self.ula.get_contention(self.cycles, port, is_io=True)
        self.cycles += 4
        if self.io_bus:
            val = self.io_bus.read_byte(port, self.cycles)
        
        self.wz = (port + 1) & 0xFFFF
        
        # Update register
        if r == 'f': # Special case for IN (C) which only updates flags
             pass
        else:
            setattr(self, r, val)
            
        # Update flags
        # S, Z, P/V, N=0, H=0. 5, 3 from val.
        f = self.f & 0b00000001 # Keep C
        if val & 0x80: f |= 0x80
        if val == 0: f |= 0x40
        if val & 0x20: f |= 0x20
        if val & 0x08: f |= 0x08
        # P/V is parity of input
        parity = bin(val).count('1') % 2 == 0
        if parity: f |= 0x04
        
        self.f = f

    def _out_c_r(self, r):
        """
        OUT (C), r
        """
        port = self.bc
        val = 0
        if r == '0': val = 0
        else: val = getattr(self, r)
        
        if self.ula:
            self.cycles += self.ula.get_contention(self.cycles, port, is_io=True)
        self.cycles += 4
        if self.io_bus:
            self.io_bus.write_byte(port, val)
            
        self.wz = (port + 1) & 0xFFFF

    def _update_block_io_flags(self, val, modifier, b_old):
        """
        Update flags for Block I/O instructions (INI, IND, OUTI, OUTD).
        Uses NMOS Z80 logic for undocumented flags.
        """
        res_b = self.b
        
        # S, Z, F5, F3 from B after decrement
        # Z is set if B=0, S is bit 7, F5/F3 are bits 5 and 3
        f = (res_b & 0x80) | (0x40 if res_b == 0 else 0) | (res_b & 0x28)
        
        # N flag is bit 7 of the value transferred
        if val & 0x80: f |= 0x02
        
        # C and H flags are set if (val + modifier) > 255
        temp = (val + modifier) & 0x1FF
        if temp > 255:
            f |= 0x11 # Set both H and C
            
        # P/V flag is the parity of ((temp & 7) ^ B_old ^ h_int)
        # where h_int is the half-carry from (val + modifier)
        h_int = 1 if (val & 0x0F) + (modifier & 0x0F) > 0x0F else 0
        xor_val = (temp & 0x07) ^ b_old ^ h_int
        if self._parity(xor_val):
            f |= 0x04
            
        self.f = f

    def _ini(self):
        """
        INI: B = B - 1; IN (HL), (C); INC HL
        """
        bc_before = self.bc
        b_old = self.b
        port = self.bc # Use B before decrement for port address
        c_mod = (self.c + 1) & 0xFF
        self.b = (self.b - 1) & 0xFF
        val = 0xFF
        if self.ula:
            self.cycles += self.ula.get_contention(self.cycles, port, is_io=True)
        self.cycles += 4
        if self.io_bus:
            val = self.io_bus.read_byte(port, self.cycles)
            
        self.write_byte(self.hl, val)
        self.wz = (bc_before + 1) & 0xFFFF
        
        self._update_block_io_flags(val, c_mod, b_old)
        
        self.hl = (self.hl + 1) & 0xFFFF

    def _inir(self):
        self._ini()
        if self.b != 0:
            self.pc = (self.pc - 2) & 0xFFFF
            self.wz = (self.pc + 1) & 0xFFFF
            # Flags 5, 4 and 3 are set from bits 13, 12 and 11 of the instruction address (PC)
            # Actually, H is cleared (bit 4), and F5/F3 come from PC high byte.
            self.f = (self.f & 0b11000111) | ((self.pc >> 8) & 0x28)
            self.cycles += 21
        else:
            self.cycles += 16

    def _ind(self):
        """
        IND: B = B - 1; IN (HL), (C); DEC HL
        """
        bc_before = self.bc
        b_old = self.b
        port = self.bc # Use B before decrement
        c_mod = (self.c - 1) & 0xFF
        self.b = (self.b - 1) & 0xFF
        val = 0xFF
        if self.ula:
            self.cycles += self.ula.get_contention(self.cycles, port, is_io=True)
        self.cycles += 4
        if self.io_bus:
            val = self.io_bus.read_byte(port, self.cycles)
            
        self.write_byte(self.hl, val)
        self.wz = (bc_before - 1) & 0xFFFF
        
        self._update_block_io_flags(val, c_mod, b_old)
        
        self.hl = (self.hl - 1) & 0xFFFF

    def _indr(self):
        self._ind()
        if self.b != 0:
            self.pc = (self.pc - 2) & 0xFFFF
            self.wz = (self.pc + 1) & 0xFFFF
            self.f = (self.f & 0b11000111) | ((self.pc >> 8) & 0x28)
            self.cycles += 21
        else:
            self.cycles += 16

    def _outi(self):
        """
        OUTI: B = B - 1; OUT (C), (HL); INC HL
        """
        b_old = self.b
        self.b = (self.b - 1) & 0xFF
        port = self.bc # Use B AFTER decrement for port address
        val = self.read_byte(self.hl)
        if self.ula:
            self.cycles += self.ula.get_contention(self.cycles, port, is_io=True)
        self.cycles += 4
        if self.io_bus:
            self.io_bus.write_byte(port, val)
            
        self.wz = (port + 1) & 0xFFFF
        
        # Save L before increment for flag update modifier
        l_old = self.l
        self.hl = (self.hl + 1) & 0xFFFF
        self._update_block_io_flags(val, l_old, b_old)

    def _otir(self):
        self._outi()
        if self.b != 0:
            self.pc = (self.pc - 2) & 0xFFFF
            self.wz = (self.pc + 1) & 0xFFFF
            # H is also cleared during repeat for OTIR/OTDR
            self.f = (self.f & 0b11000111) | ((self.pc >> 8) & 0x28)
            self.cycles += 21
        else:
            self.cycles += 16

    def _outd(self):
        """
        OUTD: B = B - 1; OUT (C), (HL); DEC HL
        """
        b_old = self.b
        self.b = (self.b - 1) & 0xFF
        port = self.bc # Use B AFTER decrement
        val = self.read_byte(self.hl)
        if self.ula:
            self.cycles += self.ula.get_contention(self.cycles, port, is_io=True)
        self.cycles += 4
        if self.io_bus:
            self.io_bus.write_byte(port, val)
            
        self.wz = (port - 1) & 0xFFFF
        
        # Save L before decrement
        l_old = self.l
        self.hl = (self.hl - 1) & 0xFFFF
        self._update_block_io_flags(val, l_old, b_old)

    def _otdr(self):
        self._outd()
        if self.b != 0:
            self.pc = (self.pc - 2) & 0xFFFF
            self.wz = (self.pc + 1) & 0xFFFF
            self.f = (self.f & 0b11000111) | ((self.pc >> 8) & 0x28)
            self.cycles += 21
        else:
            self.cycles += 16
