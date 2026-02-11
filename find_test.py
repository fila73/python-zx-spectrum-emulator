import json
import sys

filename = sys.argv[1]
test_name = sys.argv[2]

with open(filename, 'r') as f:
    tests = json.load(f)
    for test in tests:
        if test['name'] == test_name:
            print(json.dumps(test, indent=2))
            break
