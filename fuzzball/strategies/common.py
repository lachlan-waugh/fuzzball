class CommonStrategy:
    def generate_input(self):
        yield b''
        yield b'1'

    def byteflip(self, text):
        bytes = bytearray(text.decode(), 'UTF-8')

        for i in range(0, len(bytes)):
            if random.randint(0, 20) == 1:
                bytes[i] ^= random.getrandbits(7)

        return bytes.decode('ascii')