import random
import string
import sys
import os

def get_arguments():
    if len(sys.argv) != 3:
        sys.exit("Usage: python3 -m pyfuzz [binaryName] [sampleInput]")

    binary, sample = sys.argv[1:3]
    if not (os.path.isfile(binary)):
        sys.exit(f'[x] ERROR: binary file \'{os.path.basename(binary)}\' not found')
    elif not (os.path.isfile(sample)):
        sys.exit(f'[x] ERROR: sample input \'{os.path.basename(sample)}\' not found.')
    else:
        print(f'[*] binary file: {os.path.basename(binary)}. sample input: {os.path.basename(sample)}')

    return binary, sample

def get_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for _ in range(length))

# TODO: fix
def get_random_format_string(size):
    return ''.join(random.choice(['%x', '%c', '%d', '%p', '%s']) for _ in range(size))
