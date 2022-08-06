from .modules.helper import *
from .modules.harness import *
from .modules.bootstrap import *
from .modules.coverage import *

"""
> $1: binary name
> $2: sampleinput
"""
class Fuzzer:
    def __init__(self):
        self.binary_file, self._sample_input = get_arguments()
        self.harness = Harness(self._binary_file)
        self.strategies = Bootstrap(self._sample_input)
        self.coverage = Coverage()

    def run(self):
        # first generate some input, that doesn't rely on the sample
        self.harness.run(self.strategies.common().generate_input())

        # next, mutate the sample input
        self.harness.run(self.strategies.bootstrap().generate_input())

        # busy wait until the workers finish
        while len(MP.active_children()) > 0:
            sleep(1)