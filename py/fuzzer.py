import sys
import os
import logging

from helper import *

# argument error checking
# 1 = binary name
# 2 = sampleinput

if len(sys.argv) != 3:
    sys.exit("Usage: python3 fuzzer.py [binaryName] [sampleInput]")

binaryFileName = sys.argv[1]
sampleInputFileName = sys.argv[2]
print(f'[*] binary: {sampleInputFileName}\n[*] sample input: {binaryFileName}')

PATH_TO_SANDBOX = ""  # make empty string for deployment
binary = PATH_TO_SANDBOX + binaryFileName
if not (os.path.isfile(binary)):
    sys.exit('[x] binary doesn\'t exist')

inputFile = PATH_TO_SANDBOX + sampleInputFileName
if not (os.path.isfile(inputFile)):
    sys.exit('[x] sample input doesn\'t exist')

# next, mutate the sample input
with open(inputFile) as input:
    # first test some basic input, that doesn't rely on the sample
    simple_fuzz()

    # 
    for test_input in get_fuzzer(input).generate_input():
        try:
            test_payload(binary, test_input)
        except Exception as e:
            print(e)

    # busy wait until the workers finish
    while len(MP.active_children()) > 0:
        sleep(1)
