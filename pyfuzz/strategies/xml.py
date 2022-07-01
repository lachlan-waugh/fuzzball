from alive_progress import *
import random
import copy

import xml.etree.ElementTree as ET
import xml
import re

class XMLStrategy:
    def __init__(self, input):
        try:
            print('[*] XML input detected, mutation started')
            self.xml = input.getroot()
            self.text = ET.tostring(self.xml)
        except Exception as e:
            print(f'[x] XMLStrategy.__init__ error: {e}')

    def _byteflip(self):
        bytes = bytearray(self.text.decode(), 'UTF-8')

        for i in range(0, len(bytes)):
            if random.randint(0, 20) == 1:
                bytes[i] ^= random.getrandbits(7)

        return bytes.decode('ascii')

    """
    Adds new nodes to the existing XML test input, which attempt to find
    a vulnerability in a certain part of the parsing of the document
    """
    def _add_node(self, functions):
        root = copy.deepcopy(self.xml)
        child = ET.SubElement(root, 'div')

        def _link_fstring():
            content = ET.SubElement(child, 'a')
            content.set('href', f'http://{"%s" * 0x10}.com')

        def _link_overflow():
            content = ET.SubElement(child, 'a')
            content.set('href', f'https://{"A" * 0x1000}.com')

        def _content_int_overflow():
            content = ET.SubElement(child, 'a')
            content.set('a', str(2 ** 31))
            content.set(str(2 ** 31), 'b')

        def _content_int_underflow():
            content = ET.SubElement(child, 'a')
            content.set('a', str(-2 ** 31))
            content.set(str(-2 ** 31), 'b')

        def _child_name_overflow():
            child.tag = 'A' * 0x1000

        def _child_name_fstring():
            child.tag = '%s' * 0x10

        switch = {
            0: _link_fstring,
            1: _link_overflow,
            2: _content_int_overflow,
            3: _content_int_underflow,
            4: _child_name_overflow,
            5: _child_name_fstring }

        for i in functions:
            try:
                switch.get(i)()
            except Exception as e:
                print(i)
                print(e)

        return root

    """
    Modifies the provided child node of the test_input and returns the new test input
        @child:     one of the children nodes of the test input
        @functions: an array of integers specifying which of the inner function to use
                    in order to change the data
    """
    def _mutate_node(self, child, functions):
        root = copy.deepcopy(self.xml)     # Don't overwrite the original text
        child = root.find(child.tag)        #

        # remove the given node from the root
        def _remove():
            root.remove(child)

        # duplicate the given node a random number of times at the end
        def _duplicate():
            for i in range(0, random.randint(75, 100)):
                root.append(copy.deepcopy(child))

        # create a line of children nodes starting from the provided child
        def _duplicate_recursively():
            _root = child
            for i in range(0, random.randint(75, 100)):
                _child = copy.deepcopy(_root)
                _child.tag = str(random.randint(0, 10000))
                _root.append(_child)
                _root = _root.find(_child.tag)

        # move the given node to the end of the input
        def _move():
            root.remove(root.find(child.tag))
            root.append(copy.deepcopy(child))

        # Add some unexpected info to the node
        def _add_info():
            child.set('%x' * 100, 'B' * 1000)
            child.set('A' * 1000, '%s' * 100)

        # remove all children (grandchildren of root if thats the correct term) from the child
        def _remove_child():
            for grandchild in child:
                child.remove(grandchild)

        switch = {
            0: _remove,
            1: _duplicate,
            2: _duplicate_recursively,
            3: _move,
            4: _add_info,
            5: _remove_child,
        }

        for i in functions:
            try:
                switch.get(i)()
            except Exception as e:
                print(i)
                print(e)

        return root

    """ 
    Treats the XML data as a string and replaces certain important parts with invalid data 
    """
    def _replace_text(self, functions):
        lines = self.text.decode()

        def _delete_open_tag():
            return re.sub('<[^>]+>', '', lines)

        def _delete_close_tag():
            return re.sub('</[^>]+>', '', lines)

        def _replace_numbers():
            return re.sub('\b[0-9]+\b', '1000000000', lines)

        def _replace_words():
            return re.sub('\b[a-zA-Z]+\b', 'A' * 0x1000, lines)

        def _replace_links():
            return re.sub('"https:[^"]+.com"', '%s' * 100, lines)

        switch = {
            0: _delete_open_tag,
            1: _delete_close_tag,
            2: _replace_numbers,
            3: _replace_words,
            4: _replace_links
        }

        for i in functions:
            try:
                lines = switch.get(i)()
            except Exception as e:
                print(i)
                print(e)

        return lines

    def generate_input(self):
        ##########################################################
        ##             Test valid (format) XML data             ##
        with alive_bar(12 * len(self.xml), dual_line=True, title='modifying nodes'.ljust(20)) as bar:
            # Modify the test input to still be in the correct format for XML
            for child in self.xml:
                for i in range(0, 6):
                    yield ET.tostring(self.mutate_node(child, [i])).decode()
                    bar()

                    yield ET.tostring(self.mutate_node(child, range(1, 6))).decode()
                    bar()

        with alive_bar(12, dual_line=True, title='adding nodes'.ljust(20)) as bar:
            # Create some new nodes and add these to the test input
            for i in range(0, 6):
                yield ET.tostring(self.add_node([i])).decode()
                bar()

                yield ET.tostring(self.add_node((range(0, 5)))).decode()
                bar()

        ##########################################################

        ##########################################################
        ##            Test invalid (format) XML data            ##
        with alive_bar(10, dual_line=True, title='replacing content'.ljust(20)) as bar:
            for i in range(0, 5):
                yield self.replace_text([i])
                bar()

                yield self.replace_text(range(0, 5))
                bar()

        with alive_bar(1000, dual_line=True, title='testing byteflips'.ljust(20)) as bar:
            for i in range(0, 1000):
                # test random bitflips on the test input
                yield self.byteflip()
                bar()

        with alive_bar(1000, dual_line=True, title='testing random data'.ljust(20)) as bar:
            for i in range(0, 1000):
                # test random input (invalid XML)
                yield get_random_string((i + 1) * 10)
                bar()
        ###########################################################