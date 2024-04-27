import paho.mqtt.client as mqtt
from celery import Celery
from celery.schedules import crontab
from config.config import influx_client, MQTT_HOST, MQTT_PORT, MQTT_KEEP_ALIVE
from influxdb_client.client.write_api import SYNCHRONOUS
import influxdb_client
from datetime import datetime
import pytz

app = Celery('tasks')
app.config_from_object('config.config', namespace='CELERY')


@app.task(name='message')
def message(topic, msg):
    if topic.split('/')[5] == "Will":
        pass
    else:
        try:
            value = int(msg)
        except ValueError:
            value = float(msg)
        store_influxdb(topic, value)


@app.task(name='publish_time')
def publish_time():
    time = datetime.now(pytz.timezone("Asia/Tehran")).strftime("%Y,%m,%d-%H:%M:%S")
    client = mqtt.Client(client_id="publish_time")
    client.username_pw_set(username="celery", password="xXS5Kab5v3JPbpQc")
    client.connect(host=MQTT_HOST, port=MQTT_PORT, keepalive=MQTT_KEEP_ALIVE)
    client.publish('/angizeh/time', time)
    client.disconnect()
    return time


@app.task(name='store_influxdb')
def store_influxdb(topic, value):
    owner, gateway, node, measurement = topic.split('/')[2:6]
    try:
        client = influx_client.connection()
        write_api = client.write_api(write_options=SYNCHRONOUS)
        record = influxdb_client.Point(f"{measurement}").tag("gateway", f"{gateway}").tag("node", f"{node}").field(f"{owner}", value)
        write_api.write(bucket='IoT', record=record)
        return True
    except OSError:
        return "Cant connect to broker"


@app.task(bind=True)
def debug_task(self):
    print(f'Request:{self.request!r}')


app.conf.beat_schedule = {
    'publish_time': {
        'task': 'publish_time',
        'schedule': crontab(minute='*/1',),
        'args': ()
    },
}
