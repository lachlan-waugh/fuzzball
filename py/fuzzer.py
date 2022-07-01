from helper import *
from runner import *
import sys
import os

import xml.etree.ElementTree as ET
import json
import csv

sys.path.append('./modules')
from json_fuzzer import JSONFuzzer
from csv_fuzzer import CSVFuzzer
from xml_fuzzer import XMLFuzzer
from txt_fuzzer import TXTFuzzer

"""
> $1: binary name
> $2: sampleinput
"""
class Fuzzer:
    def __init__(self):
        if len(sys.argv) != 3:
            sys.exit("Usage: python3 fuzzer.py [binaryName] [sampleInput]")

        self._binary_file, self._sample_input = sys.argv[1:3]
        if not (os.path.isfile(self._binary_file)):
            sys.exit(f'[x] ERROR: binary file \'{os.path.basename(self._binary_file)}\' not found')
        elif not (os.path.isfile(self._sample_input)):
            sys.exit(f'[x] ERROR: sample input \'{os.path.basename(self._sample_input)}\' not found.')
        else:
            print(f'[*] binary file: {os.path.basename(self._binary_file)}\n[*] sample input: {os.path.basename(self._sample_input)}')

        self._runner = Runner(self._binary_file)

    def get_fuzzer(self):
        with open(self._sample_input) as sample_input:
            try:
                sample_input.seek(0)
                return JSONFuzzer(json.load(sample_input))
            except ValueError as e:
                pass

            try:
                sample_input.seek(0)
                csvObj = csv.Sniffer().sniff(sample_input.read(1024))
                if (csvObj.delimiter in [csv.excel.delimiter, csv.excel_tab.delimiter]):
                    return CSVFuzzer(input)
            except csv.Error:
                pass

            try:
                # file.seek(0)
                return XMLFuzzer(ET.parse(self._sample_input))
            except Exception:
                pass

            return TXTFuzzer(sample_input)

    def fuzz(self):
        # first test some basic input, that doesn't rely on the sample
        # self._runner.run(simple_fuzz())

        # next, mutate the sample input
        self._runner.run(self.get_fuzzer().generate_input())

        # busy wait until the workers finish
        while len(MP.active_children()) > 0:
            sleep(1)

if __name__ == "__main__":
    fuzzer = Fuzzer()
    fuzzer.fuzz()