import unittest
import struct
from src.cpu import Z80
from src.memory import Memory
from src.tape import Tape

class MockIOBus:
    pass

class TestTape(unittest.TestCase):
    def setUp(self):
        self.tape = Tape()
        self.memory = Memory()
        self.cpu = Z80(self.memory, MockIOBus())
        self.cpu.tape = self.tape

    def create_dummy_tap(self, filename):
        # Create a valid TAP file structure
        # Block 1: Header (19 bytes: Flag(1) + Type(1) + Name(10) + Len(2) + Param1(2) + Param2(2) + Checksum(1))
        # Total Length = 19. Block Data = 2 bytes (Len) + 19 bytes.
        
        # Header Data: 
        # Flag: 0x00 (Header)
        # Type: 0x00 (Program)
        # Name: "TEST      "
        # Len: 10 bytes
        # Start: 0
        # Vars: 0
        # Checksum: XOR of all bytes including Flag
        
        header_payload = bytearray([0x00, 0x00]) + b"TEST      " + struct.pack('<H', 10) + struct.pack('<H', 0) + struct.pack('<H', 0)
        checksum = 0
        for b in header_payload:
            checksum ^= b
        header_payload.append(checksum)
        
        # 2-byte Length prefix for Header block
        header_block = struct.pack('<H', len(header_payload)) + header_payload
        
        # Block 2: Data (12 bytes: Flag(1) + 10 bytes data + Checksum(1))
        data_payload = bytearray([0xFF]) + b"0123456789"
        checksum = 0
        for b in data_payload:
            checksum ^= b
        data_payload.append(checksum)
        
        # 2-byte Length prefix for Data block
        data_block = struct.pack('<H', len(data_payload)) + data_payload
        
        with open(filename, 'wb') as f:
            f.write(header_block)
            f.write(data_block)
            
    def test_load_and_parse_tap(self):
        filename = "test.tap"
        self.create_dummy_tap(filename)
        
        success = self.tape.load_file(filename)
        self.assertTrue(success)
        self.assertEqual(len(self.tape.blocks), 2)
        
        # Check Header Block
        # First 2 bytes are length in file, but Tape.blocks stores just the block data (Flag+Data+Checksum)
        block1 = self.tape.get_next_block()
        self.assertEqual(block1[0], 0x00) # Flag
        self.assertEqual(len(block1), 19)
        
        # Check Data Block
        block2 = self.tape.get_next_block()
        self.assertEqual(block2[0], 0xFF) # Flag
        self.assertEqual(len(block2), 12)
        self.assertEqual(block2[1:11], b"0123456789")

    def test_cpu_trap_header(self):
        # Test loading the Header block via CPU trap
        filename = "test_trap.tap"
        self.create_dummy_tap(filename)
        self.tape.load_file(filename)
        
        # Setup CPU for Header Loading
        # Routine 0x0556 roughly:
        # Expected Flag in A (0x00)
        # IX = Address (0x4000 for verification usually, but let's say 0x8000)
        # DE = Length (17 bytes for header payload excl flag/checksum? No, usually loads 17 bytes)
        
        self.cpu.a = 0x00 # Expecting Header
        self.cpu.ix = 0x8000
        self.cpu.de = 17 # Header data length
        
        # Trigger Trap
        self.cpu.pc = 0x0556
        handled = self.cpu.check_traps()
        self.assertTrue(handled)
        
        # Verify Memory
        # The trap writes data starting at IX.
        # It skips the Flag byte (index 0).
        # It writes DE bytes.
        
        # Block: [00, 00, T, E, S, T ... ]
        # Memory[8000] should be 00 (Type)
        # Memory[8001] should be 'T'
        
        val = self.memory.read_byte(0x8000)
        self.assertEqual(val, 0x00)
        
        val = self.memory.read_byte(0x8001)
        self.assertEqual(val, ord('T'))
        
        # Verify Carry Flag set (Success)
        self.assertTrue(self.cpu.f & 0x01)

    def test_cpu_trap_data(self):
        # Skip header
        filename = "test_trap_data.tap"
        self.create_dummy_tap(filename)
        self.tape.load_file(filename)
        self.tape.get_next_block() # Consume Header
        
        # Load Data Block
        self.cpu.a = 0xFF # Expecting Data
        self.cpu.ix = 0x9000
        self.cpu.de = 10 # Data length
        
        self.cpu.pc = 0x0556
        handled = self.cpu.check_traps()
        self.assertTrue(handled)
        
        # Verify Data
        # Block: [FF, '0', '1' ... ]
        # Memory[9000] should be '0'
        
        for i in range(10):
            val = self.memory.read_byte(0x9000 + i)
            self.assertEqual(val, ord(str(i)))
            
        self.assertTrue(self.cpu.f & 0x01)

if __name__ == '__main__':
    unittest.main()
