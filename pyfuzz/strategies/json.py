from alive_progress import *
import random
import json

class JSONStrategy:
    def __init__(self, input):
        print('[*] JSON Fuzzer started')
        try:
            self._json = input
        except Exception as e:
            print(f'[x] ERROR: JSONFuzzer init {e}')

    def deep_nested_json(self, dictionary, length):
        if length == 0:
            return random.randint(0, 1024)
        else:
            dictionary[get_random_string(8)] = self.deep_nested_json({}, length - 1)

        return dictionary

    def invalid_json(self):
        return ''.join(chr(random.randrange(0, 255)) for x in range(0, 1000)).encode('UTF-8')

    def random_json(self):
        payload = {}
        chances = [None, get_random_string(6),random.randint(0, 1024), self.deep_nested_json({}, 32)]
        for i in range(100):
            payload[get_random_string(5)] = chances[random.randint(0, 3)]

        return json.dumps(payload).encode('UTF-8')

    # ASDASD
    def nullify_json(self):
        payload = self._json.copy()
        # set inputs to 0 equivelants
        for key in payload.keys():
            try:
                payload[key] += 1
                payload[key] = 0
            except TypeError:
                payload[key] = [] if (type(payload[key]) is dict) else ''

        return json.dumps(payload).encode('UTF-8')

    def all_null(self):
        payload = self._json.copy()
        for key in payload.keys():
            payload[key] = None

        return json.dumps(payload).encode('UTF-8')

    # asdasdasdas
    def add_fields(self):
        # add additional entries
        for i in range(25):
            payload = json_object.copy()
            for x in range(i):
                payload[get_random_string(10)] = get_random_string(5) if random.randint(0, 1) else random.randint(0, 262144)

            yield payload

    def remove_fields(self):
        for i in range(len(self._json.keys())):
            payload = json_object.copy()
            for x in range(i):
                # have chosen not to sort to have different subsets of fields removed (more random impact ?)
                del payload[list(self._json.keys())[x]]

            yield payload.encode('UTF-8')

    def swap_json_fields(self):
        fields = [ self._json[entry] for entry in self._json ]
        payload = self._json.copy()
        for entry in payload:
            payload[entry] = random.choice(fields)

        return payload

    # performs type swaps on ints and strings in root level of json dict
    def swap_json_values(self):
        for key in self._json:
            try:
                self._json[key] += 1
                self._json[key] = get_random_string(random.randint(2, 10))
            except TypeError:
                if type(self._json[key]) is dict:
                    self._json[key] = swap_json_values(self._json[key])
                else:
                    self._json[key] = random.randint(2, 10)
        return self._json

    # ADASDSA
    def wrong_type_values(self):
        return json.dumps(self._json.copy() + json.dumps(swap_json_values(self._json.copy())).encode("UTF-8")).encode("UTF-8")

    # TODO: fix the actions switch
    def random_types(self):
        actions = {
            'string': get_random_string(random.randint(16, 12000)),
            'boolean': random.choice([True, False]),
            'int': random.randint(-429496729, 429496729),
            'none': None,
            'list': list(range(self.randint(-64, 0), random.randint(0, 64))),
            'float': random.uniform(-128, 128),
            'dict': random_json(False)
        }

        for i in range(100):
            payload = self._json.copy()
            for key in payload.keys():
                choice = random.choice(actions.keys)
                payload[key] = actions[choice]

        return payload

    # ASDASDASASDS

    def format_string(self):
        payload = self._json.copy()
        for key in payload.keys():
            if type(payload[key]) is str:
                payload[key] = get_random_format_string(64)
            elif type(copy[key]) is int:
                payload[key] = 429496730

        return json.dumps(copy).encode("UTF-8")

    def overflow_strings(self):
        payload = self._json.copy()
        for i in range(1000, 12000, 200):
            for key in payload.keys():
                try:
                    payload[key] += 1
                    payload[key] -= 1
                except TypeError:
                    if type(payload[key]) is str:
                        payload[key] = get_random_string(i)

            yield payload

    def integer_overflow_keys(self):
        keys = list(self._json.keys())
        for i in range(len(keys)):
            payload = self._json.copy()
            try:
                payload[keys[i]] += 1
                payload[keys[i]] = 429496729
            except TypeError:
                continue

            yield payload

    def integer_overflow_values(self):
        payload = self._json.copy()
        for key in copy.keys():
            try:
                payload[key] += 1
                payload[key] = 429496729
            except TypeError:
                continue

        return payload

    def generate_input(self):
        ##########################################################
        ##             Test valid (format) JSON data            ##        
        with alive_bar(2, dual_line=True, title='nullifying entries'.ljust(20)) as bar:
            yield self.nullify_json()            # nullify fields - zero and empty strings
            bar()

            yield self.all_null()
            bar()

        with alive_bar(2, dual_line=True, title='changing # fields'.ljust(20)) as bar:
            yield self.add_fields()
            bar()

            yield self.remove_fields()
            bar()

        with alive_bar(2, dual_line=True, title='swapping key/vals'.ljust(20)) as bar:
            yield self.swap_json_fields()        # swap fields
            bar()

            yield self.swap_json_values()        # swap values
            bar()

        # with alive_bar(2, dual_line=True, title='invalid values'.ljust(20)) as bar:
        #     yield self.wrong_type_values()  # swapping expected data types - works for high level and sub dictionaries
        #     bar()

        #     yield self.random_types()            # random type assignment
        #     bar()

        # with alive_bar(4, dual_line=True, title='swapping values/fields'.ljust(20)) as bar:
        #     yield self.format_string()      # format strings
        #     bar()

        #     yield self.overflow_strings()   # overflow strings
        #     bar()

        #     yield self.integer_overflow_keys()   # 
        #     bar()

        #     yield self.integer_overflow_values() # 
        #     bar()

        # with alive_bar(100, dual_line=True, title='invalid json'.ljust(20)) as bar:
        #     for _ in range(100):
        #         yield self.invalid_json()    # invalid json
        #         bar()

        # with alive_bar(100, dual_line=True, title='random json'.ljust(20)) as bar:
        #     for _ in range(100):
        #         yield self.random_json()     # lots of random fields and things
        #         bar()
