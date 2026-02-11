class Disassembler:
    def __init__(self):
        self.opcodes = self._init_opcodes()
        self.cb_opcodes = self._init_cb_opcodes()
        self.ed_opcodes = self._init_ed_opcodes()

    def disassemble(self, memory, pc):
        """
        Disassemble a single instruction at address pc.
        Returns (mnemonic, length, bytes_str)
        """
        try:
            opcode = memory.read_byte(pc)
            
            # Prefixes
            if opcode == 0xCB:
                return self._disassemble_cb(memory, pc)
            elif opcode == 0xED:
                return self._disassemble_ed(memory, pc)
            elif opcode == 0xDD:
                return self._disassemble_index(memory, pc, 'IX')
            elif opcode == 0xFD:
                return self._disassemble_index(memory, pc, 'IY')
            
            # Standard Opcodes
            info = self.opcodes.get(opcode)
            if info:
                fmt, length = info
                # Read operands
                operands = []
                bytes_data = [opcode]
                
                if length > 1:
                    b1 = memory.read_byte((pc + 1) & 0xFFFF)
                    bytes_data.append(b1)
                    operands.append(b1)
                
                if length > 2:
                    b2 = memory.read_byte((pc + 2) & 0xFFFF)
                    bytes_data.append(b2)
                    operands.append(b2)
                    
                bytes_str = ' '.join([f"{b:02X}" for b in bytes_data])
                
                # Format mnemonic
                # nn = 16-bit payload (b2 << 8 | b1)
                # n = 8-bit payload (b1)
                # d = 8-bit signed displacement (b1)
                
                mnemonic = fmt
                if 'nn' in fmt and length == 3:
                     val = (operands[1] << 8) | operands[0]
                     mnemonic = fmt.replace('nn', f"0x{val:04X}")
                elif 'n' in fmt and length == 2:
                     val = operands[0]
                     mnemonic = fmt.replace('n', f"0x{val:02X}")
                elif 'd' in fmt and length == 2:
                     val = operands[0]
                     if val > 127: val -= 256
                     sign = '+' if val >= 0 else ''
                     mnemonic = fmt.replace('d', f"{sign}{val}")
                     
                return mnemonic, length, bytes_str
            else:
                return f"DB 0x{opcode:02X}", 1, f"{opcode:02X}"
                
        except Exception as e:
            return f"ERR: {e}", 1, "00"

    def _disassemble_cb(self, memory, pc):
        byte = memory.read_byte((pc + 1) & 0xFFFF)
        bytes_str = f"CB {byte:02X}"
        mnemonic = self.cb_opcodes.get(byte, f"CB 0x{byte:02X}")
        return mnemonic, 2, bytes_str

    def _disassemble_ed(self, memory, pc):
        byte = memory.read_byte((pc + 1) & 0xFFFF)
        bytes_str = f"ED {byte:02X}"
        mnemonic = self.ed_opcodes.get(byte, f"ED 0x{byte:02X}")
        # ED instructions can have operands (e.g. LD (nn), dd is 4 bytes: ED op low high)
        # Check standard ED length or hardcode?
        # Most ED are 2 bytes. Exceptions:
        # 43/53/63/73 (LD (nn), dd) -> 4 bytes
        # 4B/5B/6B/7B (LD dd, (nn)) -> 4 bytes
        extra_len = 0
        extra_bytes = ""
        
        if (byte & 0xCF) == 0x43 or (byte & 0xCF) == 0x4B:
             # It is 16-bit load ED val len=4
             low = memory.read_byte((pc + 2) & 0xFFFF)
             high = memory.read_byte((pc + 3) & 0xFFFF)
             val = (high << 8) | low
             extra_len = 2
             extra_bytes = f" {low:02X} {high:02X}"
             mnemonic = mnemonic.replace("nn", f"0x{val:04X}")
             
        return mnemonic, 2 + extra_len, bytes_str + extra_bytes

    def _disassemble_index(self, memory, pc, reg_name):
        opcode = memory.read_byte((pc + 1) & 0xFFFF)
        
        if opcode == 0xCB:
             # DDCB/FDCB d op
             d = memory.read_byte((pc + 2) & 0xFFFF)
             op = memory.read_byte((pc + 3) & 0xFFFF)
             
             # Adjust d
             if d > 127: d -= 256
             sign = '+' if d >= 0 else ''
             disp_str = f"({reg_name}{sign}{d})"
             
             # Get base mnemonic
             base_mnemonic = self.cb_opcodes.get(op, f"BIT ?, {op:02X}")
             
             # Replace (HL) with (IX+d)
             # CB ops usually operate on r or (HL).
             # DDCB d op -> operates on (IX+d).
             # Usually DDCB ... RES 0, (HL) -> RES 0, (IX+d)
             if "(HL)" in base_mnemonic:
                 mnemonic = base_mnemonic.replace("(HL)", disp_str)
             else:
                 # Standard DDCB behavior: performs op on (IX+d), copies result to r?
                 # Disassemblers often show `SET b, (IX+d)` even if bits imply `SET b, (IX+d), r`
                 # We will just show the (HL) replaced version or generic.
                 # If base mnemonic has register (e.g. SET 0, B), it is technically UNDOCUMENTED copy.
                 # We'll validly disassemble the documented 'default' which corresponds to (HL) slot in CB table.
                 # Wait, op is the instruction.
                 # If we look up 'op' in standard CB table, we get e.g. "SET 0, B".
                 # This corresponds to DDCB... B. This constructs (IX+d) and copies to B.
                 # But standard usage is with z=6 (HL).
                 # So we should probably force lookup as if z=6?
                 # No, let's just strip the register and put (IX+d) if it differs, or append?
                 # Simpler: All indexes act on (IX+d).
                 # Let's map 'op' bits to function (RES/SET/ROT) and bit.
                 # x = (op >> 6) & 3, y = (op >> 3) & 7, z = op & 7
                 # z is source/dest. In DDCB, result is written to (IX+d).
                 # If z != 6, it ALSO copies to reg z.
                 # We will display "OP ..., (IX+d)"
                 
                 # Reconstruct mnemonic generic
                 x = (op >> 6) & 3
                 y = (op >> 3) & 7
                 z = op & 7
                 
                 shifts = ['RLC', 'RRC', 'RL', 'RR', 'SLA', 'SRA', 'SLL', 'SRL']
                 if x == 0:
                     mnemonic = f"{shifts[y]} {disp_str}"
                 elif x == 1:
                     mnemonic = f"BIT {y}, {disp_str}"
                 elif x == 2:
                     mnemonic = f"RES {y}, {disp_str}"
                 elif x == 3:
                     mnemonic = f"SET {y}, {disp_str}"
                     
                 if z != 6:
                     mnemonic += f", {['B','C','D','E','H','L','?','A'][z]}"
             
             return mnemonic, 4, f"DD CB {d & 0xFF:02X} {op:02X}"

        # Standard Index
        info = self.opcodes.get(opcode)
        if not info:
            return f"DB 0x{opcode:02X}", 1, f"DD {opcode:02X}"
            
        base_mnemonic, base_len = info
        
        # Check for (HL) or HL
        if "(HL)" in base_mnemonic:
            # Uses displacement
            d = memory.read_byte((pc + 2) & 0xFFFF)
            if d > 127: d -= 256
            sign = '+' if d >= 0 else ''
            disp_str = f"({reg_name}{sign}{d})"
            
            mnemonic = base_mnemonic.replace("(HL)", disp_str)
            length = base_len + 1 # Add displacement byte
            
            # Handle operands (n or nn)
            # Base len include opcode(1) + operands.
            # Index len includes prefix(1) + opcode(1) + disp(1) + operands.
            # So total index len = 1 (Prefix) + 1 (Disp) + (Base len - 1 (Opcode)) + 1 (Opcode) = Base len + 2?
            # Example: LD (HL), n (len 2: 36 nn).
            # Index: DD 36 d n (len 4).
            # My calc: base_len (2) + 1 (disp) + 1 (prefix implicitly handled by caller? No, caller usually adds prefix len?)
            # Wait, `disassemble` returns length of WHOLE instruction.
            # PC points to Prefix.
            # Bytes: [DD] [Op] [d] [n]
            # Base info: length include [Op] [n] -> 2.
            # Result length: 1 (DD) + 1 (Op) + 1 (d) + 1 (n) = 4.
            # So Result length = Base length + 2.
            
            length = base_len + 2 
            
            # Fetch operands
            # Opcode at PC+1. d at PC+2. Operands start at PC+3.
            bytes_debug = [0xDD, opcode, d & 0xFF]
            
            # Need to fill 'n' or 'nn' in mnemonic
            # Base mnemonic has 'n' or 'nn' placeholders.
            if 'nn' in mnemonic:
                low = memory.read_byte((pc + 3) & 0xFFFF)
                high = memory.read_byte((pc + 4) & 0xFFFF)
                val = (high << 8) | low
                mnemonic = mnemonic.replace("nn", f"0x{val:04X}")
                bytes_debug.extend([low, high])
            elif 'n' in mnemonic:
                val = memory.read_byte((pc + 3) & 0xFFFF)
                mnemonic = mnemonic.replace("n", f"0x{val:02X}")
                bytes_debug.append(val)
                
            bytes_str = ' '.join([f"{b:02X}" for b in bytes_debug])
            return mnemonic, length, bytes_str
            
        elif "HL" in base_mnemonic:
            # Replaces HL with IX/IY, no displacement (usually)
            # Exception: JP (HL) -> JP (IX) (Correct, no disp)
            # EX DE, HL -> EX DE, IX
            # LD SP, HL -> LD SP, IX
            mnemonic = base_mnemonic.replace("HL", reg_name)
            
            # Length: Prefix(1) + Base len.
            length = base_len + 1
            
            bytes_debug = [0xDD, opcode]
            
            # Operands are at PC+2 (immediately after Opcode)
            if 'nn' in mnemonic:
                low = memory.read_byte((pc + 2) & 0xFFFF)
                high = memory.read_byte((pc + 3) & 0xFFFF)
                val = (high << 8) | low
                mnemonic = mnemonic.replace("nn", f"0x{val:04X}")
                bytes_debug.extend([low, high])
            elif 'n' in mnemonic:
                val = memory.read_byte((pc + 2) & 0xFFFF)
                mnemonic = mnemonic.replace("n", f"0x{val:02X}")
                bytes_debug.append(val)
            
            bytes_str = ' '.join([f"{b:02X}" for b in bytes_debug])
            return mnemonic, length, bytes_str
            
        else:
             # Prefix ignored or affects something else?
             # Just return base op with prefix note
             return f"{base_mnemonic}", base_len + 1, f"DD {opcode:02X} ..."

    def _init_opcodes(self):
        ops = {}
        # 8-bit Loads
        # LD r, r'
        regs = ['B', 'C', 'D', 'E', 'H', 'L', '(HL)', 'A']
        for y in range(8):
            for z in range(8):
                opcode = 0x40 | (y << 3) | z
                if opcode == 0x76:
                    ops[opcode] = ("HALT", 1)
                else:
                    ops[opcode] = (f"LD {regs[y]}, {regs[z]}", 1)
        
        # LD r, n
        for y in range(8):
            opcode = 0x06 | (y << 3)
            ops[opcode] = (f"LD {regs[y]}, n", 2)
            
        # LD r, (BC/DE) is mostly A invalid? No.
        # LD A, (BC) = 0A
        ops[0x0A] = ("LD A, (BC)", 1)
        ops[0x1A] = ("LD A, (DE)", 1)
        ops[0x3A] = ("LD A, (nn)", 3)
        ops[0x02] = ("LD (BC), A", 1)
        ops[0x12] = ("LD (DE), A", 1)
        ops[0x32] = ("LD (nn), A", 3)
        
        # 16-bit Loads
        rp = ['BC', 'DE', 'HL', 'SP']
        for p in range(4):
            opcode = 0x01 | (p << 4)
            ops[opcode] = (f"LD {rp[p]}, nn", 3)
            
            # ADD HL, ss (09, 19, 29, 39)
            opcode_add = 0x09 | (p << 4)
            ops[opcode_add] = (f"ADD HL, {rp[p]}", 1)
            
            # INC ss (03, 13, 23, 33)
            opcode_inc = 0x03 | (p << 4)
            ops[opcode_inc] = (f"INC {rp[p]}", 1)
            
            # DEC ss (0B, 1B, 2B, 3B)
            opcode_dec = 0x0B | (p << 4)
            ops[opcode_dec] = (f"DEC {rp[p]}", 1)
            
            
        # ALU
        alu_ops = ['ADD A,', 'ADC A,', 'SUB', 'SBC A,', 'AND', 'XOR', 'OR', 'CP']
        for y in range(8):
            for z in range(8):
                opcode = 0x80 | (y << 3) | z
                ops[opcode] = (f"{alu_ops[y]} {regs[z]}", 1)
        
        # ALU n
        for y in range(8):
            opcode = 0xC6 | (y << 3)
            ops[opcode] = (f"{alu_ops[y]} n", 2)
            
        # Jumps / Calls
        ops[0xC3] = ("JP nn", 3)
        ops[0xCD] = ("CALL nn", 3)
        ops[0xC9] = ("RET", 1)
        ops[0x18] = ("JR d", 2)
        ops[0x10] = ("DJNZ d", 2)
        
        # Conditional Jumps/Ret/Call
        conds = ['NZ', 'Z', 'NC', 'C', 'PO', 'PE', 'P', 'M']
        for y in range(8):
            # JR cc (only 4 conds: NZ, Z, NC, C) - 20, 28, 30, 38
            if y < 4:
                opcode = 0x20 | (y << 3)
                ops[opcode] = (f"JR {conds[y]}, d", 2)
            
            # JP cc
            opcode = 0xC2 | (y << 3)
            ops[opcode] = (f"JP {conds[y]}, nn", 3)
            
            # CALL cc
            opcode = 0xC4 | (y << 3)
            ops[opcode] = (f"CALL {conds[y]}, nn", 3)
            
            # RET cc
            opcode = 0xC0 | (y << 3)
            ops[opcode] = (f"RET {conds[y]}", 1)
            
        # Common Misc
        ops[0x00] = ("NOP", 1)
        ops[0xF3] = ("DI", 1)
        ops[0xFB] = ("EI", 1)
        ops[0xD3] = ("OUT (n), A", 2)
        ops[0xDB] = ("IN A, (n)", 2)
        ops[0xEB] = ("EX DE, HL", 1)
        ops[0x08] = ("EX AF, AF'", 1)
        ops[0xD9] = ("EXX", 1)
        ops[0xE3] = ("EX (SP), HL", 1)
        ops[0xE9] = ("JP (HL)", 1)
        ops[0xF9] = ("LD SP, HL", 1)
        
        # Stack
        rp2 = ['BC', 'DE', 'HL', 'AF']
        for p in range(4):
            ops[0xC5 | (p << 4)] = (f"PUSH {rp2[p]}", 1)
            ops[0xC1 | (p << 4)] = (f"POP {rp2[p]}", 1)

        # Misc
        ops[0x27] = ("DAA", 1)
        ops[0x2F] = ("CPL", 1)
        ops[0x37] = ("SCF", 1)
        ops[0x3F] = ("CCF", 1)
        
        # Accumulator Rotates
        ops[0x07] = ("RLCA", 1)
        ops[0x0F] = ("RRCA", 1)
        ops[0x17] = ("RLA", 1)
        ops[0x1F] = ("RRA", 1)
        
        # RST
        for y in range(8):
             ops[0xC7 | (y << 3)] = (f"RST {y*8:02X}h", 1)
             
        # Add IO / Special
        
        return ops

    def _init_cb_opcodes(self):
        ops = {}
        # RLC, RRC, RL, RR, SLA, SRA, SLL, SRL (0-7)
        shifts = ['RLC', 'RRC', 'RL', 'RR', 'SLA', 'SRA', 'SLL', 'SRL']
        regs = ['B', 'C', 'D', 'E', 'H', 'L', '(HL)', 'A']
        
        for y in range(8):
            for z in range(8):
                 opcode = (y << 3) | z
                 ops[opcode] = f"{shifts[y]} {regs[z]}"
                 
        # BIT, RES, SET
        for bit in range(8):
            for z in range(8):
                # BIT
                opcode = 0x40 | (bit << 3) | z
                ops[opcode] = f"BIT {bit}, {regs[z]}"
                # RES
                opcode = 0x80 | (bit << 3) | z
                ops[opcode] = f"RES {bit}, {regs[z]}"
                # SET
                opcode = 0xC0 | (bit << 3) | z
                ops[opcode] = f"SET {bit}, {regs[z]}"
        return ops

    def _init_ed_opcodes(self):
        ops = {}
        # Block ops
        ops[0xB0] = "LDIR"
        ops[0xB8] = "LDDR"
        ops[0xA0] = "LDI"
        ops[0xA8] = "LDD"
        ops[0xB1] = "CPIR"
        ops[0xB9] = "CPDR"
        ops[0xA1] = "CPI"
        ops[0xA9] = "CPD"
        
        # Block I/O
        ops[0xA2] = "INI"
        ops[0xB2] = "INIR"
        ops[0xAA] = "IND"
        ops[0xBA] = "INDR"
        ops[0xA3] = "OUTI"
        ops[0xB3] = "OTIR"
        ops[0xAB] = "OUTD"
        ops[0xBB] = "OTDR"
        
        # IM
        ops[0x46] = "IM 0"
        ops[0x56] = "IM 1"
        ops[0x5E] = "IM 2"
        
        # Special Loads
        ops[0x57] = "LD A, I"
        ops[0x47] = "LD I, A"
        ops[0x5F] = "LD A, R"
        ops[0x4F] = "LD R, A"
        
        # Neg
        ops[0x44] = "NEG"
        ops[0x4D] = "RETI"
        ops[0x45] = "RETN"
        
        # ADC HL, ss
        ss = ['BC', 'DE', 'HL', 'SP']
        for p in range(4):
            # ADC HL, ss (4A, 5A, 6A, 7A)
            ops[0x4A | (p << 4)] = f"ADC HL, {ss[p]}"
            # SBC HL, ss (42, 52, 62, 72)
            ops[0x42 | (p << 4)] = f"SBC HL, {ss[p]}"
            
            # LD (nn), dd (43, 53, 63, 73)
            ops[0x43 | (p << 4)] = f"LD (nn), {ss[p]}"
            # LD dd, (nn) (4B, 5B, 6B, 7B)
            ops[0x4B | (p << 4)] = f"LD {ss[p]}, (nn)"
            
        # RLD/RRD
        ops[0x6F] = "RLD"
        ops[0x67] = "RRD"
        
        # IO
        # IN r, (C) / OUT (C), r
        # 40 (B), 48 (C), 50 (D), 58 (E), 60 (H), 68 (L), 78 (A), 70 (F/0)
        regs_io = ['B', 'C', 'D', 'E', 'H', 'L', '(HL)', 'A'] # (HL) is exception -> 0x70 is usually IN F, (C) or similar
        # Correct mapping for IN r, (C):
        # 40, 48, 50, 58, 60, 68, 70, 78
        io_regs = ['B', 'C', 'D', 'E', 'H', 'L', 'F', 'A'] # 0x70 is IN F,(C) / OUT (C),0
        for i in range(8):
             # IN r, (C)
             opcode_in = 0x40 | (i << 3)
             ops[opcode_in] = f"IN {io_regs[i]}, (C)"
             # OUT (C), r
             opcode_out = 0x41 | (i << 3)
             if i == 6: # 0x71 -> OUT (C), 0
                 ops[opcode_out] = "OUT (C), 0"
             else:
                 ops[opcode_out] = f"OUT (C), {io_regs[i]}"
                 
        return ops
