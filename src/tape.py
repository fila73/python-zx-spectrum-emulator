import struct

class Tape:
    def __init__(self):
        self.blocks = []
        self.current_block = 0
        self.is_loaded = False

    def load_file(self, filename):
        """
        Load and parse a .TAP or .TZX file.
        Načte a analyzuje .TAP nebo .TZX soubor.
        """
        try:
            with open(filename, 'rb') as f:
                data = f.read()
            
            self.blocks = []
            if filename.lower().endswith('.tap'):
                self._load_tap(data)
            elif filename.lower().endswith('.tzx'):
                self._load_tzx(data)
            else:
                print(f"Unknown tape format: {filename}")
                return False
                
            self.current_block = 0
            self.is_loaded = True
            print(f"Tape loaded: {filename} ({len(self.blocks)} blocks)")
            return True
        except Exception as e:
            print(f"Error loading tape: {e}")
            return False

    def _load_tap(self, data):
        pos = 0
        while pos < len(data):
            if pos + 2 > len(data): break
            length = struct.unpack('<H', data[pos:pos+2])[0]
            pos += 2
            if pos + length > len(data): break
            self.blocks.append(data[pos:pos+length])
            pos += length

    def _load_tzx(self, data):
        # TZX Header: "ZXTape!" + 0x1A + Major + Minor
        if data[:7] != b'ZXTape!' or data[7] != 0x1A:
            raise ValueError("Not a valid TZX file")
            
        pos = 10
        while pos < len(data):
            block_id = data[pos]
            pos += 1
            
            if block_id == 0x10: # Standard Speed Data Block
                pause = struct.unpack('<H', data[pos:pos+2])[0]
                pos += 2
                length = struct.unpack('<H', data[pos:pos+2])[0]
                pos += 2
                self.blocks.append(data[pos:pos+length])
                pos += length
            elif block_id == 0x11: # Turbo Speed Data Block
                # Skip for now, or handle?
                # Structure: Pilot pulse len(2), First sync(2), Second sync(2), Zero pulse(2), One pulse(2), 
                # Pilot count(2), Used bits in last byte(1), Pause(2), Length(3), Data
                pos += 18 # All fixed size fields before length
                length = data[pos] | (data[pos+1] << 8) | (data[pos+2] << 16)
                pos += 3
                self.blocks.append(data[pos:pos+length])
                pos += length
            elif block_id == 0x32: # Archive Info
                length = struct.unpack('<H', data[pos:pos+2])[0]
                pos += 2 + length
            elif block_id == 0x20: # Pause (silence)
                pos += 2
            elif block_id == 0x30: # Text Description
                length = data[pos]
                pos += 1 + length
            else:
                # Unknown block, many TZX blocks have length at different offsets.
                # This is tricky for a generic parser. 
                # Let's handle some common ones.
                print(f"Skipping TZX block {hex(block_id)}")
                break # Stop parsing to avoid desync if we don't know the length


    def get_next_block(self):
        """
        Return the next block data or None if no more blocks.
        Vrátí data dalšího bloku nebo None, pokud už žádné nejsou.
        """
        if not self.is_loaded or self.current_block >= len(self.blocks):
            return None
        
        block = self.blocks[self.current_block]
        self.current_block += 1
        return block

    def rewind(self):
        """
        Rewind tape to beginning.
        Přetočí pásku na začátek.
        """
        self.current_block = 0
