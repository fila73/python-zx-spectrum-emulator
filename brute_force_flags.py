import json

def parity(val):
    return bin(val).count('1') % 2 == 0

def test_file(file_path):
    with open(file_path, 'r') as f:
        tests = json.load(f)
    
    is_ini = 'b2' in file_path.lower() or 'ba' in file_path.lower()
    
    results = []
    # Brute force XOR combination of 3-bit values
    for b_expr in ['b_before', 'b_after']:
        for mod_expr in ['c', 'c+1', 'c-1', 'l_before', 'l_after']:
            for h_expr in ['none', 'h_int']:
                for c_expr in ['none', 'c_flag']:
                    for n_expr in ['none', 'n_flag']:
                        for offset in [-1, 0, 1]:
                            correct = 0
                            for test in tests:
                                if not test.get('ports'): continue
                                val = test['ports'][0][1]
                                initial = test['initial']
                                final = test['final']
                                b_val = initial['b'] if b_expr == 'b_before' else final['b']
                                if mod_expr == 'c': mod = initial['c']
                                elif mod_expr == 'c+1': mod = (initial['c']+1)&0xFF
                                elif mod_expr == 'c-1': mod = (initial['c']-1)&0xFF
                                elif mod_expr == 'l_before': mod = initial['l']
                                elif mod_expr == 'l_after': mod = final['l']
                                
                                k = (val + mod + offset) & 0x1FF
                                h = (1 if (val & 0x0F) + (mod & 0x0F) > 0x0F else 0) if h_expr == 'h_int' else 0
                                c_flag = 1 if (val + mod) > 255 else 0
                                n_flag = (val >> 7)
                                
                                xor_val = (k & 7) ^ (b_val & 7)
                                if h == 1: xor_val ^= 1 # wait, this only affects 1 bit
                                if c_flag == 1: xor_val ^= 2 # arbitrary
                                if n_flag == 1: xor_val ^= 4 # arbitrary
                                
                                # Actually, it's parity of the whole byte
                                xor_byte = (k & 7) ^ b_val
                                if h: xor_byte ^= 0x01 # or something else?
                                # Let's try XORing with various bits
                                
                                # Let's stick to the most common: parity((k & 7) ^ b_val ^ h)
                                # I already tried that.
                                pass
    print(f"Finished {file_path}")

test_file('tests/z80_standard/edb2.json')