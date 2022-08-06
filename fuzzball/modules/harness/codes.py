response_codes = {
    '134': 'abort',
    '-3': 'abort',
    '-6': 'abort',
    '-11': 'segfault',
    '-5': 'sigtrap',
    '0': 'exit'
}

def get_response(response_code):
    return return_codes.get(response_code, 'unknown')