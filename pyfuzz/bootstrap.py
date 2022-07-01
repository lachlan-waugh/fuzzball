import xml.etree.ElementTree as ET
import json
import csv

from .strategies.json import JSONStrategy
from .strategies.csv import CSVStrategy
from .strategies.xml import XMLStrategy
from .strategies.txt import TXTStrategy
from .strategies.common import CommonStrategy

"""
Used to determine the type of sample input provided for smarter fuzzing
"""
class Bootstrap:
    def __init__(self, sample_input):
        self._sample_input = sample_input

    def bootstrap(self):
        try:
            return XMLStrategy(ET.parse(self._sample_input))
        except Exception:
            pass

        with open(self._sample_input) as sample_input:
            try:
                sample_input.seek(0)
                return JSONStrategy(json.load(sample_input))
            except ValueError as e:
                pass

            try:
                sample_input.seek(0)
                csvObj = csv.Sniffer().sniff(sample_input.read(1024))
                if (csvObj.delimiter in [csv.excel.delimiter, csv.excel_tab.delimiter]):
                    return CSVStrategy(input)
            except csv.Error:
                pass

            return TXTStrategy(sample_input)

    def common(self):
        return CommonStrategy()