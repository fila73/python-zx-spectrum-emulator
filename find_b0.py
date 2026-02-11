import json
import sys

filename = sys.argv[1]

with open(filename, 'r') as f:
    tests = json.load(f)
    for test in tests:
        if test['final']['b'] == 0:
            print(json.dumps(test, indent=2))
            break
