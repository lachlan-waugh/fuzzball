from alive_progress import *
from time import sleep
from pwn import *
import itertools
import logging

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

class TXTStrategy:
    def __init__(self, input):
        try:
            print('[*] TXT input detected, mutation started')
            input.seek(0)
            self._txt = input.readlines()
        except Exception as e:
            print(f'[x] TXTStrategy.__init__ error: {e}')

            # Mutate numbers only (SLOW FINE GRAIN)
    def mutation_based(self):
        perm_inputs = []
        for line in self._txt:
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
        for line in self._txt:
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
        for line in self._txt:
            perm_lines = []
            for perm_line in defined_perm(line, len(line)):
                perm_lines.append(f'{perm_line}\n')
            perm_inputs.append(perm_lines)

        return list(itertools.product(*perm_inputs)) if (len(perm_inputs) > 1) else perm_inputs[0]

    def generate_input(self):
        with alive_bar(31, dual_line=True, title='integer overflow'.ljust(20)) as bar:
            for i in range(31):
                payload = b''
                for _ in self._txt:
                    payload += str(1 << i).encode() + b'\n'

                bar()
                yield payload

        with alive_bar(13, dual_line=True, title='buffer overflow'.ljust(20)) as bar:
            for i in range(13):
                payload = b''
                for _ in self._txt:
                    payload += f'{cyclic(1 << i)}\n'.encode()

                bar()
                yield payload

        with alive_bar(10, dual_line=True, title='expand lines'.ljust(20)) as bar:
            for i in range(1, 11):
                payload = b''
                for line in self._txt:
                    payload += f'{line[:-1] * i}\n'.encode()
                
                bar()
                yield payload

        with alive_bar(1, dual_line=True, title='negating numbers'.ljust(20)) as bar:
            payload = b''
            for line in self._txt:
                try:
                    payload += f'{-int(line[:-1])}\n'.encode()
                except ValueError:
                    payload += f'{line[:-1]}\n'.encode()

            bar()
            yield payload

        with alive_bar(1, dual_line=True, title='negate & expand'.ljust(20)) as bar:
            payload = b''
            for line in self._txt:
                try:
                    payload += f'{-int(line[:-1])}\n'.encode()
                except ValueError:
                    payload += f'{line[:-1] * 512}\n'.encode()
            
            bar()
            yield payload

        with alive_bar(99, dual_line=True, title='format strings'.ljust(20)) as bar:
            for i in range(1, 100):
                payload = f'%{i}$s %{i}$x %{i}$p %{i}$c\n'.encode() * len(self._txt)
                
                bar()
                yield payload

        ## Mutation Based
        payloads = self.mutation_based()
        with alive_bar(len(list(payloads)), dual_line=True, title='mutation'.ljust(20)) as bar:
            for payload in list(payloads):
                bar()
                yield f'{payload}'.encode()

        payloads = self.mutate_numbers()
        with alive_bar(len(list(payloads)), dual_line=True, title='mutate numbers'.ljust(20)) as bar:
            for payload in list(payloads):
                bar()
                yield f'{payload}'.encode()

        payloads = self.mutate_everything()
        with alive_bar(len(list(payloads)), dual_line=True, title='mutate everything'.ljust(20)) as bar:
            for payload in payloads:
                yield f'{payload}'.encode()

        with alive_bar(5, dual_line=True, title='numerical perms'.ljust(20)) as bar:
            # Basic Numeric Permutation of various lengths
            for i in range(5):
                for payload in num_perm(i):
                    yield f'{payload}'.encode()

        with alive_bar(4, dual_line=True, title='alphabetical perms'.ljust(20)) as bar:
            # Basic Alphabet Permutation of various lengths
            for i in range(4):
                for payload in alpha_perm(i):
                    yield f'{payload}'.encode()

        with alive_bar(4, dual_line=True, title='alphanumeric perms'.ljust(20)) as bar:
            # Basic Alphanumeric Permuation of various lengths
            for i in range(4):
                for payload in alphanum_perm(i):
                    yield f'{payload}'.encode()