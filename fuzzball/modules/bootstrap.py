import magic
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
    types = {
        'json': JSONStrategy,
        'csv': CSVStrategy,
        'html': XMLStrategy,
        'plain': TXTStrategy 
    }
    
    def __init__(self, sample_input):
        self.sample_input = sample_input
 
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
        file_type = magic.from_file(self.sample_input, mime=True).split('/')[1]
        
        with open(self.sample_input) as sample_input
            strategy = self.types.get(file_type, CommonStrategy)(sample_input)