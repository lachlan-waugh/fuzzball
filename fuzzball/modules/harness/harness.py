from alive_progress import *
import multiprocessing as MP
from codes import get_response
from pwn import *

context.log_level = 'ERROR'

"""
# Used to communicate with the target program, handles
# > sending data to the target
# > determining the type of the crash
"""
class Harness:
    def __init__(self, binary):
        self.binary = binary

    def run(self, strategies):
        for inputs in strategies:
            with alive_bar(len(inputs['tests']), dual_line=True, title=inputs['title'].ljust(20)) as bar:
                for test_input in inputs['tests']:
                    try:
                        self.test_payload(test_input)
                    except Exception as e:
                        print(f'[x] Harness.run error: {e}')
                    bar()

    def test_payload(self, payload):
        if not isinstance(payload, str):
            try:
                payload = payload.decode()
            except (UnicodeDecodeError, AttributeError):
                exit('[x] ERROR @ test_payload: payload is not bytes or string')

        # Benchmarking shows that having more processes than cpu cores improves performace, maybe IO bound or waiting while polling
        if ((len(MP.active_children()) < (MP.cpu_count() * 2)) and (MP.current_process().name == 'MainProcess')):
            p = MP.Process(target=self.test_payload, args=(payload,))
            p.daemon = True
            p.start()

        else:
            self.run_test(payload)

    # 
    def run_test(self, payload):
        with process(self.binary) as p:
            # commented because payload doesn't needed to be unicoded
            # test payload is byte array
            p.send(payload.encode('UTF-8'))
            if self.check_segfault(p, payload):
                if MP.current_process().name != 'MainProcess':
                    try:
                        os.kill(os.getppid(), signal.SIGTERM)
                    except PermissionError:
                        sys.exit()
                else:
                    sys.exit()

    # 
    def check_segfault(self, p, output):
        p.proc.stdin.close()
        if p.poll(block=True) == -11:
            print('[+] planet successfully hacked... saving to bad.txt')
            with open('./bad.txt', 'w') as out:
                out.write(output)
            return True
        else:
            return False