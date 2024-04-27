import paho.mqtt.client as mqtt
from config.config import MQTT_USERNAME, MQTT_PASSWORD, MQTT_HOST, MQTT_PORT, MQTT_KEEP_ALIVE
from tasks import message
import time


def on_connect(client, userdata, flags, rc):
    client.subscribe("/angizeh/+/+/+/+")
    print("Connected with result code: " + str(rc))


def on_message(client, userdata, msg):
    if msg.topic == '/angizeh/doorlock':
        if msg.payload.decode("UTF-8") == "D3 4C E9 14":
            client.publish(msg.topic, "APPROVED")
        elif len(msg.payload.decode("UTF-8").split(" ")) == 4:
            client.publish(msg.topic, "REJECTED")
    try:
        message.delay(msg.topic, msg.payload.decode("UTF-8"))
    except UnicodeDecodeError as e:
        print(e)


def on_disconnect(client, userdata, rc):
    client.unsubscribe('/angizeh/#')
    print("Disconnected with result code: " + str(rc))


client = mqtt.Client(client_id="MQTT_Server")
client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)

client.on_message = on_message
client.on_connect = on_connect
client.on_disconnect = on_disconnect

client.connect(host=MQTT_HOST, port=MQTT_PORT, keepalive=MQTT_KEEP_ALIVE)
client.reconnect_delay_set(1, 120)

while True:
    if not client.is_connected():
        try:
            client.reconnect()
            client.loop_forever(timeout=1.0, max_packets=1, retry_first_connection=True)
        except ConnectionRefusedError:
            time.sleep(1)
            pass
    client.loop(timeout=10)


    # db = postgre_connect(None)
    # cur = db.cursor()
    # sql = "SELECT * FROM actuator a WHERE a.set != a.current"
    # cur.execute(sql)
    # result = cur.fetchall()
    # for r in result:
    #     command = r[2]
    #     print(command)
    # db.close()
    # influx_connect()
    # db = postgre_connect()
    # cur = db.cursor()
    #
    # cur.execute("""SELECT * FROM devices_devicemanager""")
    # for table in cur.fetchall():
    #     sql = """UPDATE devices_devicemanager SET is_online = %s WHERE device = %s"""
    #     print(table)
    #     cur.execute(sql, ("False", table[2]))
    # db.commit()
    # cur.close()

    # print(db.get_list_continuous_queries())
    # print(db.get_list_database())
    # print(db.get_list_measurements())
    # print(db.get_list_users())
    # print(db.get_list_retention_policies('ZIRSAKHT'))
    # print(db.ping())
