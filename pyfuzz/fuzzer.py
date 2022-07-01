from .utility.helper import *
from .utility.harness import *
from .bootstrap import *

"""
> $1: binary name
> $2: sampleinput
"""
class Fuzzer:
    def __init__(self):
        self._binary_file, self._sample_input = get_arguments()
        self._harness = Harness(self._binary_file)
        self._strategies = Bootstrap(self._sample_input)

    def fuzz(self):
        # first test some basic input, that doesn't rely on the sample
        self._harness.run(self._strategies.common().generate_input())

        # next, mutate the sample input
        self._harness.run(self._strategies.bootstrap().generate_input())

        # busy wait until the workers finish
        while len(MP.active_children()) > 0:
            sleep(1)

if __name__ == "__main__":
    fuzzer = Fuzzer()
    fuzzer.fuzz()