#mosquitto_sub -v -h localhost -p 1883 -u leo -p Goldenhand76 -t /angizehco/VMN-A01-01-0005/#
#mosquitto_pub -v -h localhost -p 1883 -u leo -p Goldenhand76 -t /angizehco/VCN-A01-01-0003/Will -m "Dis"


import paho.mqtt.client as mqtt
import redis
from datetime import datetime 
import threading
import re
import time
import logging


logging.basicConfig(filename='/var/www/MQTT_Server/Path_Willmessages.log',level=logging.DEBUG)


DELAY=60 # seconds
r=redis.Redis(host='localhost',port=6379,db=3,password='uhCdS3wYmMKK6H8mdwg43yjQjtpvUPsaSjG2mg5ty3ywWk7w3WTSeTzMHUgDWG73')
# import numpy
def thread_checkWill(client):
    while(True):
        try:
            all_keys=r.keys()

            
            foundWillmessages=[key.decode() for key in all_keys if 'Will' in key.decode() and '/Will_0' not in key.decode()]  # hameye Will ha
            # foundWillmessages=[key.decode() for key in all_keys if 'Will' in key.decode() and '-0/Will' not in key.decode()]  # hameye Will ha

            foundWillmessages=list(set(foundWillmessages))
            
            for item in foundWillmessages:
                
                foundNOTWILLmessage=[key.decode() for key in all_keys if re.match(item.replace('Will',''),key.decode()) and 'Will' not in key.decode()]  # hameye Will ha
                

                if (len(foundNOTWILLmessage)>0):
                    #== Check time
                    time_will=datetime.fromisoformat(r.get(item).decode())
                    maxTimestamp=max([datetime.fromisoformat(r.get(key).decode()) for key in foundNOTWILLmessage])

                
                    # Get new message
                    if (maxTimestamp>time_will):
                        logging.info('++++++++not send Will   '+ foundNOTWILLmessage[0])
                        r.delete(item)
                    else: # no new message
                        if (datetime.now()-time_will).seconds>DELAY:  # wait until DELAY (send Will message frequently)
                            client.publish(item.replace('/Will','/Will_0'),"Disconnect")
                            
                            logging.info('--------send Will message  (Delay '+ str((datetime.now()-time_will).seconds)+') ' + item.replace('/Will','/Will_0'))                           
                            r.delete(item)

                    # if (maxTimestamp>time_will):  # agar will message amad, DELAY second ghablesh ya badesh notWill nayad-> Will ersal mishavad
                    #     spendTime=(maxTimestamp-time_will).seconds
                    # else:
                    #     spendTime=(time_will-maxTimestamp).seconds

                    # if spendTime>=DELAY:
                    #     # send will message 
                    #     client.publish(item.replace('/Will','-0/Will'),"Disconnect")

                    #     print('--------send Will message  (Delay '+ str((maxTimestamp-time_will).seconds)+') ' + item.replace('/Will','-0/Will'))
                    # else:
                    #     print('++++++++not send Will   '+ foundNOTWILLmessage[0])
                # else:
                    # r.delete(item)
            # for item in foundWillmessages:
            #     r.delete(item)
                
                # topics_willmessages=[key for key in foundWillmessages if 'Will' not in key]
            time.sleep(5)
        except Exception as e:
            # print(str(e))
            time.sleep(5)
            continue




client=mqtt.Client()
client.username_pw_set("leo", "Goldenhand76")
# print('Connectd_OK')

def on_connect(client,userdata,flags,rc):
    # client.subscribe("/angizeh/+/+/+/+")
    # client.subscribe("/angizeh/+/+/")
    client.subscribe('/angizeh/+/+/+/+/+')
    client.subscribe('/angizeh/+/+/+/+')
    client.subscribe('/angizeh/+/+/+')
    client.subscribe('/angizeh/+/+/+', 1)
    client.subscribe('/angizeh/+/+/+/+', 1)
    client.subscribe('/angizeh/+/+/+/+/+', 1)


    # print('Connected with result code: '+str(rc))
    th=threading.Thread(target=thread_checkWill,args=(client,))
    th.start()


def on_message(client,userdata,msg):
    dt=datetime.now()
    dt_str=dt.isoformat()
    if ('/Will_0' not in msg.topic):
        r.set(msg.topic,dt_str)
    # print(msg.topic+ " Approved    " +str(msg.payload.decode('UTF-8')))
    # client.publish(msg.topic," Approved")
    # pass


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




#=== For test 
# panel moavengh --> vase 0005  --> humidity --> will topic and will alt topic ra taghir dadim!!!!
#mosquitto_pub  -h localhost -p 1883 -u leo -P Goldenhand76 -t /angizeh/VCN-A01-01-0005/12/1/Will -m "Disconnected"
#mosquitto_pub  -h localhost -p 1883 -u leo -P Goldenhand76 -t /angizeh/VCN-A01-01-0005/12/1/rr -m "Disconnected"
#mosquitto_pub  -h localhost -p 1883 -u leo -P Goldenhand76 -t /angizeh/VMN-A01-01-0002/01/Will -m "Disconnected"



#--- example for VMN   ( ??? OK mishavad)  
# توضیحات اینکهُ در اینتدا ویلل را بر می دارد و به دنیال بقیه عبارت در کل پیام ها می گردد. یعنی میشه همه سنسورها.
# در صورت اینکه یک سنسور داده ارسال کرده باشد از ارسال ویلل منصرف می شود ولی در صورتی که هیچ سنسوری داده ارسال نکرده باشد پیام ویلل ارسال می شود که سبب می گردد همه سنسورها غیر فعال شوند.
# /angizeh/VMN-A01-01-0004/06/Will
# /angizeh/VMN-A01-01-0005/06/LUX 38426.00


#--- example for VCN  (?? OK mishavad!)
#/angizeh/VCN-A01-01-0005/12/1/Will 
#/angizeh/VCN-A01-01-0001/12/1/Relay_01
#/angizeh/VCN-A01-01-0001/12/1/Relay_03


# panel Moaven
# monitor # mosquitto_sub -v -h localhost -p 1883 -u leo -P Goldenhand76 -t /angizeh/VMN-A01-01-0005/#
#disbale #mosquitto_pub  -h localhost -p 1883 -u leo -P Goldenhand76 -t /angizeh/VMN-A01-01-0005/06/Will -m "Disconnected"