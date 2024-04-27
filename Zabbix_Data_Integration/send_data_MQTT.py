import paho.mqtt.client as mqtt
import time
import docker

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEP_ALIVE = 60
MQTT_USERNAME = "leo"
MQTT_PASSWORD = "Goldenhand76"
ZABBIX_AGENT_CONTAINER_ID = '87b8c9a8b526'
ZABBIX_SERVER_IP_ADDRESS = "185.252.28.58"
client = docker.from_env()
zabbix_agent = client.containers.get(ZABBIX_AGENT_CONTAINER_ID)
items = ["Temperature", "Moisture","Humidity", "EC", "POT", "LUX", "PHOS", "PH", "CO2"] # Update This List

def on_connect(client, userdata, flags, rc):
    client.subscribe("/angizeh/#")
    print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
    topic = str(msg.topic).split('/')
    if any(items) == topic[-1]:
        value = msg.payload.decode("utf-8")
        key = topic[-1].lower() + ".key"
        host = topic[1]
        zabbix_agent.exec_run(f'zabbix_sender -z {ZABBIX_SERVER_IP_ADDRESS} -s \"{host}\" -k {key} -o {value}')
        print("value sent to zabbix: " + str(msg.payload))

def on_disconnect(client, userdata, rc):
    client.unsubscribe('/angizeh/#')
    print("Disconnected with result code: " + str(rc))

client = mqtt.Client(client_id="MQTT_Zabbix")
client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)
client.on_message = on_message
client.on_connect = on_connect
client.on_disconnect = on_disconnect

client.connect("localhost", 1883, 60)
while True:
    if not client.is_connected():
        try:
            client.reconnect()
            client.loop_forever(timeout=1.0, max_packets=1, retry_first_connection=True)
        except ConnectionRefusedError:
            time.sleep(1)
            pass
    client.loop(timeout=10)