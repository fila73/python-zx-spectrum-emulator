import unittest
from src.cpu import Z80
from src.memory import Memory
from src.io import IOBus

class MockIOBus(IOBus):
    def __init__(self):
        self.last_port_read = None
        self.last_port_write = None
        self.last_val_written = None
        self.ports = {} # Map port -> value for reading

    def read_byte(self, port, cycles=0):
        self.last_port_read = port
        return self.ports.get(port, 0xFF)

    def write_byte(self, port, value):
        self.last_port_write = port
        self.last_val_written = value

class TestCPUIO(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.io_bus = MockIOBus()
        self.cpu = Z80(self.memory, self.io_bus)

    def test_in_a_n(self):
        # IN A, (n) - DB n
        # Read from port (A << 8) | n
        self.cpu.a = 0x12
        self.io_bus.ports[0x1234] = 0xAB
        
        self.memory.write_byte(0x8000, 0xDB)
        self.memory.write_byte(0x8001, 0x34) # n = 0x34
        
        self.cpu.pc = 0x8000
        self.cpu.step()
        
        self.assertEqual(self.cpu.a, 0xAB)
        self.assertEqual(self.io_bus.last_port_read, 0x1234)

    def test_out_n_a(self):
        # OUT (n), A - D3 n
        # Write to port (A << 8) | n
        self.cpu.a = 0x55
        
        self.memory.write_byte(0x8000, 0xD3)
        self.memory.write_byte(0x8001, 0x10) # n = 0x10
        
        self.cpu.pc = 0x8000
        self.cpu.step()
        
        self.assertEqual(self.io_bus.last_port_write, 0x5510)
        self.assertEqual(self.io_bus.last_val_written, 0x55)

        self.assertEqual(self.io_bus.last_val_written, 0x55)

    def test_in_r_c(self):
        # IN B, (C) - ED 40
        # Read from port (B << 8) | C
        self.cpu.b = 0x12
        self.cpu.c = 0x34
        self.io_bus.ports[0x1234] = 0x99
        
        self.memory.write_byte(0x8000, 0xED)
        self.memory.write_byte(0x8001, 0x40)
        
        self.cpu.pc = 0x8000
        self.cpu.step()
        
        self.assertEqual(self.cpu.b, 0x99)
        self.assertEqual(self.io_bus.last_port_read, 0x1234)

    def test_outi(self):
        # OUTI - ED A3
        # Write (HL) to port (B << 8) | C, HL++, B--
        self.cpu.b = 0x05
        self.cpu.c = 0x10
        self.cpu.hl = 0x9000
        self.memory.write_byte(0x9000, 0xDD)
        
        self.memory.write_byte(0x8000, 0xED)
        self.memory.write_byte(0x8001, 0xA3)
        
        self.cpu.pc = 0x8000
        self.cpu.step()
        
        # High byte of port is the NEW value of B (0x04)
        self.assertEqual(self.io_bus.last_port_write, 0x0410)
        self.assertEqual(self.io_bus.last_val_written, 0xDD)
        self.assertEqual(self.cpu.hl, 0x9001)
        self.assertEqual(self.cpu.b, 0x04)

if __name__ == '__main__':
    unittest.main()
