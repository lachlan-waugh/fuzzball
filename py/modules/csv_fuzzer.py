import random
import csv
import sys
import os

from helper import *

def fields_csv(binary, csv_input, delimiter):
    expected_field_no = -1
    for field_no in range(1, len(csv_input[0]) + 10):
        error = []
        for x in range(len(csv_input)):
            n = len(csv_input[x])
            if field_no < n:
                for _ in range(0, n - field_no):
                    csv_input[x].pop()
            else:
                for _ in range(n, field_no):
                    csv_input[x].append("A")
            try:
                test_payload(binary, delimiter.join(csv_input[x]))
            except:
                if x > 0:
                    # assumption that sending multiple lines is accpeted no of fields
                    # assumption only one right number of fields
                    expected_field_no = x
                break
            error.append(delimiter.join(csv_input[x]) + "\n")
        test_payload(binary, "".join(error))
    return expected_field_no

# Check if a enough CSV lines will crash the program
def lines_csv(binary, csv_input, delimiter):
    for length in range(0, 1000, 100):
        error = []
        for l in range(0, length):
            if l < len(csv_input):
                test_payload(binary, delimiter.join(csv_input[l]))
                error.append(delimiter.join(csv_input[l]) + "\n")
            else:
                test_payload(binary, delimiter.join(csv_input[len(csv_input) - 1]))
                error.append(delimiter.join(csv_input[len(csv_input) - 1]) + "\n")

        test_payload(binary, "".join(error))

# remove all delimiters make file invalid
def remove_delimiters(binary, csv_input, delimiter):
    payload = ""
    for l in range(0, len(csv_input)):
        payload += "".join(csv_input[l]) + "\n"
    test_payload(binary, payload)

def change_delimiters(binary, csv_input):
    for x in [" ", ".", ",", "\t", "\n", "|", "/", "\\", ":", ";"]:
        payload = ""
        for l in range(0, len(csv_input)):
            payload += x.join(csv_input[l]) + "\n"
        test_payload(binary, payload)

def overflow_fields(binary, csv_input, delimiter):
    for x in range(32, 1000, 32):
        payload = ""
        for l in range(0, len(csv_input)):
            if l == 1 and random.randrange(0, 1) == 1:
                payload += delimiter.join(csv_input[0]) + "\n"
                continue
            for w in csv_input[l]:
                payload += "A" * x + delimiter
            payload = payload[:-1] + "\n"
        test_payload(binary, payload)

def format_string(binary, csv_input, delimiter):
    for x in ["%p", "%s"]:
        payload = delimiter.join(csv_input[0]) + "\n"
        for l in range(1, len(csv_input)):
            for _ in csv_input[l]:
                payload += x * 32 + delimiter
            payload = payload[:-1] + "\n"
        test_payload(binary, payload)
    for x in ["%p", "%s"]:
        for l in range(0, len(csv_input)):
            for w in csv_input[l]:
                payload += x * 32 + delimiter
            payload = payload[:-1] + "\n"
        test_payload(binary, payload)

def change_header(binary, csv_input, delimiter):
    payload = ""
    for l in range(0, len(csv_input)):
        for _ in range(0, len(csv_input[l])):
            payload += get_random_string(25) + delimiter
        payload = payload[:-1] + "\n"
    test_payload(binary, payload)

# overflows
def overflow_numbers(binary, csv_input, delimiter):
    # zero
    payload = ""
    payload = delimiter.join(csv_input[0]) + "\n"
    firstline = len(payload)
    for l in range(1, len(csv_input)):
        for _ in range(0, len(csv_input[l])):
            payload += "0" + delimiter
        payload = payload[:-1] + "\n"
    test_payload(binary, payload)
    test_payload(binary, payload[firstline:])

    # negative numbers
    payload = delimiter.join(csv_input[0]) + "\n"
    for l in range(1, len(csv_input)):
        for _ in range(0, len(csv_input[l])):
            payload += str(random.randrange(-4294967296, 0)) + delimiter
        payload = payload[:-1] + "\n"
    test_payload(binary, payload)
    test_payload(binary, payload[firstline:])

    # high postive numbers
    payload = delimiter.join(csv_input[0]) + "\n"
    for l in range(1, len(csv_input)):
        for _ in range(0, len(csv_input[l])):
            payload += str(random.randrange(2147483648, (2 ** 65))) + delimiter
        payload = payload[:-1] + "\n"
    test_payload(binary, payload)
    test_payload(binary, payload[firstline:])

    # float
    payload = delimiter.join(csv_input[0]) + "\n"
    for l in range(1, len(csv_input)):
        for _ in range(0, len(csv_input[l])):
            payload += str(random.random()) + delimiter
        payload = payload[:-1] + "\n"
    test_payload(binary, payload)
    test_payload(binary, payload[firstline:])

def byte_flip(self):
    payload = ""
    freq = random.randrange(1, 20)
    
    for l in range(0, len(self._csv)):
        for w in range(0, len(self._csv[l])):
            payload += self._csv[l][w] + self._delim
        payload = payload[:-1] + "\n"
    payload = bytearray(payload, "UTF-8")
    
    for i in range(0, len(payload)):
        if random.randint(0, freq) == 1:
            payload[i] ^= random.getrandbits(7)

    return payload

class CSVFuzzer:
    def __init__(self, input):
        try:
            csvObj = csv.Sniffer().sniff(input.read(1024))
            input.seek(0)
            self._delim = csvObj.delimiter
            self._csv = [row for row in csv.reader(input, delimiter=self._delim)]
        except Exception as e:
            print(e)

    def generate_input(self):
        csv_input, delimiter = read_csv(inputFile)
        # check nothing
        yield empty(binary)
        # invalid csv - remove all delimiters
        yield remove_delimiters(binary, csv_input, delimiter)
        # check number of lines
        yield lines_csv(binary, csv_input, delimiter)
        # check fields - can return number of expected fields
        yield fields_csv(binary, csv_input, delimiter)
        # change delimiters
        yield change_delimiters(binary, csv_input)
        # overflowing fields with string
        yield overflow_fields(binary, csv_input, delimiter)
        # string format
        yield format_string(binary, csv_input, delimiter)
        # change first line
        yield change_header(binary, csv_input, delimiter)
        # overflow intergers
        yield overflow_numbers(binary, csv_input, delimiter)
        # bit flipping
        for _ in range(0, 20):
            yield byte_flip(binary, csv_input, delimiter)