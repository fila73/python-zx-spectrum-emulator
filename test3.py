import sys
sys.path.append('.')
from src.cpu import Z80
print("Testing _in_a_n")
import inspect
print(inspect.getsource(Z80._in_a_n))
