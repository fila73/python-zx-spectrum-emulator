from src.cpu import Z80
from src.memory import Memory

def main():
    print("Running manual verification (Flow Control)...")
    memory = Memory()
    cpu = Z80(memory)
    
    # Program: Simple loop
    # LD B, 5        (0x06 0x05)
    # Loop:
    # DEC B          (0x05)
    # JR NZ, -3      (0x20 0xFD) ; Jump back to DEC B
    # HALT           (0x76) - Not implemented, just stop
    
    # Opcode 0x06 (LD B, n) - Implemented
    # Opcode 0x05 (DEC B) - Not implemented! Wait, I only did DEC A (0x3D) and 16-bit DEC.
    # I did NOT implement 8-bit DEC r for other registers yet!
    # Let me check cpu.py...
    
    # checking cpu.py...
    # I see:
    # self.opcodes[0x3C] = lambda: self._inc_r('a')
    # self.opcodes[0x3D] = lambda: self._dec_r('a')
    # I have NOT implemented INC/DEC for B, C, D, E, H, L.
    
    # I need to use compatible instructions.
    # I implemented DEC A (0x3D).
    # So let's use A as loop counter.
    
    # Program:
    # LD A, 5        (0x3E 0x05)
    # Loop:
    # DEC A          (0x3D)
    # JR NZ, -3      (0x20 0xFD)
    
    program = b'\x3E\x05\x3D\x20\xFD'
    memory.load_rom(program)
    
    print("Initial State: PC=0, A=0")
    
    # Step 1: LD A, 5
    cpu.step()
    print(f"After LD A, 5: A={cpu.a}")
    if cpu.a != 5:
        print("FAIL: A should be 5")
        exit(1)
        
    # Loop execution
    # Iteration 1: DEC A -> 4. NZ. Jump back.
    # Iteration 2: DEC A -> 3. NZ. Jump back.
    # ...
    # Iteration 5: DEC A -> 0. Z. Fall through.
    
    max_steps = 20
    steps = 0
    while cpu.pc < len(program) and steps < max_steps:
        prev_pc = cpu.pc
        cpu.step()
        steps += 1
        print(f"Step {steps}: PC={cpu.pc:04X}, A={cpu.a}, Z_Flag={(cpu.f&0x40)!=0}")
        
        # If we passed the jump (PC >= 5), we are done.
        # Program length is 5 bytes. Address 0..4.
        # Fallthrough is PC=5.
        if cpu.pc >= 5:
            break
            
    if cpu.a != 0:
        print(f"FAIL: A should be 0, but is {cpu.a}")
        exit(1)
        
    print("PASS: Flow control verification successful.")

    # Test 4: 16-bit Load Instructions
    # Zkouška 4: 16bitové instrukce načítání
    print("Running manual verification (16-bit Loads)...")
    cpu.pc = 0x8000
    # LD HL, 0x55AA (21 AA 55)
    memory.write_byte(0x8000, 0x21)
    memory.write_byte(0x8001, 0xAA)
    memory.write_byte(0x8002, 0x55)
    # LD (0x9000), HL (22 00 90)
    memory.write_byte(0x8003, 0x22)
    memory.write_byte(0x8004, 0x00)
    memory.write_byte(0x8005, 0x90)
    
    # LD HL, 0x0000 (21 00 00)
    memory.write_byte(0x8006, 0x21)
    memory.write_byte(0x8007, 0x00)
    memory.write_byte(0x8008, 0x00)
    
    # LD HL, (0x9000) (2A 00 90)
    memory.write_byte(0x8009, 0x2A)
    memory.write_byte(0x800A, 0x00)
    memory.write_byte(0x800B, 0x90)
    
    # Run 4 instructions
    for _ in range(4):
        cpu.step()
    
    if cpu.hl != 0x55AA:
        print(f"FAIL: HL is 0x{cpu.hl:04X}, expected 0x55AA")
        exit(1)
    else:
        print("PASS: 16-bit Load verification successful.")
        
    # Test 5: Block Transfer (LDIR)
    # Zkouška 5: Blokový přenos (LDIR)
    print("Running manual verification (LDIR)...")
    cpu.pc = 0x8000
    # Copy 3 bytes from 0x9000 to 0x9100
    # Data: AA BB CC
    memory.write_byte(0x9000, 0xAA)
    memory.write_byte(0x9001, 0xBB)
    memory.write_byte(0x9002, 0xCC)
    
    # Setup registers
    cpu.hl = 0x9000
    cpu.de = 0x9100
    cpu.bc = 0x0003
    
    # LDIR opcode: ED B0
    memory.write_byte(0x8000, 0xED)
    memory.write_byte(0x8001, 0xB0)
    
    # Run loop
    # BC=3 -> LDI, PC-=2 (Loop)
    # BC=2 -> LDI, PC-=2 (Loop)
    # BC=1 -> LDI, PC+=2 (Done)
    # Total steps: 3 instructions executed? No, LDIR is one instruction that manipulates PC.
    # But step() executes one opcode.
    # If LDIR decrements PC, step() is called again and reads LDIR again.
    # So we need 3 calls to step().
    
    for _ in range(3):
        cpu.step()
        
    if memory.read_byte(0x9100) != 0xAA or memory.read_byte(0x9101) != 0xBB or memory.read_byte(0x9102) != 0xCC:
        print("FAIL: LDIR did not copy data correctly")
        exit(1)
        
    if cpu.bc != 0:
        print(f"FAIL: BC should be 0, is {cpu.bc}")
        exit(1)
        
    print("PASS: LDIR verification successful.")

    # Test 6: Bit Manipulation (Prefix CB)
    # Zkouška 6: Bitové operace (předpona CB)
    print("Running manual verification (Bit Manipulation)...")
    cpu.pc = 0x8000
    cpu.a = 0x01
    
    # RLC A (CB 07) -> A=0x02, C=0
    # SET 7, A (CB FF) -> A=0x82
    # BIT 7, A (CB 7F) -> Z=0 (Not Zero)
    
    memory.write_byte(0x8000, 0xCB)
    memory.write_byte(0x8001, 0x07)
    
    memory.write_byte(0x8002, 0xCB)
    memory.write_byte(0x8003, 0xFF)
    
    memory.write_byte(0x8004, 0xCB)
    memory.write_byte(0x8005, 0x7F)
    
    # Step 1: RLC A
    cpu.step()
    if cpu.a != 0x02:
        print(f"FAIL: RLC A expected 0x02, got 0x{cpu.a:02X}")
        exit(1)
        
    # Step 2: SET 7, A
    cpu.step()
    if cpu.a != 0x82:
        print(f"FAIL: SET 7, A expected 0x82, got 0x{cpu.a:02X}")
        exit(1)
        
    # Step 3: BIT 7, A
    cpu.step()
    # Z flag is bit 6 (0x40). If bit 7 is set (it is), Z should be 0.
    if cpu.f & 0x40:
        print("FAIL: BIT 7, A expected Z=0, got Z=1")
        exit(1)
        
    print("PASS: Bit Manipulation verification successful.")

    # Test 7: Extended Instructions (Prefix ED)
    # Zkouška 7: Rozšířené instrukce (předpona ED)
    print("Running manual verification (Extended Instructions)...")
    cpu.pc = 0x8000
    
    # NEG (ED 44)
    # A = 1 -> NEG -> A = 0xFF, S=1, N=1
    cpu.a = 1
    memory.write_byte(0x8000, 0xED)
    memory.write_byte(0x8001, 0x44)
    
    # ADC HL, DE (ED 5A)
    # HL = 0x1000, DE = 0x2000, C=0 -> HL = 0x3000
    memory.write_byte(0x8002, 0xED)
    memory.write_byte(0x8003, 0x5A)
    
    # Step 1: NEG
    cpu.step()
    if cpu.a != 0xFF:
        print(f"FAIL: NEG expected 0xFF, got 0x{cpu.a:02X}")
        exit(1)
        
    # Step 2: ADC HL, DE
    cpu.hl = 0x1000
    cpu.de = 0x2000
    cpu.f = 0 # Clear carry
    cpu.step()
    if cpu.hl != 0x3000:
        print(f"FAIL: ADC HL, DE expected 0x3000, got 0x{cpu.hl:04X}")
        exit(1)

    print("PASS: Extended Instructions verification successful.")

    print("ALL TESTS PASSED.")

if __name__ == "__main__":
    main()
