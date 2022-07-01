from pwn import *
import csv
import json
import xml.etree.ElementTree as ET
import multiprocessing as MP

sys.path.append('./modules')
from json_fuzzer import JSONFuzzer
from csv_fuzzer import CSVFuzzer
from xml_fuzzer import XMLFuzzer
from txt_fuzzer import TXTFuzzer

def simple_fuzz():
    yield ''

def get_fuzzer(file):
    try:
        file.seek(0)
        jsonObj = json.load(file)
        return JSONFuzzer
    except ValueError as e:
        pass

    try:
        file.seek(0)
        csvObj = csv.Sniffer().sniff(file.read(1024))
        if (csvObj.delimiter in [csv.excel.delimiter, csv.excel_tab.delimiter]):
            return CSVFuzzer
    except csv.Error:
        pass

    try:
        file.seek(0)
        xmlObj = ET.parse(file)
        return XMLFuzzer
    except Exception:
        pass

    return TXTFuzzer

def check_segfault(p, output):
    p.proc.stdin.close()
    if p.poll(block=True) == -11:
        print("Found something... saving to file bad.txt")
        with open("./bad.txt", "w") as out:
            out.write(output)
        return True
    else:
        return False

def get_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for i in range(length))

def test_payload(binary, payload):
    # Prepare payload for sending
    # Send binary and payload into a pool
    if not isinstance(payload, str):
        try:
            payload = payload.decode()
        except (UnicodeDecodeError, AttributeError):
            exit("payload is not a byte string")

    # Benchmarking shows that having more processes than cpu cores improves performace, maybe IO bound or waiting while polling
    if ((len(MP.active_children()) < (MP.cpu_count() * 2)) and (MP.current_process().name == "MainProcess")):
        p = MP.Process(target=test_payload, args=(binary, payload))
        p.daemon = True
        p.start()

    else:
        run_test(binary, payload)

def run_test(binary, payload):
    with process(binary) as p:
        # commented because payload doesn't needed to be unicoded
        # test payload is byte array
        p.send(payload)
        if check_segfault(p, payload):
            if MP.current_process().name != "MainProcess":
                try:
                    os.kill(os.getppid(), signal.SIGTERM)
                except PermissionError:
                    sys.exit()
            else:
                sys.exit()