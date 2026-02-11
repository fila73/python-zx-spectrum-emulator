from src.ay38910 import AY38910

class Hardware128K:
    def __init__(self, memory, mixing_mode='mono'):
        """
        128K Spectrum Specific Hardware.
        Handles Memory Paging and AY-3-8910.
        Specifický hardware 128K Spectra.
        Obsluhuje stránkování paměti a AY-3-8910.
        """
        self.memory = memory
        self.ay = AY38910(mixing_mode=mixing_mode)

    @property
    def ay_register(self):
        """Current selected AY register."""
        return self.ay.current_register

    @property
    def ay_registers(self):
        """Reference to AY registers."""
        return self.ay.registers

    def read_port(self, port):
        """
        Read from 128K ports.
        Čtení z portů 128K.
        """
        # AY-3-8910 Register Read (0xFFFD)
        # A15=1, A14=1, A1=0
        if (port & 0xC002) == 0xC000:
            return self.ay.read_data()
            
        return None

    def write_port(self, port, value):
        """
        Write to 128K ports.
        Zápis do portů 128K.
        """
        # Port 0x7FFD (Memory Management)
        # A15=0, A1=0
        if (port & 0x8002) == 0x0000:
            self.memory.write_port_7ffd(value)
            
        # Port 0xFFFD (AY Register Select)
        # A15=1, A14=1, A1=0
        elif (port & 0xC002) == 0xC000:
            self.ay.write_address(value)
            
        # Port 0xBFFD (AY Data Write)
        # A15=1, A14=0, A1=0
        elif (port & 0xC002) == 0x8000:
            self.ay.write_data(value)
