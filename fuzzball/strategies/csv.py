import random
import csv

class CSVStrategy:
    def __init__(self, input):
        try:
            print('[*] CSV input detected, mutation started')
            self.delimiter = csv.Sniffer().sniff(input.read(1024)).delimiter
            input.seek(0)
            self.csv = [row for row in csv.reader(input, delimiter=self.delimiter)]
        except Exception as e:
            print(f'[x] CSVStrategy.__init__ error: {e}')

    def generate_input(self):
        # 12 * len(self.csv), 'modifying delimiters'
        yield remove_delimiters()   # invalid csv - remove all self.delimiters
        yield change_delimiters()   # change delimiters
        
        # 12 * len(self.csv), 'modify # of lines'
        yield lines_csv()   # check number of lines

        # 12 * len(self.csv), 'modify the fields'
        yield fields_csv()  # check fields - can return number of expected fields
        
        # 12 * len(self.csv), 'overflowing fields'
        yield overflow_fields() # overflowing fields with string
        
        # 12 * len(self.csv), 'format strings'
        yield format_string()   # string format
        
        # 12 * len(self.csv), 'modifying headers'
        yield change_header()   # change first line

        # 12 * len(self.csv), 'overflowing numbers'
        yield overflow_numbers()# overflow intergers

        # 12 * len(self.csv), 'random bit flips'
        for _ in range(0, 20):  # bit flipping
            yield byte_flip()

    def fields_csv(self):
        expected_field_no = -1
        for field_no in range(1, len(self.csv[0]) + 10):
            error = []
            for x in range(len(self.csv)):
                n = len(self.csv[x])
                if field_no < n:
                    for _ in range(0, n - field_no):
                        self.csv[x].pop()
                else:
                    for _ in range(n, field_no):
                        self.csv[x].append("A")
                try:
                    yield self.delimiter.join(self.csv[x])
                except:
                    if x > 0:
                        # assumption that sending multiple lines is accpeted no of fields
                        # assumption only one right number of fields
                        expected_field_no = x
                    break
                error.append(self.delimiter.join(self.csv[x]) + "\n")
            yield binary, b''.join(error)

        return expected_field_no

    # Check if a enough CSV lines will crash the program
    def lines_csv(self):
        for length in range(0, 1000, 100):
            error = []
            for l in range(0, length):
                if l < len(self.csv):
                    yield self.delimiter.join(self.csv[l])
                    error.append(self.delimiter.join(self.csv[l]) + "\n")
                else:
                    yield self.delimiter.join(self.csv[len(self.csv) - 1])
                    error.append(self.delimiter.join(self.csv[len(self.csv) - 1]) + "\n")

            yield b''.join(error)

    # remove all self.delimiters make file invalid
    def remove_delimiters(self):
        payload = b''
        for l in range(0, len(self.csv)):
            payload += b''.join(self.csv[l]) + "\n"
        return payload

    def change_delimiters(self):
        for x in [" ", ".", ",", "\t", "\n", "|", "/", "\\", ":", ";"]:
            payload = b''
            for l in range(0, len(self.csv)):
                payload += x.join(self.csv[l]) + "\n"

            yield payload

    def overflow_fields(self):
        for x in range(32, 1000, 32):
            payload = b''
            for l in range(0, len(self.csv)):
                if l == 1 and random.randrange(0, 1) == 1:
                    payload += self.delimiter.join(self.csv[0]) + "\n"
                    continue

                for w in self.csv[l]:
                    payload += "A" * x + self.delimiter

                payload = payload[:-1] + "\n"

            yield payload

    def format_string(self):
        for x in ["%p", "%s"]:
            payload = self.delimiter.join(self.csv[0]) + "\n"
            for l in range(1, len(self.csv)):
                for _ in self.csv[l]:
                    payload += x * 32 + self.delimiter
                payload = payload[:-1] + "\n"
            yield payload

        for x in ["%p", "%s"]:
            for l in range(0, len(self.csv)):
                for w in self.csv[l]:
                    payload += x * 32 + self.delimiter
                payload = payload[:-1] + "\n"

            yield payload

    def change_header(self):
        payload = b''
        for l in range(0, len(self.csv)):
            for _ in range(0, len(self.csv[l])):
                payload += get_random_string(25) + self.delimiter
            payload = payload[:-1] + "\n"

        yield payload

    # overflows
    def overflow_numbers(self):
        # zero
        payload = b''
        payload = self.delimiter.join(self.csv[0]) + "\n"
        firstline = len(payload)
        for l in range(1, len(self.csv)):
            for _ in range(0, len(self.csv[l])):
                payload += "0" + self.delimiter
            payload = payload[:-1] + "\n"

        yield payload
        yield payload[firstline:]

        # negative numbers
        payload = self.delimiter.join(self.csv[0]) + "\n"
        for l in range(1, len(self.csv)):
            for _ in range(0, len(self.csv[l])):
                payload += str(random.randrange(-4294967296, 0)) + self.delimiter
            payload = payload[:-1] + "\n"

        yield payload
        yield payload[firstline:]

        # high postive numbers
        payload = self.delimiter.join(self.csv[0]) + "\n"
        for l in range(1, len(self.csv)):
            for _ in range(0, len(self.csv[l])):
                payload += str(random.randrange(2147483648, (2 ** 65))) + self.delimiter
            payload = payload[:-1] + "\n"

        yield payload
        yield payload[firstline:]

        # float
        payload = self.delimiter.join(self.csv[0]) + "\n"
        for l in range(1, len(self.csv)):
            for _ in range(0, len(self.csv[l])):
                payload += str(random.random()) + self.delimiter
            payload = payload[:-1] + "\n"

        yield payload
        yield payload[firstline:]

    def byte_flip(self):
        payload = b''
        freq = random.randrange(1, 20)
        
        for l in range(0, len(self.csv)):
            for w in range(0, len(self.csv[l])):
                payload += self.csv[l][w] + self.delim
            payload = payload[:-1] + "\n"
        
        payload = bytearray(payload, "UTF-8")
        
        for i in range(0, len(payload)):
            if random.randint(0, freq) == 1:
                payload[i] ^= random.getrandbits(7)

        return payload