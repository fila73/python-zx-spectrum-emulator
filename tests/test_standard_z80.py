import json
import os
import unittest
from src.cpu import Z80
from src.memory import Memory

class RawMemory(Memory):
    def write_byte(self, address, value):
        self.memory[address & 0xFFFF] = value & 0xFF

class IOMock:
    def __init__(self, ports_data):
        # ports_data is list of [port, value, type]
        self.ports_data = ports_data
        self.read_index = 0
        self.actual_writes = []

    def read_byte(self, port, cycles=0):
        # Filter for read transactions
        reads = [p for p in self.ports_data if p[2] == 'r']
        if self.read_index < len(reads):
            expected_port, value, _ = reads[self.read_index]
            # Some tests might read from different ports than expected? 
            # Usually they match.
            self.read_index += 1
            return value
        return 0xFF

    def write_byte(self, port, value):
        self.actual_writes.append([port, value, 'w'])

class TestStandardZ80(unittest.TestCase):
    def run_z80_test_file(self, file_path):
        if not os.path.exists(file_path):
            self.skipTest(f"Test file {file_path} not found")
            
        with open(file_path, 'r') as f:
            tests = json.load(f)

        failed_tests = []

        for test in tests:
            name = test['name']
            initial = test['initial']
            final = test['final']
            ports_data = test.get('ports', [])

            # Setup CPU, Memory and I/O
            mem = RawMemory()
            io = IOMock(ports_data)
            cpu = Z80(mem, io_bus=io)

            # Set registers
            cpu.a = initial['a']
            cpu.f = initial['f']
            cpu.b = initial['b']
            cpu.c = initial['c']
            cpu.d = initial['d']
            cpu.e = initial['e']
            cpu.h = initial['h']
            cpu.l = initial['l']
            cpu.pc = initial['pc']
            cpu.sp = initial['sp']
            cpu.ix = initial['ix']
            cpu.iy = initial['iy']
            cpu.i = initial['i']
            cpu.r = initial['r']
            cpu.im = initial['im']
            cpu.iff1 = initial['iff1']
            cpu.iff2 = initial['iff2']
            cpu.wz = initial.get('wz', 0)
            cpu.q = initial.get('q', 0) # Use q if available, else 0

            # Alternate registers
            cpu.a_alt = (initial['af_'] >> 8) & 0xFF
            cpu.f_alt = initial['af_'] & 0xFF
            cpu.b_alt = (initial['bc_'] >> 8) & 0xFF
            cpu.c_alt = initial['bc_'] & 0xFF
            cpu.d_alt = (initial['de_'] >> 8) & 0xFF
            cpu.e_alt = initial['de_'] & 0xFF
            cpu.h_alt = (initial['hl_'] >> 8) & 0xFF
            cpu.l_alt = initial['hl_'] & 0xFF

            # Memory
            for addr, val in initial['ram']:
                mem.write_byte(addr, val)

            # Execute one instruction
            try:
                cpu.step()
            except Exception as e:
                failed_tests.append(f"{name}: Exception during step: {e}")
                continue

            # Verify state
            errors = []

            def check(actual, expected, reg_name):
                if actual != expected:
                    errors.append(f"{reg_name}: expected {hex(expected)}, got {hex(actual)}")

            check(cpu.a, final['a'], 'a')
            check(cpu.f, final['f'], 'f')
            check(cpu.b, final['b'], 'b')
            check(cpu.c, final['c'], 'c')
            check(cpu.d, final['d'], 'd')
            check(cpu.e, final['e'], 'e')
            check(cpu.h, final['h'], 'h')
            check(cpu.l, final['l'], 'l')
            check(cpu.pc, final['pc'], 'pc')
            check(cpu.sp, final['sp'], 'sp')
            check(cpu.ix, final['ix'], 'ix')
            check(cpu.iy, final['iy'], 'iy')
            check(cpu.i, final['i'], 'i')
            
            # Special handling for R: ProcessorTests usually expect R to increment by 1 per M1
            check(cpu.r, final['r'], 'r')
            
            check(cpu.im, final['im'], 'im')
            check(cpu.iff1, final['iff1'], 'iff1')
            check(cpu.iff2, final['iff2'], 'iff2')
            check(cpu.wz, final.get('wz', 0), 'wz')

            # Shadow registers
            check(cpu.a_alt, (final['af_'] >> 8) & 0xFF, 'af_ high')
            check(cpu.f_alt, final['af_'] & 0xFF, 'af_ low')
            check(cpu.b_alt, (final['bc_'] >> 8) & 0xFF, 'bc_ high')
            check(cpu.c_alt, final['bc_'] & 0xFF, 'bc_ low')
            check(cpu.d_alt, (final['de_'] >> 8) & 0xFF, 'de_ high')
            check(cpu.e_alt, final['de_'] & 0xFF, 'de_ low')
            check(cpu.h_alt, (final['hl_'] >> 8) & 0xFF, 'hl_ high')
            check(cpu.l_alt, final['hl_'] & 0xFF, 'hl_ low')

            # RAM
            for addr, val in final['ram']:
                actual_val = mem.read_byte(addr)
                if actual_val != val:
                    errors.append(f"RAM[{hex(addr)}]: expected {hex(val)}, got {hex(actual_val)}")

            # Verify I/O Writes
            expected_writes = [p for p in ports_data if p[2] == 'w']
            if len(io.actual_writes) != len(expected_writes):
                errors.append(f"I/O Writes: expected {len(expected_writes)} writes, got {len(io.actual_writes)}")
            else:
                for i in range(len(expected_writes)):
                    exp_port, exp_val, _ = expected_writes[i]
                    act_port, act_val, _ = io.actual_writes[i]
                    if exp_port != act_port or exp_val != act_val:
                        errors.append(f"I/O Write {i}: expected Port {hex(exp_port)}={hex(exp_val)}, got {hex(act_port)}={hex(act_val)}")

            if errors:
                if name == "ED B2 0000":
                    print(f"DEBUG {name}: initial a={hex(initial['a'])} f={hex(initial['f'])} b={hex(initial['b'])} c={hex(initial['c'])} hl={hex((initial['h'] << 8) | initial['l'])}")
                    print(f"DEBUG {name}: final expected f={hex(final['f'])} actual f={hex(cpu.f)}")
                failed_tests.append(f"{name}:\n  " + "\n  ".join(errors))

        if failed_tests:
            # Only print first few failures to avoid flooding
            msg = f"Failed {len(failed_tests)} tests in {file_path}.\nFirst few failures:\n"
            msg += "\n".join(failed_tests[:5])
            self.fail(msg)

def create_test_method(file_path):
    def test(self):
        self.run_z80_test_file(file_path)
    return test

# Auto-discover tests
test_dir = 'tests/z80_standard'
if os.path.exists(test_dir):
    for filename in os.listdir(test_dir):
        if filename.endswith('.json') and filename != 'test_format.json':
            test_name = 'test_' + filename.replace('.', '_')
            file_path = os.path.join(test_dir, filename)
            setattr(TestStandardZ80, test_name, create_test_method(file_path))

if __name__ == '__main__':
    unittest.main()

