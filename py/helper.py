from pwn import *
import xml.etree.ElementTree as ET
import multiprocessing as MP
import json
import csv

def simple_fuzz():
    yield b''

def get_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for i in range(length))

# TODO: fix
def get_random_format_string(size):
    return ''.join(random.choice(['%x', '%c', '%d', '%p', '%s']) for _ in range(size))

# 
