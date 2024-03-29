import random
import json
import Strategy from .strategy

from ..modules.helper import get_random_string, get_random_format_string

class JSONStrategy(Strategy):
    def __init__(self, input):
        print('[*] JSON input detected, mutation started')
        try:
            self.json = input
        except Exception as e:
            print(f'[x] JSONStrategy.__init__ error: {e}')

    def generate_input(self):
        ##########################################################
        ##             Test valid (format) JSON data            ##  
        # 2, 'nullifying entries'      
        yield self.nullify_json()            # nullify fields - zero and empty strings
        yield self.all_null()

        # 2, 'changing # fields'
        yield self.add_fields()
        yield self.remove_fields()

        # 2, 'swapping key/vals'
        yield self.swap_json_fields()        # swap fields
        yield self.swap_json_values()        # swap values

        # 2, 'invalid values'
        yield self.wrong_type_values()  # swapping expected data types - works for high level and sub dictionaries
        yield self.random_types()            # random type assignment

        # 4, 'swapping values/fields'
        yield self.format_string()      # format strings
        yield self.overflow_strings()   # overflow strings
        yield self.integer_overflow_keys()   # 
        yield self.integer_overflow_values() # 

        # 100, 'invalid json'
        for _ in range(100):
            yield self.invalid_json()    # invalid json

        # 100, 'random json'
        for _ in range(100):
            yield self.random_json()     # lots of random fields and things

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

    def nullify_json(self):
        payload = self.json.copy()
        for key in payload.keys():
            try:
                payload[key] += 1
                payload[key] = 0
            except TypeError:
                payload[key] = [] if (type(payload[key]) is dict) else ''

        return json.dumps(payload).encode('UTF-8')

    def all_null(self):
        payload = self.json.copy()
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
        for i in range(len(self.json.keys())):
            payload = json_object.copy()
            for x in range(i):
                # have chosen not to sort to have different subsets of fields removed (more random impact ?)
                del payload[list(self.json.keys())[x]]

            yield payload.encode('UTF-8')

    def swap_json_fields(self):
        fields = [ self.json[entry] for entry in self.json ]
        payload = self.json.copy()
        for entry in payload:
            payload[entry] = random.choice(fields)

        return payload

    # performs type swaps on ints and strings in root level of json dict
    def swap_json_values(self):
        for key in self.json:
            try:
                self.json[key] += 1
                self.json[key] = get_random_string(random.randint(2, 10))
            except TypeError:
                if type(self.json[key]) is dict:
                    self.json[key] = swap_json_values(self.json[key])
                else:
                    self.json[key] = random.randint(2, 10)
        return self.json

    # ADASDSA
    def wrong_type_values(self):
        return json.dumps(self.json.copy() + json.dumps(swap_json_values(self.json.copy())).encode("UTF-8")).encode("UTF-8")

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
            payload = self.json.copy()
            for key in payload.keys():
                choice = random.choice(actions.keys)
                payload[key] = actions[choice]

        return payload

    def format_string(self):
        payload = self.json.copy()
        for key in payload.keys():
            if type(payload[key]) is str:
                payload[key] = get_random_format_string(64)
            elif type(copy[key]) is int:
                payload[key] = 429496730

        return json.dumps(copy).encode("UTF-8")

    def overflow_strings(self):
        payload = self.json.copy()
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
        keys = list(self.json.keys())
        for i in range(len(keys)):
            payload = self.json.copy()
            try:
                payload[keys[i]] += 1
                payload[keys[i]] = 429496729
            except TypeError:
                continue

            yield payload

    def integer_overflow_values(self):
        payload = self.json.copy()
        for key in copy.keys():
            try:
                payload[key] += 1
                payload[key] = 429496729
            except TypeError:
                continue

        return payload
