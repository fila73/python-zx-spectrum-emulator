class Memory:
    def __init__(self, model="48K"):
        """
        Initialize Memory.
        Inicializace paměti pro různé modely (16K, 48K, 128K, +2, +3, ZX80, ZX81).
        """
        self.model = model.upper()
        self.is_128k = self.model in ["128K", "+2"]
        self.is_plus3 = self.model == "+3"
        self.is_zx80 = self.model == "ZX80"
        self.is_zx81 = self.model == "ZX81"
        self.is_16k = self.model == "16K"
        
        self.paging_locked = False
        self.screen_bank = 5 # 5 or 7
        
        if self.is_plus3:
            self.ram_banks = [bytearray(16384) for _ in range(8)]
            self.rom_banks = [bytearray(16384) for _ in range(4)]
            self.current_ram_bank = 0
            self.current_rom_bank = 0
            self.special_paging = False
            self.special_mapping = 0
            
        elif self.is_128k:
            self.ram_banks = [bytearray(16384) for _ in range(8)]
            self.rom_banks = [bytearray(16384) for _ in range(2)]
            self.current_ram_bank = 0
            self.current_rom_bank = 0
            
        else:
            self.memory = bytearray(65536)

    def read_byte(self, address):
        address &= 0xFFFF
        
        if self.is_zx80 or self.is_zx81:
            # Echo paměti neřešíme do detailu, omezíme rozsah
            # ROM do 0x1FFF, (ZX81 až do 0x3FFF s tiskovou rutinou, standardně 8K zrcadlených)
            if self.is_zx80 and address >= 0x1000 and address < 0x4000:
                address &= 0x0FFF # 4K ROM mirrored
            elif self.is_zx81 and address >= 0x2000 and address < 0x4000:
                address &= 0x1FFF # 8K ROM mirrored
                
            if address >= 0x4000 and address < 0x8000:
                # 16K RAM na 0x4000
                return self.memory[address]
            elif address < 0x4000:
                # ROM na 0x0000
                return self.memory[address]
            else:
                # Kód mimo RAM/ROM u ZX80 vrací nesmysly, často mirrorované, neřešíme (0xFF)
                return 0xFF
                
        elif self.is_16k:
            if address >= 0x8000:
                return 0xFF
            return self.memory[address]
            
        elif not (self.is_128k or self.is_plus3):
            # 48K
            return self.memory[address]
            
        # 128K a +3 Logika stránkování
        if self.is_plus3 and self.special_paging:
            # +3 Speciální uspořádání čisté RAM (0000-FFFF)
            # config: 0 -> 0,1,2,3 | 1 -> 4,5,6,7 | 2 -> 4,7,6,3 | 3 -> 4,3,6,7
            bank_map = (
                (0, 1, 2, 3),
                (4, 5, 6, 7),
                (4, 7, 6, 3),
                (4, 3, 6, 7)
            )[self.special_mapping]
            
            bank_idx = address >> 14
            return self.ram_banks[bank_map[bank_idx]][address & 0x3FFF]
            
        else:
            if address < 0x4000:
                # ROM
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
        address &= 0xFFFF
        value &= 0xFF
        
        if self.is_zx80 or self.is_zx81:
            if address >= 0x4000 and address < 0x8000:
                self.memory[address] = value
            return
            
        elif self.is_16k:
            if address >= 0x4000 and address < 0x8000:
                self.memory[address] = value
            return
            
        elif not (self.is_128k or self.is_plus3):
            if address >= 0x4000:
                self.memory[address] = value
            return
            
        # 128K a +3 Logika stránkování
        if self.is_plus3 and self.special_paging:
            bank_map = (
                (0, 1, 2, 3),
                (4, 5, 6, 7),
                (4, 7, 6, 3),
                (4, 3, 6, 7)
            )[self.special_mapping]
            
            bank_idx = address >> 14
            self.ram_banks[bank_map[bank_idx]][address & 0x3FFF] = value
        else:
            if address < 0x4000:
                # ROM is read-only
                return
            elif address < 0x8000:
                self.ram_banks[5][address - 0x4000] = value
            elif address < 0xC000:
                self.ram_banks[2][address - 0x8000] = value
            else:
                self.ram_banks[self.current_ram_bank][address - 0xC000] = value

    def load_rom(self, data, bank=0):
        if self.is_plus3:
            if len(data) > 16384:
                raise ValueError("ROM data too large for 16K ROM bank")
            self.rom_banks[bank][0:len(data)] = data
        elif self.is_128k:
            if len(data) > 16384:
                raise ValueError("ROM data too large for 16K ROM bank")
            self.rom_banks[bank][0:len(data)] = data
        else:
            # 16K, 48K, ZX80, ZX81
            if len(data) > 0x4000:
                raise ValueError("ROM data too large for 16K ROM space")
            self.memory[0:len(data)] = data

    def read_word(self, address):
        low = self.read_byte(address)
        high = self.read_byte(address + 1)
        return (high << 8) | low

    def write_word(self, address, value):
        self.write_byte(address, value & 0xFF)
        self.write_byte(address + 1, (value >> 8) & 0xFF)

    def write_port_7ffd(self, value):
        if not (self.is_128k or self.is_plus3) or self.paging_locked:
            return
            
        self.current_ram_bank = value & 0x07
        self.screen_bank = 7 if (value & 0x08) else 5
        
        # Složení ROM banky - u 128K je 1 bit, u +3 se sčítá s 1FFD
        rom_bit_0 = (value >> 4) & 0x01
        if self.is_plus3:
            rom_bit_1 = self.current_rom_bank >> 1  # zachováme bit z 1FFD
            self.current_rom_bank = (rom_bit_1 << 1) | rom_bit_0
        else:
            self.current_rom_bank = rom_bit_0
            
        if value & 0x20:
            self.paging_locked = True

    def write_port_1ffd(self, value):
        if not self.is_plus3 or self.paging_locked:
            return
            
        # Paging Mode (0 = Normal, 1 = Special)
        self.special_paging = bool(value & 0x01)
        
        # Special Mode Config
        self.special_mapping = (value >> 1) & 0x03
        
        # ROM Selection (High bit)
        rom_bit_1 = (value >> 2) & 0x01
        rom_bit_0 = self.current_rom_bank & 0x01 # zachováme bit z 7FFD
        self.current_rom_bank = (rom_bit_1 << 1) | rom_bit_0

    def get_bank_data(self, bank):
        if self.is_plus3 or self.is_128k:
            return self.ram_banks[bank]
            
        if bank == 0: return self.memory[0x0000:0x4000] # ROM
        if bank == 5: return self.memory[0x4000:0x8000]
        if bank == 2: return self.memory[0x8000:0xC000]
        return self.memory[0xC000:0x10000]

