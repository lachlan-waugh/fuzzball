import random
import copy
import re
import xml.etree.ElementTree as ET
import xml

from ..modules.helper import get_random_string, get_random_format_string

class XMLStrategy:
    def __init__(self, sample_input):
        try:
            print('[*] XML input detected, mutation started')
            self.xml = sample_input.getroot()
            self.text = ET.tostring(self.xml)
        except Exception as e:
            print(f'[x] XMLStrategy.__init__ error: {e}')

    def generate_input(self):
        ##########################################################
        ##             Test valid (format) XML data             ##
        # 12 * len(self.xml), 'modifying nodes'
        for child in self.xml: # Modify the test input to still be in the correct format for XML
            for i in range(0, 6):
                yield ET.tostring(self.mutate_node(child, [i])).decode()
                yield ET.tostring(self.mutate_node(child, range(1, 6))).decode()

        # 12, 'adding nodes'
        for i in range(0, 6): # Create some new nodes and add these to the test input
            yield ET.tostring(self.add_node([i])).decode()
            yield ET.tostring(self.add_node((range(0, 5)))).decode()

        ##########################################################
        ##            Test invalid (format) XML data            ##
        # 10, 'replacing content'
        for i in range(0, 5):
            yield self.replace_text([i])
            yield self.replace_text(range(0, 5))

        # 1000, 'testing byteflips'
        for i in range(0, 1000): # test random bitflips on the test input
            yield self.byteflip()

        # 1000, 'testing random data'
        for i in range(0, 1000): # test random input (invalid XML)
            yield get_random_string((i + 1) * 10)

    def byteflip(self):
        bytes = bytearray(self.text.decode(), 'UTF-8')

        for i in range(0, len(bytes)):
            if random.randint(0, 20) == 1:
                bytes[i] ^= random.getrandbits(7)

        return bytes.decode('ascii')

    """
    Adds new nodes to the existing XML test input, which attempt to find
    a vulnerability in a certain part of the parsing of the document
    """
    def add_node(self, functions):
        root = copy.deepcopy(self.xml)
        child = ET.SubElement(root, 'div')

        def link_fstring():
            content = ET.SubElement(child, 'a')
            content.set('href', f'http://{"%s" * 0x10}.com')

        def link_overflow():
            content = ET.SubElement(child, 'a')
            content.set('href', f'https://{"A" * 0x1000}.com')

        def content_int_overflow():
            content = ET.SubElement(child, 'a')
            content.set('a', str(2 ** 31))
            content.set(str(2 ** 31), 'b')

        def content_int_underflow():
            content = ET.SubElement(child, 'a')
            content.set('a', str(-2 ** 31))
            content.set(str(-2 ** 31), 'b')

        def child_name_overflow():
            child.tag = 'A' * 0x1000

        def child_name_fstring():
            child.tag = '%s' * 0x10

        switch = {
            0: link_fstring,
            1: link_overflow,
            2: content_int_overflow,
            3: content_int_underflow,
            4: child_name_overflow,
            5: child_name_fstring }

        for i in functions:
            try:
                switch.get(i)()
            except Exception as e:
                print(f'{i}: {e}')

        return root

    """
    Modifies the provided child node of the test_input and returns the new test input
        @child:     one of the children nodes of the test input
        @functions: an array of integers specifying which of the inner function to use
                    in order to change the data
    """
    def mutate_node(self, child, functions):
        root = copy.deepcopy(self.xml)     # Don't overwrite the original text
        child = root.find(child.tag)        #

        # remove the given node from the root
        def remove():
            root.remove(child)

        # duplicate the given node a random number of times at the end
        def duplicate():
            for i in range(0, random.randint(75, 100)):
                root.append(copy.deepcopy(child))

        # create a line of children nodes starting from the provided child
        def duplicate_recursively():
            root = child
            for i in range(0, random.randint(75, 100)):
                _child = copy.deepcopy(root)
                _child.tag = str(random.randint(0, 10000))
                root.append(_child)
                root = root.find(_child.tag)

        # move the given node to the end of the input
        def move():
            root.remove(root.find(child.tag))
            root.append(copy.deepcopy(child))

        # Add some unexpected info to the node
        def add_info():
            child.set('%x' * 100, 'B' * 1000)
            child.set('A' * 1000, '%s' * 100)

        # remove all children (grandchildren of root if thats the correct term) from the child
        def remove_child():
            for grandchild in child:
                child.remove(grandchild)

        switch = {
            0: remove,
            1: duplicate,
            2: duplicate_recursively,
            3: move,
            4: add_info,
            5: remove_child,
        }

        for i in functions:
            try:
                switch.get(i)()
            except Exception as e:
                print(f'{i}: {e}')

        return root

    """ 
    Treats the XML data as a string and replaces certain important parts with invalid data 
    """
    def replace_text(self, functions):
        lines = self.text.decode()

        def delete_open_tag():
            return re.sub('<[^>]+>', '', lines)

        def delete_close_tag():
            return re.sub('</[^>]+>', '', lines)

        def replace_numbers():
            return re.sub('\b[0-9]+\b', '1000000000', lines)

        def replace_words():
            return re.sub('\b[a-zA-Z]+\b', 'A' * 0x1000, lines)

        def replace_links():
            return re.sub('"https:[^"]+.com"', '%s' * 100, lines)

        switch = {
            0: delete_open_tag,
            1: delete_close_tag,
            2: replace_numbers,
            3: replace_words,
            4: replace_links
        }

        for i in functions:
            try:
                lines = switch.get(i)()
            except Exception as e:
                print(f'{i}: {e}')

        return lines