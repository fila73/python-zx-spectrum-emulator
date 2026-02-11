import os
import urllib.request
import time

BASE_URL = "https://raw.githubusercontent.com/SingleStepTests/z80/main/v1/"
TARGET_DIR = "tests/z80_standard"

if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)

def download_file(filename, target_filename=None):
    if target_filename is None:
        target_filename = filename.lower().replace(" ", "")
        
    target_path = os.path.join(TARGET_DIR, target_filename)
    if os.path.exists(target_path):
        return False
    
    url = BASE_URL + filename.replace(" ", "%20")
    print(f"Downloading {url}...")
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                with open(target_path, "wb") as f:
                    f.write(response.read())
                return True
            else:
                print(f"Failed to download {filename}: {response.status}")
                return False
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"HTTP Error {e.code} for {filename}")
        return False
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False

# Standard opcodes 00-FF
print("Downloading standard opcodes...")
for i in range(0x100):
    opcode = f"{i:02x}.json"
    if download_file(opcode):
        time.sleep(0.05)

# CB prefixed
print("Downloading CB prefixed opcodes...")
for i in range(0x100):
    opcode = f"cb {i:02x}.json"
    if download_file(opcode):
        time.sleep(0.05)

# ED prefixed
print("Downloading ED prefixed opcodes...")
for i in range(0x100):
    opcode = f"ed {i:02x}.json"
    if download_file(opcode):
        time.sleep(0.05)

# DD prefixed
print("Downloading DD prefixed opcodes...")
for i in range(0x100):
    opcode = f"dd {i:02x}.json"
    if download_file(opcode):
        time.sleep(0.05)

# FD prefixed
print("Downloading FD prefixed opcodes...")
for i in range(0x100):
    opcode = f"fd {i:02x}.json"
    if download_file(opcode):
        time.sleep(0.05)

# DD CB prefixed
print("Downloading DD CB prefixed opcodes...")
for i in range(0x100):
    opcode = f"dd cb {i:02x}.json"
    if download_file(opcode):
        time.sleep(0.05)

# FD CB prefixed
print("Downloading FD CB prefixed opcodes...")
for i in range(0x100):
    opcode = f"fd cb {i:02x}.json"
    if download_file(opcode):
        time.sleep(0.05)
