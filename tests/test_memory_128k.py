import pytest
from src.memory import Memory
from src.hardware_128k import Hardware128K

def test_128k_paging_defaults():
    mem = Memory(is_128k=True)
    assert mem.current_ram_bank == 0
    assert mem.current_rom_bank == 0
    assert mem.screen_bank == 5
    assert mem.paging_locked == False

def test_128k_paging_ram_banks():
    mem = Memory(is_128k=True)
    hw = Hardware128K(mem)
    
    # Write to bank 0 (default at 0xC000)
    mem.write_byte(0xC000, 0x42)
    assert mem.read_byte(0xC000) == 0x42
    assert mem.ram_banks[0][0] == 0x42
    
    # Switch to bank 1
    hw.write_port(0x7FFD, 1)
    assert mem.current_ram_bank == 1
    assert mem.read_byte(0xC000) == 0x00 # Should be empty bank 1
    
    # Write to bank 1
    mem.write_byte(0xC000, 0x13)
    assert mem.read_byte(0xC000) == 0x13
    assert mem.ram_banks[1][0] == 0x13
    
    # Switch back to bank 0
    hw.write_port(0x7FFD, 0)
    assert mem.read_byte(0xC000) == 0x42

def test_128k_paging_rom_banks():
    mem = Memory(is_128k=True)
    hw = Hardware128K(mem)
    
    mem.load_rom(bytes([0x01]), bank=0)
    mem.load_rom(bytes([0x02]), bank=1)
    
    # Default ROM 0
    assert mem.read_byte(0x0000) == 0x01
    
    # Switch to ROM 1
    hw.write_port(0x7FFD, 0x08) # Bit 3 set
    assert mem.current_rom_bank == 1
    assert mem.read_byte(0x0000) == 0x02
    
    # Switch back to ROM 0
    hw.write_port(0x7FFD, 0x00)
    assert mem.read_byte(0x0000) == 0x01

def test_128k_paging_lock():
    mem = Memory(is_128k=True)
    hw = Hardware128K(mem)
    
    # Switch to bank 1 and lock
    hw.write_port(0x7FFD, 0x20 | 1) # Bit 5 (lock) and bit 0 (bank 1)
    assert mem.current_ram_bank == 1
    assert mem.paging_locked == True
    
    # Try to switch back to bank 0
    hw.write_port(0x7FFD, 0)
    assert mem.current_ram_bank == 1 # Still bank 1
    assert mem.paging_locked == True

def test_128k_fixed_banks():
    mem = Memory(is_128k=True)
    
    # Bank 5 at 0x4000
    mem.ram_banks[5][0] = 0x55
    assert mem.read_byte(0x4000) == 0x55
    
    # Bank 2 at 0x8000
    mem.ram_banks[2][0] = 0x22
    assert mem.read_byte(0x8000) == 0x22
    
    # Even if we change 0xC000 bank, 0x4000 and 0x8000 stay the same
    mem.write_port_7ffd(1)
    assert mem.read_byte(0x4000) == 0x55
    assert mem.read_byte(0x8000) == 0x22

def test_ay_registers():
    mem = Memory(is_128k=True)
    hw = Hardware128K(mem)
    
    # Select AY register 7
    hw.write_port(0xFFFD, 7)
    assert hw.ay_register == 7
    
    # Write value to AY register 7
    hw.write_port(0xBFFD, 0xFE)
    assert hw.ay_registers[7] == 0xFE
    
    # Read value from AY register 7
    assert hw.read_port(0xFFFD) == 0xFE
