import xml.etree.ElementTree as ET
import json
import csv
import sys

from ..strategies.json import JSONStrategy
from ..strategies.csv import CSVStrategy
from ..strategies.xml import XMLStrategy
from ..strategies.txt import TXTStrategy
from ..strategies.common import CommonStrategy

"""
# Returns the relevant strategies to be used for the fuzzing logic
"""
class Bootstrap:
    def __init__(self, sample_input):
        self._sample_input = sample_input
 
    """
    # used for the initial, basic fuzzing logic. 
    # Generates some input (that isn't based on the sample) to test
    """
    def common(self):
        return CommonStrategy()

    """
    # Used to determine the type of sample input provided for smarter fuzzing
    # takes in the sample input, and returns the strategies to mutate that input
    """
    def bootstrap(self):
        with open(self._sample_input) as sample_input:
            for lace in self.laces():
                strategy = lace(sample_input)
                if strategy:
                    return strategy

                sample_input.seek(0)

    """
    # 
    """
    def laces(self):
        return [
            self.is_xml,
            self.is_json,
            self.is_csv,
            self.is_txt
        ]

    def is_xml(self, sample_input):
        try:
            return XMLStrategy(ET.parse(self._sample_input))
        except Exception:
            return None

    def is_json(self, sample_input):
        try:
            return JSONStrategy(json.load(sample_input))
        except ValueError as e:
            return None

    def is_csv(self, sample_input):
        try:
            csvObj = csv.Sniffer().sniff(sample_input.read(1024))
            if (csvObj.delimiter in [csv.excel.delimiter, csv.excel_tab.delimiter]):
                return CSVStrategy(sample_input)
        except csv.Error:
            return None
    
    def is_txt(self, sample_input):
        return TXTStrategy(sample_input)