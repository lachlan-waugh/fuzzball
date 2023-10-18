class Strategy:
    def generate_input(self):
        yield b''
        yield b'1'

    def get_random_string(length):
        return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for _ in range(length))

    # TODO: fix
    def get_random_format_string(size):
        return ''.join(random.choice(['%x', '%c', '%d', '%p', '%s']) for _ in range(size))
