import redis
import hashlib
from mqtt_file_transfer.settings import REDIS_PASSWORD
import argparse
# serial_numbers = ["VCN-A01-01-0001","VCN-A01-01-0004","VMN-A01-01-0002","VMN-A01-01-0005","VMN-A01-01-0008","VCN-A01-01-0002","VCN-A01-01-0005","VMN-A01-01-0003","VMN-A01-01-0006","VMN-A01-01-0015","VCN-A01-01-0003","VMN-A01-01-0001","VMN-A01-01-0004","VMN-A01-01-0007","VMN-A01-01-0012"]
redis_client = redis.Redis(host='localhost', port=6379, password=REDIS_PASSWORD, decode_responses=True)
def add_batch():
    serial_numbers = []
    while True:
        serial_num = input("Please Input a Serial Number (Type \"end\" if you have already entered the serial numbers you need): ")
        if serial_num == "end":
            break
        confirmation = input(f"Are you sure you want to add serial number {serial_num} to database?\nType \"Y\" for Yes. Type anything else for No: ")
        if confirmation == "Y":
            serial_numbers.append(serial_num)
    for serial_number in serial_numbers:
        if redis_client.get(serial_number) is not None:
            redis_client.delete(serial_number)
        hashed = hashlib.sha256(serial_number.encode()).hexdigest()
        if redis_client.get(hashed) is not None:
            redis_client.delete(hashed)
        salted = "&?" + serial_number + "?&"
        hashed_salted = hashlib.sha256(salted.encode()).hexdigest()
        if redis_client.get(hashed_salted) is None:
            redis_client.set(hashed_salted,serial_number)
            print("added " + serial_number)
    print("Done!")

def add_serial_number(serial_number):
    if redis_client.get(serial_number) is not None:
        redis_client.delete(serial_number)
    hashed = hashlib.sha256(serial_number.encode()).hexdigest()
    if redis_client.get(hashed) is not None:
        redis_client.delete(hashed)
    salted = "&?" + serial_number + "?&"
    hashed_salted = hashlib.sha256(salted.encode()).hexdigest()
    if redis_client.get(hashed_salted) is None:
        redis_client.set(hashed_salted,serial_number)
        print("added " + serial_number)

def get_all():
    keys = redis_client.keys('*')
    all_values = []
    for key in keys:
        value = redis_client.get(key)
        if value:
            all_values.append(value)
    print(str(all_values)[1:-1])

def delete_serial_number(serial_number):
    salted = "&?" + serial_number + "?&"
    key_to_delete = hashlib.sha256(salted.encode()).hexdigest()
    result = redis_client.delete(key_to_delete)
    if result == 1:
        print(f"The serial number '{serial_number}' has been successfully deleted.")
    else:
        print(f"The serial number '{serial_number}' does not exist in the database.")
    

parser = argparse.ArgumentParser(description='Command-line interface for your functions')
subparsers = parser.add_subparsers(dest='subparser_name')
parser_add = subparsers.add_parser('add')
parser_add.add_argument('serial_number', type=str, help='Serial Number')

parser_delete = subparsers.add_parser('delete')
parser_delete.add_argument('serial_number', type=str, help='Serial Number')

parser_get = subparsers.add_parser('get_all')

args = parser.parse_args()

if args.subparser_name == 'add':
    add_serial_number(args.serial_number)
elif args.subparser_name == 'delete':
    delete_serial_number(args.serial_number)
elif args.subparser_name == 'get_all':
    get_all()
else:
    print("Invalid command")
