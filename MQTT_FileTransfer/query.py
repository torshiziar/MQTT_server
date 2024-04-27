import hashlib
import redis
from mqtt_file_transfer.settings import REDIS_PASSWORD
redis_client = redis.Redis(host = 'localhost', port = 6379, password = REDIS_PASSWORD, decode_responses=True)
serial_number = "&?VMN-A01-01-0015?&"
hashed = hashlib.sha256(serial_number.encode()).hexdigest()
print(hashed)
print(redis_client.get(hashed))
