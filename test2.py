import sys
sys.path.append('.')
from src.cpu import Z80
print("Testing _in_r_c")
import inspect
print(inspect.getsource(Z80._in_r_c))
