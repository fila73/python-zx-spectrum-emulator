import sys
sys.path.append('.')
from src.cpu import Z80
from src.memory import Memory
from src.io import IOBus
class FakeULA:
    def read_port(self, port):
        # return same as ULA does for port 0xFE
        if (port & 1) == 0:
            return 0xDE # Key pressed
        return None

mem = Memory()
bus = IOBus()
ula = FakeULA()
bus.add_device(ula)
z80 = Z80(mem, bus)
z80.ula = ula

# IN A, (C) -> opcode ED 78
# set BC to 0xFEFE
z80.b = 0xFE
z80.c = 0xFE
z80.memory.write_byte(0, 0xED)
z80.memory.write_byte(1, 0x78)

z80.pc = 0
z80.step()
print("A after IN A, (C):", hex(z80.a))
