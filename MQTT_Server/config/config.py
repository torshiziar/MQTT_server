import influxdb_client

MQTT_USERNAME = 'leo'
MQTT_PASSWORD = 'Goldenhand76'
MQTT_HOST = 'localhost'
MQTT_PORT = 1883
MQTT_KEEP_ALIVE = 60

CELERY_BROKER_URL = 'redis://:uhCdS3wYmMKK6H8mdwg43yjQjtpvUPsaSjG2mg5ty3ywWk7w3WTSeTzMHUgDWG73@localhost:6379/1'
CELERY_result_backend = 'redis://:uhCdS3wYmMKK6H8mdwg43yjQjtpvUPsaSjG2mg5ty3ywWk7w3WTSeTzMHUgDWG73@localhost:6379/1'
CELERY_accept_content = ['application/json']
CELERY_task_serializer = 'json'
CELERY_result_serializer = 'json'
CELERY_timezone = "Asia/Tehran"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60


class InfluxClient:
    def __init__(self):
        self.client = influxdb_client.InfluxDBClient(
            url='http://smart.angizehco.com:8086',
            token='eDtNrp3b3iBeJeJ6mwwj6jquL3JFuBwb4O0d11nF3YXYGWopWbBvRavG6gHl3ECpsQJpAVU7FSIj7kOvqZalVg==',
            org='angizeh'
        )

    def connection(self):
        if self.client.ping():
            return self.client
        else:
            return self.__init__()


influx_client = InfluxClient()
