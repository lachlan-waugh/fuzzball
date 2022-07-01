from helper import *
from pwn import *
import sys
import os
import logging

# context.log_level = 'ERROR'

# argument error checking
# 1 = binary name
# 2 = sampleinput

if len(sys.argv) != 3:
    sys.exit("Usage: python3 fuzzer.py [binaryName] [sampleInput]")

binary_file, sample_input = sys.argv[1:3]
if not (os.path.isfile(binary_file)):
    sys.exit(f'[x] ERROR: binary file \'{os.path.basename(binary_file)}\' not found')
elif not (os.path.isfile(sample_input)):
    sys.exit(f'[x] ERROR: sample input \'{os.path.basename(sample_input)}\' not found.')
else:
    print(f'[*] binary file: {os.path.basename(binary_file)}\n[*] sample input: {os.path.basename(sample_input)}')

# first test some basic input, that doesn't rely on the sample
generate_inputs(binary_file, simple_fuzz())

# next, mutate the sample input
with open(sample_input) as input:
    generate_inputs(binary_file, get_fuzzer(input).generate_input())

# busy wait until the workers finish
while len(MP.active_children()) > 0:
    sleep(1)
