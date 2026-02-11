import unittest
from src.memory import Memory
from src.ula import ULA
from src.cpu import Z80
from src.io import IOBus

class TestContention(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.ula = ULA(self.memory)
        self.cpu = Z80(self.memory)
        self.cpu.ula = self.ula
        self.ula.set_cpu(self.cpu)
        
    def test_no_contention_rom(self):
        # ROM (0x0000) is not contended
        # ROM (0x0000) není zatížena kolizemi
        self.cpu.cycles = 14336 # Screen start
        self.cpu.read_byte(0x0000)
        # Should take exactly 3 cycles
        self.assertEqual(self.cpu.cycles, 14336 + 3)

    def test_no_contention_upper_ram(self):
        # RAM 0x8000+ is not contended
        # RAM 0x8000+ není zatížena kolizemi
        self.cpu.cycles = 14336
        self.cpu.read_byte(0x8000)
        self.assertEqual(self.cpu.cycles, 14336 + 3)

    def test_contention_at_screen_start(self):
        # RAM 0x4000 is contended
        # RAM 0x4000 je zatížena kolizemi
        # Cycle 14336 is the start of the screen area
        self.cpu.cycles = 14336
        self.cpu.read_byte(0x4000)
        # Expected: 6 (contention) + 3 (read) = 9
        self.assertEqual(self.cpu.cycles, 14336 + 6 + 3)

    def test_contention_pattern(self):
        # Test the 6, 5, 4, 3, 2, 1, 0, 0 pattern
        # Testování vzorce 6, 5, 4, 3, 2, 1, 0, 0
        expected_delays = [6, 5, 4, 3, 2, 1, 0, 0]
        for i in range(8):
            self.cpu.cycles = 14336 + i
            # We need to measure the INCREASE, so we don't just use read_byte which adds 3
            delay = self.ula.get_contention(self.cpu.cycles, 0x4000)
            self.assertEqual(delay, expected_delays[i], f"Failed at offset {i}")

    def test_floating_bus_bitmap(self):
        # At cycle 14336, ULA fetches bitmap for (0,0) -> 0x4000
        # V taktu 14336 ULA načítá bitmapu pro (0,0) -> 0x4000
        self.memory.write_byte(0x4000, 0xA5)
        io_bus = IOBus()
        io_bus.add_device(self.ula)
        
        # Read from unattached port at cycle 14336
        val = io_bus.read_byte(0xFFFF, 14336)
        self.assertEqual(val, 0xA5)

    def test_floating_bus_attribute(self):
        # At cycle 14337, ULA fetches attribute for (0,0) -> 0x5800
        # V taktu 14337 ULA načítá atribut pro (0,0) -> 0x5800
        self.memory.write_byte(0x5800, 0x42)
        io_bus = IOBus()
        io_bus.add_device(self.ula)
        
        # Read from unattached port at cycle 14337
        val = io_bus.read_byte(0xFFFF, 14337)
        self.assertEqual(val, 0x42)

    def test_floating_bus_idle(self):
        # At cycle 14338, ULA is idle (cycles 2 and 3 of the 4-cycle fetch)
        # V taktu 14338 je ULA nečinná
        io_bus = IOBus()
        io_bus.add_device(self.ula)
        
        val = io_bus.read_byte(0xFFFF, 14338)
        self.assertEqual(val, 0xFF)

    def test_border_per_line(self):
        # Set border color 1 (Blue) at start
        # Nastavení barvy okraje 1 (modrá) na začátku
        self.cpu.cycles = 0
        self.ula.write_port(0xFE, 1)
        
        # Set border color 2 (Red) at line 100
        # Nastavení barvy okraje 2 (červená) na řádku 100
        self.cpu.cycles = 224 * 100
        self.ula.write_port(0xFE, 2)
        
        buffer = self.ula.render_screen()
        
        # Line 50 should be color 1 (Blue)
        # Řádek 50 by měl mít barvu 1 (modrá)
        pixel50 = buffer[50, 0]
        self.assertEqual(tuple(pixel50), self.ula.palette[1])
        
        # Line 150 should be color 2 (Red)
        # Řádek 150 by měl mít barvu 2 (červená)
        pixel150 = buffer[150, 0]
        self.assertEqual(tuple(pixel150), self.ula.palette[2])

    def test_io_contention_ula_port(self):
        # Even ports (bit 0 = 0) are contended
        # Port 0xFE is contended
        self.cpu.cycles = 14336
        # get_contention for I/O should check 4 cycles
        # Because each cycle is delayed, the subsequent cycles "skip" some contention states.
        # Cycle 0: delay 6 -> next at 7
        # Cycle 7: delay 0 -> next at 8 (0)
        # Cycle 0: delay 6 -> next at 7
        # Cycle 7: delay 0
        # Total: 6 + 0 + 6 + 0 = 12
        delay = self.ula.get_contention(14336, 0x00FE, is_io=True)
        self.assertEqual(delay, 12)

    def test_io_contention_ram_port(self):
        # Port in 0x4000-0x7FFF range is contended even if bit 0 = 1
        self.cpu.cycles = 14336
        delay = self.ula.get_contention(14336, 0x4001, is_io=True)
        self.assertEqual(delay, 12)

if __name__ == '__main__':
    unittest.main()
