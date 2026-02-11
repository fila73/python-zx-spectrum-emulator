import unittest
from src.cpu import Z80
from src.memory import Memory
from src.io import IOBus

class TestCPUInterrupts(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.io_bus = IOBus()
        self.cpu = Z80(self.memory, self.io_bus)

    def test_interrupt_mode_1_disabled(self):
        self.cpu.iff1 = 0
        self.cpu.pc = 0x8000
        self.cpu.interrupt()
        self.assertEqual(self.cpu.pc, 0x8000) # Should not jump

    def test_interrupt_mode_1_enabled(self):
        self.cpu.iff1 = 1
        self.cpu.iff2 = 1
        self.cpu.pc = 0x8000
        self.cpu.sp = 0xFFFE
        
        self.cpu.interrupt()
        
        # Should jump to 0x0038
        self.assertEqual(self.cpu.pc, 0x0038)
        
        # Should disable interrupts
        self.assertEqual(self.cpu.iff1, 0)
        self.assertEqual(self.cpu.iff2, 0)
        
        # Should push PC to stack
        # SP decremented by 2 -> 0xFFFC
        self.assertEqual(self.cpu.sp, 0xFFFC)
        
        # Stack content should be 0x8000
        low = self.memory.read_byte(0xFFFC)
        high = self.memory.read_byte(0xFFFD)
        val = (high << 8) | low
        self.assertEqual(val, 0x8000)
        
        # Check cycles (13 cycles for RST + 6 cycles for 2x memory write)
        self.assertEqual(self.cpu.cycles, 19)

if __name__ == '__main__':
    unittest.main()
