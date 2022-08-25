import random
import string
import sys
import os

def get_arguments():
    if len(sys.argv) != 3:
        sys.exit("Usage: python3 -m fuzzball [binaryName] [sampleInput]")

    binary, sample = sys.argv[1:3]
    if not (os.path.isfile(binary)):
        sys.exit(f'[x] ERROR: binary file \'{os.path.basename(binary)}\' not found')
    elif not (os.path.isfile(sample)):
        sys.exit(f'[x] ERROR: sample input \'{os.path.basename(sample)}\' not found.')
    else:
        print(f'[*] binary file: {os.path.basename(binary)}. sample input: {os.path.basename(sample)}')

    return binary, sample