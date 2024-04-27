#mosquitto_sub -v -h localhost -p 1883 -u leo -p Goldenhand76 -t /angizehco/VMN-A01-01-0005/#
import paho.mqtt.client as mqtt
import time
client=mqtt.Client()
client.username_pw_set("leo", "Goldenhand76")
print('Connectd_OK')

def on_connect(client,userdata,flags,rc):
    client.subscribe("/angizeh/+/+/+/+")
    print('Connected with result code: '+str(rc))



def on_message(client,userdata,msg):
    print(msg.topic+ " Approved" +str(msg.payload.decode('UTF-8')))
    # client.publish(msg.topic," Approved")
    pass


client.on_message = on_message
client.on_connect = on_connect
# client.on_disconnect = on_disconnect
# bayad dar localhost ejra shavad!
client.connect("localhost",port=1883,keepalive=80)
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




#
# # ----------- for Relay ------------------
# client.publish("/angizeh/VCN-A01-01-0002/12/1/Relay_08/status", "0")
# client.publish("/angizeh/VCN-A01-01-0002/12/01/Will", "Disconnected")
# #- --------------------------------------------
