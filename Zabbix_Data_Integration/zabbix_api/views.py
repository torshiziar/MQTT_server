import requests
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
import re
import docker
import paho.mqtt.client as mqtt
import json
from zabbix_api_project.settings import ZABBIX_AGENT_CONTAINER_ID, ZABBIX_SERVER_IP_ADDRESS, ZABBIX_API_URL

client = docker.from_env()
zabbix_agent = client.containers.get(ZABBIX_AGENT_CONTAINER_ID)

def login(username, password):
    headers = {
        'Content-Type': 'application/json-rpc'
    }
    auth_payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "username": username,
            "password": password
        },
        "id": 1
    }
    response = requests.post(ZABBIX_API_URL, json=auth_payload, headers=headers)
    return response

class SendDataToItemAPIView(GenericAPIView):
    # publish subscribe
    # documentation
    def post(self, request):
        if 'username' not in request.data or 'password' not in request.data:
            return Response({"message":"please provide username and password."}, status=status.HTTP_401_UNAUTHORIZED)
        if 'data' not in request.data:
            return Response({"message":"please provide list of data values"}, status=status.HTTP_400_BAD_REQUEST)
        username = request.data["username"]
        password = request.data["password"]
        authentication = login(username,password)
        if 'result' in authentication.json():
            data = request.data['data']
            total = len(data)
            processed, failed, time_spent, sent, skipped = [0] * 5
            for datapoint in data:
                if 'host' not in datapoint or 'key' not in datapoint or 'value' not in datapoint:
                    return Response({"message":"please provide host, key and value for each data value."}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    stdout = str(zabbix_agent.exec_run(f'zabbix_sender -z {ZABBIX_SERVER_IP_ADDRESS} -s \"{datapoint["host"]}\" -k {datapoint["key"]} -o {datapoint["value"]}'))
                except:
                    return Response({"message":"internal server error. please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                try:
                    processed += int(re.search(r'processed: (\d+)', stdout).group(1))
                    failed += int(re.search(r'failed: (\d+)', stdout).group(1))
                    time_spent += float(re.search(r'seconds spent: ([\d.]+)', stdout).group(1))
                    sent += int(re.search(r'sent: (\d+)', stdout).group(1))
                    skipped += int(re.search(r'skipped: (\d+)', stdout).group(1))
                except AttributeError:
                    return Response({'message':f"error while trying to send values to zabbix. the first {sent} values were sent.","output":stdout},status=status.HTTP_400_BAD_REQUEST)
            response = {
                "total":total,
                "processed":processed,
                "failed":failed,
                "sent":sent,
                "skipped":skipped,
                "time_spent":time_spent
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(authentication.json(), status=authentication.status_code)
        

class SendDataToItemMQTT():
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("send_request")

    def on_message(self, client, userdata, msg):
        message = json.loads(msg.payload.decode())
        if 'username' not in message or 'password' not in message:
            self.client.publish("send_response", json.dumps({"message":"please provide username and password."}))
            return
        
        if 'data' not in message:
            self.client.publish("send_response", json.dumps({"message":"please provide list of data values"}))
            return
        
        username = message["username"]
        password = message["password"]
        authentication = login(username, password)
        
        if 'result' in authentication.json():
            data = message['data']
            total = len(data)
            processed, failed, time_spent, sent, skipped = [0] * 5
            for datapoint in data:
                if 'host' not in datapoint or 'key' not in datapoint or 'value' not in datapoint:
                    self.client.publish("send_response", json.dumps({"message":"please provide host, key and value for each data value."}))
                    return
                try:
                    stdout = str(zabbix_agent.exec_run(f'zabbix_sender -z {ZABBIX_SERVER_IP_ADDRESS} -s \"{datapoint["host"]}\" -k {datapoint["key"]} -o {datapoint["value"]}'))
                except:
                    self.client.publish("send_response", json.dumps({"message":"internal server error. please try again later."}))
                    return
                try:
                    processed += int(re.search(r'processed: (\d+)', stdout).group(1))
                    failed += int(re.search(r'failed: (\d+)', stdout).group(1))
                    time_spent += float(re.search(r'seconds spent: ([\d.]+)', stdout).group(1))
                    sent += int(re.search(r'sent: (\d+)', stdout).group(1))
                    skipped += int(re.search(r'skipped: (\d+)', stdout).group(1))
                except AttributeError:
                    self.client.publish('send_response', json.dumps({'message':f"error while trying to send values to zabbix. the first {sent} values were sent.","output":stdout}))
                    return
            response = {
                "total":total,
                "processed":processed,
                "failed":failed,
                "sent":sent,
                "skipped":skipped,
                "time_spent":time_spent
            }
            self.client.publish("send_response", json.dumps(response))
        else:
            self.client.publish("send_response", authentication.json())

    def __del__(self):
        self.client.loop_stop()
        self.client.disconnect()








# class LoginAPIView(GenericAPIView):
#     def post(self, request):
#         response = login(request.data['username'],request.data['password'])
#         return Response(response.json(), status=response.status_code)

# class GetHostAPIView(GenericAPIView):
#     def post(self, request):
#         headers = {
#             'Content-Type': 'application/json-rpc',
#             'Authorization': 'Bearer ' + str(request.META.get('HTTP_TOKEN'))
#         }
#         payload = {
#             "jsonrpc": "2.0",
#             "method": "host.get",
#             "params": {
#                 "output": [
#                     "hostid",
#                     "host"
#                 ],
#                 "selectInterfaces": [
#                     "interfaceid",
#                     "ip"
#                 ]
#             },
#             "id": request.data["id"]
#         }
#         response = requests.post(ZABBIX_API_URL, json=payload, headers=headers)
#         return Response(response.json(), status=response.status_code)
    
# class CreateItemAPIView(GenericAPIView):
#     def post(self, request):
#         headers = {
#             'Content-Type': 'application/json-rpc',
#             'Authorization': 'Bearer ' + str(request.META.get('HTTP_TOKEN'))
#         }
#         payload = {
#             'jsonrpc': '2.0',
#             'method': 'item.create',
#             'params': {
#                 'name': request.data["item_name"],
#                 'key_': request.data["key"],
#                 'hostid': request.data["host_id"],
#                 "type": request.data["type"],
#                 "value_type": request.data["value_type"],
#                 "interfaceid": request.data["interfaceid"],
#                 "delay": request.data["delay"]
#             },
#             'id': 1,
#         }
#         response = requests.post(ZABBIX_API_URL, json=payload, headers=headers)
#         return Response(response.json(), status=response.status_code)
    
# class UpdateItemAPIView(GenericAPIView):
#     def post(self, request):
#         headers = {
#             'Content-Type': 'application/json-rpc',
#             'Authorization': 'Bearer ' + str(request.META.get('HTTP_TOKEN'))
#         }
#         payload = {
#         'jsonrpc': '2.0',
#         'method': 'item.update',
#         'params': {
#             'itemid': request.data["item_id"],
#             # 'additive': 1,
#             'value_type': 0,
#             'data': request.data["value"]
#         },
#         'id': 1,
#     }
#         response = requests.post(ZABBIX_API_URL, json=payload, headers=headers)
#         return Response(response.json(), status=response.status_code)
    
        
    