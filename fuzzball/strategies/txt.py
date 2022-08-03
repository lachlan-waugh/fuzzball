from time import sleep
from pwn import *
import itertools
import logging

class TXTStrategy:
    def __init__(self, input):
        try:
            print('[*] TXT input detected, mutation started')
            input.seek(0)
            self.txt = input.readlines()
        except Exception as e:
            print(f'[x] TXTStrategy.__init__ error: {e}')

    def generate_input(self):
        # 31, 'integer overflow'
        for i in range(31):
            payload = b''
            for _ in self.txt:
                payload += str(1 << i).encode() + b'\n'
            yield payload

        # 13, 'buffer overflow'
        for i in range(13):
            payload = b''
            for _ in self.txt:
                payload += f'{cyclic(1 << i)}\n'.encode()
            yield payload
        
        # 30, 'expand lines'
        for i in range(1, 11):
            yield b''.join(f'{line[:-1] * i}\n'.encode() for line in self.txt)

            try:
                yield b''.join(f'{-int(line[:-1])}\n'.encode() for line in self.txt)
            except ValueError:
                yield b''.join(f'{line[:-1]}\n'.encode() for line in self.txt)

            try:
                yield b''.join(f'{-int(line[:-1]) * (2 ** (i + 2))}\n'.encode() for line in self.txt)
            except ValueError:
                yield b''.join(f'{line[:-1] * (2 ** (i + 2))}\n'.encode() for line in self.txt)

        # 99, 'format strings'
        for i in range(1, 100):
            yield f'%{i}$s %{i}$x %{i}$p %{i}$c\n'.encode() * len(self.txt)

        ## Mutation Based
        payloads = self.mutation_based()
        # len(list(payloads)), 'mutation'
        for payload in list(payloads):
            yield f'{payload}'.encode()

        payloads = self.mutate_numbers()
        # len(list(payloads)), 'mutate numbers'
        for payload in list(payloads):
            yield f'{payload}'.encode()

        payloads = self.mutate_everything()
        # len(list(payloads)), 'mutate everything'
        for payload in payloads:
            yield f'{payload}'.encode()

        # 5, 'numerical perms'
        for i in range(5): # Basic Numeric Permutation of various lengths
            for payload in num_perm(i):
                yield f'{payload}'.encode()

        # 4, 'alphabetical perms'
        for i in range(4): # Basic Alphabet Permutation of various lengths
            for payload in alpha_perm(i):
                yield f'{payload}'.encode()

        # 4, 'alphanumeric perms'
        for i in range(4): # Basic Alphanumeric Permuation of various lengths
            for payload in alphanum_perm(i):
                yield f'{payload}'.encode()

    # Mutate numbers only (SLOW FINE GRAIN)
    def mutation_based(self):
        perm_inputs = []
        for line in self.txt:
            perm_lines = []
            for perm_line in defined_num_perm(line, len(line), -100, 100, 1):
                if isinstance(perm_line, int):
                    perm_lines.append(f'{perm_line}\n'.encode())
                else:
                    perm_lines.append(line)
                    break
            perm_inputs.append(perm_lines)

        return list(itertools.product(*perm_inputs)) if (len(perm_inputs) > 1) else perm_inputs[0]

    def mutate_numbers(self):
        # Mutate numbers only (FAST WIDE SWEEP)
        perm_inputs = []
        for line in self.txt:
            perm_lines = []
            for perm_line in defined_num_perm(line, len(line), -5000, 5000, 10):
                if isinstance(perm_line, int):
                    perm_lines.append(f'{perm_line}\n')
                else:
                    perm_lines.append(line)
                    break
            perm_inputs.append(perm_lines)

        return list(itertools.product(*perm_inputs)) if (len(perm_inputs) > 1) else perm_inputs[0]

    def mutate_everything(self):
        perm_inputs = []
        for line in self.txt:
            perm_lines = []
            for perm_line in defined_perm(line, len(line)):
                perm_lines.append(f'{perm_line}\n')
            perm_inputs.append(perm_lines)

        return list(itertools.product(*perm_inputs)) if (len(perm_inputs) > 1) else perm_inputs[0]

def alpha_perm(length):
    alphabet = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz\n'
    return itertools.combinations_with_replacement(alphabet, length)

def num_perm(length):
    alphabet = b'0123456789\n'
    return itertools.combinations_with_replacement(alphabet, length)

def alphanum_perm(length):
    alphabet = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\n'
    return itertools.combinations_with_replacement(alphabet, length)

def defined_perm(alphabet, length):
    # do not include trailing \n
    return itertools.combinations_with_replacement(alphabet[:-1], length - 1)

def defined_num_perm(alphabet, length, start, stop, speed):
    try:
        int(alphabet[:-1])
    except ValueError:
        return alphabet[:-1]
    return range(start, stop, speed)