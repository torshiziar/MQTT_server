import paho.mqtt.client as mqtt
import re


def system_func(topic, payload):
    print("System Information Arrived")


def control_func(topic, payload):
    print("Control Information Arrived")


def client_func(topic, payload):
    print("Client Information Arrived")


def on_connect(client, userdata, flags, rc):
    status = {
        0: 'Connected',
        1: 'Connection refused: Bad protocol',
        2: 'Connection refused: Identifier rejected',
        3: 'Connection refused: Server unavailable',
        4: 'Connection refused: Bad username / password',
        5: 'Connection refused: Not authorized',
    }
    print(status.get(rc, "Invalid request"))
    client.subscribe("$CONTROL/#")
    client.subscribe("$SYS/#")
    client.subscribe("/angizeh/#")


def on_message(client, userdata, msg):

    topic = {
        bool(re.match("\$SYS(.*)", msg.topic)): system_func,
        bool(re.match("\$CONTROL(.*)", msg.topic)): control_func,
        bool(re.match("/angizeh/(.*)", msg.topic)): client_func,
    }
    topic.get(True, "Invalid request")(msg.topic, msg.payload.decode("UTF-8"))


client = mqtt.Client(client_id="test")
client.username_pw_set(username="leo", password="Goldenhand76")
client.on_connect = on_connect
client.on_message = on_message


client.connect(host="mqtt.angizehco.com", port=1883, keepalive=60)


# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
