import unittest
from src.memory import Memory
from src.ula import ULA
from src.io import IOBus

class MockCPU:
    def __init__(self):
        self.cycles = 0

class TestULAAudio(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.ula = ULA(self.memory)
        self.cpu = MockCPU()
        self.ula.set_cpu(self.cpu)
        
    def test_audio_event_recording(self):
        # Initial state Beeper=0
        self.assertEqual(self.ula.beeper, 0)
        
        # Advance time
        self.cpu.cycles = 1000
        # Write Beeper=1 (Bit 4 set)
        # Port 0xFE, Value 0x10 (Bit 4=1)
        self.ula.write_port(0xFE, 0x10)
        
        # Check event
        self.assertEqual(len(self.ula.audio_events), 1)
        cycle, val = self.ula.audio_events[0]
        self.assertEqual(cycle, 1000)
        self.assertEqual(val, 160) # Beeper only = 160
        self.assertEqual(self.ula.beeper, 1)
        
        # Advance time
        self.cpu.cycles = 2000
        # Write Beeper=0
        self.ula.write_port(0xFE, 0x00)
        
        # Check event
        self.assertEqual(len(self.ula.audio_events), 2)
        cycle, val = self.ula.audio_events[1]
        self.assertEqual(cycle, 2000)
        self.assertEqual(val, 40) # Silence = 40

    def test_render_audio_output(self):
        # Initialize render state to silence
        self.ula.render_beeper_state = 40

        # Generate some events
        self.cpu.cycles = 0
        # We need to change state to record an event. 
        # Since we initialized beeper/mic to 0, writing 0x00 won't trigger an event in write_port.
        # But we want to test transitions.
        
        # 35000 cycles (half frame approx) -> High
        self.cpu.cycles = 35000
        self.ula.write_port(0xFE, 0x10) # Beeper=1
        
        # Render frame (70000 cycles total, 10 samples)
        # 1 sample per 7000 cycles
        samples = 10
        total_circles = 70000
        
        buffer = self.ula.render_audio(samples, total_circles)
        
        self.assertEqual(len(buffer), samples)
        
        # First half (0-35000) should be low (40)
        # Samples 0, 1, 2, 3, 4 (Timestamps: 0, 7000, 14000, 21000, 28000)
        for i in range(5):
             self.assertEqual(buffer[i], 40, f"Sample {i} should be low")
             
        # Second half (35000-70000) should be high (160)
        # Samples 5, 6, 7, 8, 9 (Timestamps: 35000, 42000, 49000, 56000, 63000)
        for i in range(5, 10):
            self.assertEqual(buffer[i], 160, f"Sample {i} should be high")

if __name__ == '__main__':
    unittest.main()
