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

# first test some basic input, that doesn't rely on the sample
simple_fuzz()

# next, mutate the sample input
with open(inputFile) as file:
    complex_fuzz(file)

    # busy wait until the workers finish
    while len(MP.active_children()) > 0:
        sleep(1)
