import subprocess
import time

p = subprocess.Popen(["python3", "emulator.py", "--zx81"])
time.sleep(4) # wait to boot
print("Booted.")

# We can't easily simulate pygame keypresses from another script without X11 automation
# But we can see if it throws any new errors.
p.terminate()
