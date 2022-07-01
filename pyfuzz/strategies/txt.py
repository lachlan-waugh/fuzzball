from time import sleep
from pwn import flat
import itertools
import logging

def alpha_perm(length):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ\n"
    return itertools.combinations_with_replacement(alphabet, length)

def num_perm(length):
    alphabet = "0123456789\n"
    return itertools.combinations_with_replacement(alphabet, length)

def alphanum_perm(length):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\n"
    return itertools.combinations_with_replacement(alphabet, length)

def defined_perm(alphabet, length):
    return itertools.combinations_with_replacement(
        alphabet[:-1], length - 1
    )  # do not include trailing \n

def defined_num_perm(alphabet, length, start, stop, speed):
    try:
        int(alphabet[:-1])
    except ValueError:
        return alphabet[:-1]
    return range(start, stop, speed)

def txt_fuzzer(binary, inputFile):
    # Ordered by speed of execution and likelihood of success

    ## Basic functions
    # Empty

    ## Overflow

    # Simple Overflow (Numeric)
    for i in range(31):
        payload = b""
        for _ in lines:
            payload += flat(str(1 << i)) + b"\n"
        test_payload(binary, payload)

    # Simple Overflow (Text)
    for i in range(13):
        payload = b""
        for _ in lines:
            payload += cyclic(1 << i) + b"\n"
        test_payload(binary, payload)

    # Expand Lines
    payload = ""
    for line in lines:
        payload += line[:-1] * 4 + "\n"
    test_payload(binary, payload)

    # Negate numbers
    payload = ""
    for line in lines:
        try:
            temp = int(line[:-1])
        except ValueError:
            payload += line[:-1] + "\n"
        else:
            temp = str(-temp)
            payload += temp + "\n"
    test_payload(binary, payload)

    # Negate numbers and expand lines
    payload = ""
    for line in lines:
        try:
            temp = int(line[:-1])
            temp = str(-temp)
            payload += temp + "\n"
        except ValueError:
            payload += line[:-1] * 512 + "\n"
    test_payload(binary, payload)

    # Format String
    payload = b"%10$s %100$s %1000$s %10$p %100$p %1000$p\n" * num_lines
    test_payload(binary, payload)

    ## Mutation Based

    # Mutate numbers only (SLOW FINE GRAIN)

    perm_inputs = []
    for line in lines:
        perm_lines = []
        for perm_line in defined_num_perm(line, len(line), -100, 100, 1):
            if isinstance(perm_line, int):
                perm_lines.append("".join(str(perm_line)) + "\n")
            else:
                perm_lines.append(line)
                break
        perm_inputs.append(perm_lines)

    if len(perm_inputs) > 1:
        payloads = list(itertools.product(*perm_inputs))
    else:
        payloads = perm_inputs[0]

    for payload in list(payloads):
        test_payload(binary, "".join(payload).encode())

    # Mutate numbers only (FAST WIDE SWEEP)
    perm_inputs = []
    for line in lines:
        perm_lines = []
        for perm_line in defined_num_perm(line, len(line), -5000, 5000, 10):
            if isinstance(perm_line, int):
                perm_lines.append("".join(str(perm_line)) + "\n")
            else:
                perm_lines.append(line)
                break
        perm_inputs.append(perm_lines)

    if len(perm_inputs) > 1:
        payloads = list(itertools.product(*perm_inputs))
    else:
        payloads = perm_inputs[0]

    for payload in list(payloads):
        test_payload(binary, "".join(payload).encode())

    # Mutate everything

    perm_inputs = []
    for line in lines:
        perm_lines = []
        for perm_line in defined_perm(line, len(line)):
            perm_lines.append("".join(perm_line) + "\n")
        perm_inputs.append(perm_lines)

    if len(perm_inputs) > 1:
        payloads = list(itertools.product(*perm_inputs))
    else:
        payloads = perm_inputs[0]

    for payload in payloads:
        test_payload(binary, "".join(payload).encode())

    # Basic Numeric Permutation of various lengths
    for i in range(5):
        for payload in num_perm(i):
            test_payload(binary, "".join(payload).encode())

    # Basic Alphabet Permutation of various lengths
    for i in range(4):
        for payload in alpha_perm(i):
            test_payload(binary, "".join(payload).encode())

    # Basic Alphanumeric Permuation of various lengths
    for i in range(4):
        for payload in alphanum_perm(i):
            test_payload(binary, "".join(payload).encode())

class TXTStrategy:
    def __init__(self, input):
        try:
            print('[*] TXT Fuzzer started')
            self._txt = input.readlines()
        except Exception as e:
            print(f'[x] {e}')

    def generate_input(self):
        yield b'1'