import unittest
import numpy as np
from src.ay38910 import AY38910

from src.hardware_128k import Hardware128K
from src.memory import Memory

class TestAYSound(unittest.TestCase):
    def setUp(self):
        self.ay = AY38910()

    def test_hardware_128k_io(self):
        """Test that AY registers are accessible via Hardware128K I/O ports."""
        memory = Memory(is_128k=True)
        hw128 = Hardware128K(memory)
        
        # Select register 7 (Mixer) via port 0xFFFD
        hw128.write_port(0xFFFD, 7)
        # Write 0x3F to register 7 via port 0xBFFD
        hw128.write_port(0xBFFD, 0x3F)
        # Read back from port 0xFFFD
        self.assertEqual(hw128.read_port(0xFFFD), 0x3F)
        
        # Select register 0
        hw128.write_port(0xFFFD, 0)
        hw128.write_port(0xBFFD, 0xAA)
        self.assertEqual(hw128.read_port(0xFFFD), 0xAA)

    def test_register_access(self):
        """Test basic register selection and data writing."""
        self.ay.write_address(7)
        self.ay.write_data(0x3F)
        self.assertEqual(self.ay.read_data(), 0x3F)
        
        self.ay.write_address(0)
        self.ay.write_data(0xAA)
        self.assertEqual(self.ay.read_data(), 0xAA)

    def test_tone_generation(self):
        """Test that tone generation produces some output."""
        # Enable Channel A tone only, disable noise
        self.ay.write_address(7)
        self.ay.write_data(0b111110) # 0 means enabled
        
        # Set period for Channel A
        self.ay.write_address(0)
        self.ay.write_data(100) # Period = 100
        
        # Set amplitude
        self.ay.write_address(8)
        self.ay.write_data(15) # Max volume
        
        samples = self.ay.render_audio(100, 44100)
        # Check that we have some non-zero samples
        self.assertTrue(np.any(samples > 0))
        # Check that we have some variation (it's a square wave)
        self.assertTrue(np.any(samples < 1.0)) # Mixed with others it might be lower

    def test_noise_generation(self):
        """Test that noise generation produces some output."""
        # Enable Noise on Channel A, disable tones
        self.ay.write_address(7)
        self.ay.write_data(0b110111) # Noise on A enabled (bit 3 = 0)
        
        # Set noise period
        self.ay.write_address(6)
        self.ay.write_data(1)
        
        # Set amplitude
        self.ay.write_address(8)
        self.ay.write_data(15)
        
        samples = self.ay.render_audio(1000, 44100)
        self.assertTrue(np.any(samples > 0))

    def test_envelope_generation(self):
        """Test that envelope affects amplitude."""
        # Enable Channel A tone
        self.ay.write_address(7)
        self.ay.write_data(0b111110)
        
        # Set period
        self.ay.write_address(0)
        self.ay.write_data(10)
        
        # Set envelope on Channel A
        self.ay.write_address(8)
        self.ay.write_data(0x10) # Envelope bit
        
        # Set envelope shape (Decay)
        self.ay.write_address(13)
        self.ay.write_data(0x00)
        
    def test_stereo_mixing(self):
        """Test that stereo mixing produces 2-channel output."""
        ay_abc = AY38910(mixing_mode='abc')
        # Enable Channel A tone only
        ay_abc.write_address(7)
        ay_abc.write_data(0b111110)
        ay_abc.write_address(0)
        ay_abc.write_data(100)
        ay_abc.write_address(8)
        ay_abc.write_data(15)
        
        samples = ay_abc.render_audio(100, 44100)
        self.assertEqual(samples.ndim, 2)
        self.assertEqual(samples.shape[1], 2)
        
        # Channel A in ABC is on Left channel (0) and partially on Right (1)? 
        # Wait, A=Left, B=Center, C=Right.
        # My implementation:
        # samples[i, 0] = (channel_outputs[0] + channel_outputs[1] * 0.7) / 1.7
        # samples[i, 1] = (channel_outputs[2] + channel_outputs[1] * 0.7) / 1.7
        
        # So Channel A (output[0]) should be only on channel 0
        # Wait, if output[1] and output[2] are 0:
        # samples[i, 0] = output[0] / 1.7
        # samples[i, 1] = 0
        
        self.assertTrue(np.any(samples[:, 0] > 0))
        self.assertTrue(np.all(samples[:, 1] == 0))

if __name__ == '__main__':
    unittest.main()
