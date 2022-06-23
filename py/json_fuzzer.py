import sys
import os
from pwn import *
import json
import random
from helper import *

# performs type swaps on ints and strings in root level of json dict
def swap_json_values(json_object):
    for key in json_object:
        try:
            json_object[key] += 1
            json_object[key] = get_random_string(randint(2, 10))
        except TypeError:
            if type(json_object[key]) is dict:
                json_object[key] = swap_json_values(json_object[key])
            else:
                json_object[key] = randint(2, 10)
    return json_object

def change_field_amount_json(binary, json_object):
    jsonEntriesCount = len(json_object.keys())

    # removing different entries amount of entries
    for i in range(jsonEntriesCount):
        copy = json_object.copy()
        for x in range(i):
            del copy[
                list(json_object.keys())[x]
            ]  # have chosen not to sort to have different subsets of fields removed (more random impact ?)
        payload = json.dumps(copy).encode("UTF-8")
        test_payload(binary, payload)

    # add additional entries
    for i in range(25):
        copy = json_object.copy()
        for x in range(i):
            chance = randint(0, 1)
            if chance:
                copy[get_random_string(10)] = get_random_string(5)
            else:
                copy[get_random_string(10)] = randint(0, 262144)
        payload = json.dumps(copy).encode("UTF-8")
        test_payload(binary, payload)

def deep_nested_json(dictionary, length):
    if length == 0:
        return randint(0, 1024)
    else:
        dictionary[get_random_string(8)] = deep_nested_json({}, length - 1)
    return dictionary

def wrong_type_values_json():
    copy = json_input.copy()
    payload = b""
    payload += json.dumps(swap_json_values(copy)).encode("UTF-8")
    test_payload(binary, payload)

def get_random_format_string(size):
    format_string_identifiers = ["%x", "%c", "%d", "%p"]
    payload = ""
    for i in range(size):
        payload += random.choice(format_string_identifiers)
    return payload

def overflow_strings_json():
    copy = json_input.copy()
    for i in range(1000, 12000, 200):
        for key in copy.keys():
            try:
                copy[key] += 1
                copy[key] -= 1
            except TypeError:
                if type(copy[key]) is str:
                    copy[key] = get_random_string(i)
        payload = json.dumps(copy).encode("UTF-8")
        test_payload(binary, payload)

def overflow_integers_json():
    keys = list(json_input.keys())
    for i in range(len(keys)):
        copy = json_input.copy()
        try:
            copy[keys[i]] += 1
            copy[keys[i]] = 429496729
        except TypeError:
            continue
        payload = json.dumps(copy).encode("UTF-8")
        test_payload(binary, payload)
    copy = json_input.copy()
    for key in copy.keys():
        try:
            copy[key] += 1
            copy[key] = 429496729
        except TypeError:
            continue
    payload = json.dumps(copy).encode("UTF-8")
    test_payload(binary, payload)

def format_string_fuzz():
    copy = json_input.copy()
    for key in copy.keys():
        if type(copy[key]) is str:
            copy[key] = get_random_format_string(64)
        elif type(copy[key]) is int:
            copy[key] = 429496730
    payload = json.dumps(copy).encode("UTF-8")
    test_payload(binary, payload)

def swap_json_fields():
    fields = []
    for entry in json_input:
        fields.append(json_input[entry])
    copy = json_input.copy()
    for entry in copy:
        copy[entry] = random.choice(fields)
    payload = json.dumps(copy).encode("UTF-8")
    test_payload(binary, payload)

def random_types():
    actions = {
        "string": get_random_string(randint(16, 12000)),
        "boolean": random.choice([True, False]),
        "int": randint(-429496729, 429496729),
        "none": None,
        "list": list(range(randint(-64, 0), randint(0, 64))),
        "float": random.uniform(-128, 128),
        "dict": random_json(False)
    }

    for i in range(100):
        payload = json_input.copy()
        for key in payload.keys():
            choice = random.choice(actions.keys)
            payload(key) = actions[choice]

    return json.dumps(payload).encode('UTF-8')

class JSONFuzzer:
    def __init__(self, input):
        try:
            self._json = json.load(input)
        except Exception as e:
            print(e)

    def invalid_json(self):
        return [ chr(random.randrange(0, 255)) for x in range(0, 1000) ].encode('UTF-8')

    def random_json():
        d = {}

        chances = [None, get_random_string(6), randint(0, 1024), deep_nested_json({}, 32)]
        for i in range(100):
            d[get_random_string(5)] = chances[randint(0, 3)]

        return json.dumps(d).encode('UTF-8')

    def nullify_json():
        payload = json_input.copy()
        # set inputs to 0 equivelants
        for key in payload.keys():
            try:
                copy[key] += 1
                copy[key] = 0
            except TypeError:
                if type(copy[key]) is dict:
                    copy[key] = []
                else:
                    copy[key] = ""
        payload = json.dumps(copy).encode("UTF-8")
        test_payload(binary, payload)
        # set all to null
        copy = json_input.copy()

        copy[key] = None for key in copy.keys()
        
        return json.dumps(copy).encode("UTF-8")

    def generate_input(self):
        ##########################################################
        ##             Test valid (format) XML data             ##
        yield ""    # check empty payload
        
        yield invalid_json()    # invalid json
        yield random_json()     # lots of random fields and things

        # actual fuzzing
        yield nullify_json()            # nullify fields - zero and empty strings
        yield change_field_amount_json()# create extra fields & delete some
        yield wrong_type_values_json()  # swapping expected data types - works for high level and sub dictionaries
        yield format_string_fuzz()      # format strings
        yield overflow_strings_json()   # overflow strings
        yield overflow_integers_json()  # overflow integers
        yield swap_json_fields()        # swap fields
        yield random_types()            # random type assignment

def json_fuzzer(binary, inputFile):
    context.log_level = 'WARNING'

    with open(inputFile) as input:
        for test_input in JSONFuzzer(input).generate_input():
            try:
                test_payload(binary, test_input)
            except Exception as e:
                print(e)