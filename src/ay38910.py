import numpy as np

class AY38910:
    def __init__(self, clock_hz=1773400, mixing_mode='mono'):
        """
        AY-3-8910 Programmable Sound Generator (PSG).
        Programmable Sound Generator (PSG) AY-3-8910.
        
        :param clock_hz: Input clock frequency. For Spectrum 128K it's ~1.7734 MHz.
        :param mixing_mode: 'mono', 'abc', or 'acb'.
        """
        self.clock_hz = clock_hz
        self.mixing_mode = mixing_mode.lower()
        # PSG internal clock is input clock / 16
        self.psg_clock_hz = clock_hz / 16.0
        
        self.registers = [0] * 16
        self.current_register = 0
        
        # Channel state
        self.tone_counters = [0, 0, 0] # 12-bit counters
        self.tone_states = [1, 1, 1] # 1 or 0 (square wave)
        
        # Noise state
        self.noise_counter = 0
        self.noise_rng = 1 # 17-bit LFSR
        self.noise_state = 1
        
        # Envelope state
        self.envelope_counter = 0
        self.envelope_step = 15
        self.envelope_holding = False
        self.envelope_idle = True
        
        # Logarithmic volume table (AY-3-8910 is known for this)
        # Using a standard table for PSG
        self.vol_table = np.array([
            0.0, 0.007, 0.010, 0.014, 0.021, 0.030, 0.041, 0.062,
            0.081, 0.122, 0.170, 0.245, 0.334, 0.480, 0.655, 1.0
        ], dtype=np.float32)
        
        # For sample accumulation
        self.psg_ticks_remainder = 0.0

    def write_address(self, value):
        """
        Select the current register.
        Vybrat aktuální registr.
        """
        self.current_register = value & 0x0F

    def write_data(self, value):
        """
        Write data to the current register.
        Zapsat data do aktuálního registru.
        """
        self.registers[self.current_register] = value
        
        if self.current_register == 13:
            # Reset envelope
            self.envelope_counter = 0
            self.envelope_step = 15
            self.envelope_holding = False
            self.envelope_idle = False

    def read_data(self):
        """
        Read data from the current register.
        Přečíst data z aktuálního registru.
        """
        # Registers 14 and 15 are I/O, we'll return 0xFF for now
        if self.current_register >= 14:
            return 0xFF
        return self.registers[self.current_register]

    def render_audio(self, num_samples, sample_rate):
        """
        Generate AY-3-8910 audio samples.
        Generovat audio vzorky AY-3-8910.
        
        :param num_samples: Number of samples to generate.
        :param sample_rate: Output sample rate (Hz).
        :return: numpy array of floats (num_samples, 2) for stereo or (num_samples,) for mono.
        """
        is_stereo = self.mixing_mode in ['abc', 'acb']
        if is_stereo:
            samples = np.zeros((num_samples, 2), dtype=np.float32)
        else:
            samples = np.zeros(num_samples, dtype=np.float32)
        
        # PSG ticks per output sample
        psg_ticks_per_sample = self.psg_clock_hz / sample_rate
        
        period_a = ((self.registers[1] & 0x0F) << 8) | self.registers[0]
        period_b = ((self.registers[3] & 0x0F) << 8) | self.registers[2]
        period_c = ((self.registers[5] & 0x0F) << 8) | self.registers[4]
        periods = [period_a, period_b, period_c]
        
        mixer = self.registers[7]
        noise_period = self.registers[6] & 0x1F
        env_period = (self.registers[12] << 8) | self.registers[11]
        env_shape = self.registers[13] & 0x0F
        
        if not hasattr(self, 'env_direction'):
            self.env_direction = 1 if (env_shape & 0x04) else -1

        for i in range(num_samples):
            self.psg_ticks_remainder += psg_ticks_per_sample
            num_ticks = int(self.psg_ticks_remainder)
            self.psg_ticks_remainder -= num_ticks
            
            if num_ticks > 0:
                for _ in range(num_ticks):
                    self._step_psg(periods, noise_period, env_period, env_shape)
            
            env_val = self.envelope_step
            channel_outputs = [0.0, 0.0, 0.0]
            
            for chan in range(3):
                tone_out = self.tone_states[chan] if not (mixer & (1 << chan)) else 1
                noise_out = self.noise_state if not (mixer & (1 << (chan + 3))) else 1
                
                if tone_out and noise_out:
                    amp_reg = self.registers[8 + chan]
                    if amp_reg & 0x10: # Envelope
                        channel_outputs[chan] = self.vol_table[env_val]
                    else:
                        channel_outputs[chan] = self.vol_table[amp_reg & 0x0F]
            
            # Mixing
            if is_stereo:
                if self.mixing_mode == 'abc':
                    # ABC: A=L, B=L+R, C=R
                    samples[i, 0] = (channel_outputs[0] + channel_outputs[1] * 0.7) / 1.7
                    samples[i, 1] = (channel_outputs[2] + channel_outputs[1] * 0.7) / 1.7
                elif self.mixing_mode == 'acb':
                    # ACB: A=L, C=L+R, B=R
                    samples[i, 0] = (channel_outputs[0] + channel_outputs[2] * 0.7) / 1.7
                    samples[i, 1] = (channel_outputs[1] + channel_outputs[2] * 0.7) / 1.7
            else:
                # Mono
                samples[i] = (channel_outputs[0] + channel_outputs[1] + channel_outputs[2]) / 3.0
            
        return samples

    def _step_psg(self, periods, noise_period, env_period, env_shape):
        """Step the internal PSG state by one PSG clock tick."""
        # Update Tones
        for chan in range(3):
            p = periods[chan]
            if p == 0: p = 1
            self.tone_counters[chan] += 1
            if self.tone_counters[chan] >= p:
                self.tone_counters[chan] = 0
                self.tone_states[chan] ^= 1
                
        # Update Noise
        n_p = noise_period
        if n_p == 0: n_p = 1
        self.noise_counter += 1
        if self.noise_counter >= n_p:
            self.noise_counter = 0
            feedback = (self.noise_rng ^ (self.noise_rng >> 3)) & 1
            self.noise_rng = (self.noise_rng >> 1) | (feedback << 16)
            self.noise_state = self.noise_rng & 1
            
        # Update Envelope
        if not self.envelope_idle:
            e_p = env_period
            if e_p == 0: e_p = 1
            self.envelope_counter += 1
            if self.envelope_counter >= (e_p * 16):
                self.envelope_counter = 0
                self._step_envelope(env_shape)

    def _step_envelope(self, shape):
        """Step the envelope generator."""
        if self.envelope_holding:
            return

        # Bits: 3: Continue, 2: Attack, 1: Alternate, 0: Hold
        cont = (shape >> 3) & 1
        attack = (shape >> 2) & 1
        alt = (shape >> 1) & 1
        hold = (shape >> 0) & 1

        if not hasattr(self, 'env_direction'):
            self.env_direction = 1 if attack else -1

        self.envelope_step += self.env_direction

        if self.envelope_step < 0 or self.envelope_step > 15:
            if not cont:
                # 00xx shapes: One cycle then 0
                self.envelope_step = 0
                self.envelope_holding = True
            else:
                if hold:
                    # 1x01 or 1x11 shapes
                    if alt:
                        # 1011: \¯¯¯ (Decay then 15), 1111: /___ (Attack then 0)
                        # Actually:
                        # 1011: \ followed by hold at 15
                        # 1111: / followed by hold at 0
                        # Wait, bit 0 is hold. 
                        # Shape 11 (1011) is Decay, Alternate, Hold. 
                        # Decay (15->0), then alternate (Attack 0->15), then hold at 15.
                        # Shape 15 (1111) is Attack, Alternate, Hold.
                        # Attack (0->15), then alternate (Decay 15->0), then hold at 0.
                        if self.env_direction == 1:
                                # We were attacking, now hold at 0? No, hold at end of alternate.
                                # This is getting complex. Let's use a simpler state machine.
                                self.envelope_step = 0
                                self.envelope_holding = True
                        else:
                                self.envelope_step = 15
                                self.envelope_holding = True
                    else:
                        # 1001: \___ (Hold 0), 1101: /¯¯¯ (Hold 15)
                        self.envelope_step = 15 if (self.env_direction == 1) else 0
                        self.envelope_holding = True
                else:
                    if alt:
                        # Triangle repeat
                        if self.env_direction == 1:
                            self.envelope_step = 15
                            self.env_direction = -1
                        else:
                            self.envelope_step = 0
                            self.env_direction = 1
                    else:
                        # Sawtooth repeat
                        self.envelope_step = 0 if attack else 15

    