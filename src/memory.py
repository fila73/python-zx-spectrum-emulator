class Memory:
    def __init__(self, is_128k=False):
        """
        Initialize Memory.
        Inicializace paměti.
        
        :param is_128k: True if 128K model, False for 48K.
        """
        self.is_128k = is_128k
        
        if is_128k:
            # 128K Spectrum has 8 RAM banks of 16K each
            # 128K Spectrum má 8 bank RAM po 16K
            self.ram_banks = [bytearray(16384) for _ in range(8)]
            # 2 ROM banks of 16K each
            # 2 banky ROM po 16K
            self.rom_banks = [bytearray(16384) for _ in range(2)]
            
            # Paging state
            # Stav stránkování
            self.current_ram_bank = 0
            self.current_rom_bank = 0
            self.paging_locked = False
            self.screen_bank = 5 # 5 or 7
        else:
            # 48K Spectrum memory map:
            # 0x0000 - 0x3FFF: 16K ROM
            # 0x4000 - 0xFFFF: 48K RAM
            self.memory = bytearray(65536)

    def read_byte(self, address):
        """
        Read a byte from memory.
        Přečte bajt z paměti.
        """
        address &= 0xFFFF
        
        if not self.is_128k:
            return self.memory[address]
            
        # 128K Paging Logic
        # Logika stránkování 128K
        if address < 0x4000:
            # ROM (Bank 0 or 1)
            return self.rom_banks[self.current_rom_bank][address]
        elif address < 0x8000:
            # RAM Bank 5
            return self.ram_banks[5][address - 0x4000]
        elif address < 0xC000:
            # RAM Bank 2
            return self.ram_banks[2][address - 0x8000]
        else:
            # Bankable RAM (0-7)
            return self.ram_banks[self.current_ram_bank][address - 0xC000]

    def write_byte(self, address, value):
        """
        Write a byte to memory (RAM only).
        Zapíše bajt do paměti (pouze RAM).
        """
        address &= 0xFFFF
        value &= 0xFF
        
        if not self.is_128k:
            # ROM is read-only
            if address < 0x4000:
                return
            self.memory[address] = value
            return
            
        # 128K Paging Logic
        # Logika stránkování 128K
        if address < 0x4000:
            # ROM is read-only
            return
        elif address < 0x8000:
            # RAM Bank 5
            self.ram_banks[5][address - 0x4000] = value
        elif address < 0xC000:
            # RAM Bank 2
            self.ram_banks[2][address - 0x8000] = value
        else:
            # Bankable RAM (0-7)
            self.ram_banks[self.current_ram_bank][address - 0xC000] = value

    def load_rom(self, data, bank=0):
        """
        Load ROM data into memory.
        Nahraje data ROM do paměti.
        """
        if self.is_128k:
            if len(data) > 16384:
                raise ValueError("ROM data too large for 16K ROM bank")
            self.rom_banks[bank][0:len(data)] = data
        else:
            if len(data) > 0x4000:
                raise ValueError("ROM data too large for 16K ROM space")
            self.memory[0:len(data)] = data

    def read_word(self, address):
        """
        Read a 16-bit word from memory (little-endian).
        Přečte 16bitové slovo z paměti (little-endian).
        """
        low = self.read_byte(address)
        high = self.read_byte(address + 1)
        return (high << 8) | low

    def write_word(self, address, value):
        """
        Write a 16-bit word to memory (little-endian).
        Zapíše 16bitové slovo do paměti (little-endian).
        """
        self.write_byte(address, value & 0xFF)
        self.write_byte(address + 1, (value >> 8) & 0xFF)

    def write_port_7ffd(self, value):
        """
        Handle write to port 0x7FFD (Memory Management).
        Obsluha zápisu na port 0x7FFD (Správa paměti).
        """
        if not self.is_128k or self.paging_locked:
            return
            
        # Bit 0-2: RAM bank for 0xC000 - 0xFFFF
        self.current_ram_bank = value & 0x07
        
        # Bit 3: Shadow screen selection (0=Bank 5, 1=Bank 7)
        self.screen_bank = 7 if (value & 0x08) else 5
        
        # Bit 4: ROM selection (0=ROM 0, 1=ROM 1)
        self.current_rom_bank = (value >> 4) & 0x01
        
        # Bit 5: Lock 128k paging
        if value & 0x20:
            self.paging_locked = True

    def get_bank_data(self, bank):
        """
        Get reference to a RAM bank data.
        Získat odkaz na data RAM banky.
        """
        if not self.is_128k:
            if bank == 0: return self.memory[0x0000:0x4000] # ROM
            if bank == 5: return self.memory[0x4000:0x8000]
            if bank == 2: return self.memory[0x8000:0xC000]
            return self.memory[0xC000:0x10000] # Current high bank
            
        return self.ram_banks[bank]