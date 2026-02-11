import miniaudio
import numpy as np
import threading
import sys

class AudioEngine:
    def __init__(self, sample_rate=44100, buffer_size=4096):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        
        # Ring Buffer
        # 2 channels (Stereo)
        self.ring_buffer = np.zeros((buffer_size, 2), dtype=np.float32)
        self.write_index = 0
        self.read_index = 0
        self.buffer_lock = threading.Lock()
        
        # Underrun/Overrun stats
        self.underruns = 0
        self.overruns = 0
        
        self.device = None
        self.is_running = False

    def start(self):
        if self.is_running:
            return

        try:
            self.device = miniaudio.PlaybackDevice(
                output_format=miniaudio.SampleFormat.FLOAT32,
                nchannels=2,
                sample_rate=self.sample_rate,
                buffersize_msec=50
            )
            # We must pass the generator object, so we call the method
            self._gen = self._generator()
            next(self._gen) # Prime the generator
            self.device.start(self._gen)
            self.is_running = True
            print(f"DEBUG: AudioEngine started (miniaudio). SR={self.sample_rate}", file=sys.stderr)
        except Exception as e:
            print(f"DEBUG: AudioEngine start failed: {e}", file=sys.stderr)

    def stop(self):
        if not self.is_running:
            return
            
        if self.device:
            self.device.close()
            self.device = None
        self.is_running = False
        print("DEBUG: AudioEngine stopped.", file=sys.stderr)

    def add_samples(self, samples):
        """
        Add samples to the ring buffer.
        samples: numpy array of shape (N, 2) or (N,) dtype float32
        """
        if not self.is_running:
            return

        num_samples = len(samples)
        if num_samples == 0:
            return
            
        # Ensure stereo
        if samples.ndim == 1:
            # Expand mono to stereo
            stereo_samples = np.column_stack((samples, samples))
        else:
            stereo_samples = samples

        with self.buffer_lock:
            space_avail = self.buffer_size - (self.write_index - self.read_index)
            
            if space_avail < num_samples:
                self.overruns += 1
                to_write = space_avail
            else:
                to_write = num_samples
                
            if to_write == 0:
                return

            end_idx = self.write_index + to_write
            idx_start = self.write_index % self.buffer_size
            idx_end = end_idx % self.buffer_size
            
            if idx_end > idx_start:
                self.ring_buffer[idx_start:idx_end] = stereo_samples[:to_write]
            else:
                part1_len = self.buffer_size - idx_start
                self.ring_buffer[idx_start:] = stereo_samples[:part1_len]
                self.ring_buffer[:idx_end] = stereo_samples[part1_len:to_write]
                
            self.write_index += to_write

    def _generator(self):
        """
        miniaudio generator.
        Yields audio data.
        """
        required_frames = yield b"" # Initial yield to receive first request
        
        while True:
            # required_frames is sent by miniaudio
            with self.buffer_lock:
                available = self.write_index - self.read_index
                
                to_read = min(available, required_frames)
                
                output = np.zeros((required_frames, 2), dtype=np.float32)
                
                if to_read > 0:
                    end_idx = self.read_index + to_read
                    idx_start = self.read_index % self.buffer_size
                    idx_end = end_idx % self.buffer_size
                    
                    if idx_end > idx_start:
                        output[:to_read] = self.ring_buffer[idx_start:idx_end]
                    else:
                        part1_len = self.buffer_size - idx_start
                        output[:part1_len] = self.ring_buffer[idx_start:]
                        output[part1_len:to_read] = self.ring_buffer[:idx_end]
                    
                    self.read_index += to_read
                
                if to_read < required_frames:
                    self.underruns += 1
                    # Already zeros, effectively silence
            
            required_frames = yield output.tobytes()
