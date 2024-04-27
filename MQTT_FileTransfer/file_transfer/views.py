from django.shortcuts import render
from django.http import HttpResponse
import os
from mqtt_file_transfer.settings import PASSWORD, REDIS_PASSWORD
import redis
redis_client = redis.Redis(host='localhost', port=6379, password=REDIS_PASSWORD, decode_responses=True)

def get_file(request, folder, file_name):
    path = os.path.join('/var/www/update',folder, file_name)
    if file_name == 'bin_version.txt':
        password = request.META.get('HTTP_PASSWORD')
        hashed_serial_number = request.META.get('HTTP_HASH')
        if password == PASSWORD and redis_client.get(hashed_serial_number) is not None:
            client_id = request.META['REMOTE_ADDR']
            redis_client.set(client_id, 1)
            redis_client.expire(client_id, 60)
            try:
                with open(path, 'r') as file:
                    content = file.read()
                    return HttpResponse("<"+content+">",status=200)
            except FileNotFoundError:
                return HttpResponse('File not found.', status=404)  
        else:
            return HttpResponse('Authentication failed.' + hashed_serial_number, status=401)
        
    elif file_name == folder + ".bin":
            client_id = request.META['REMOTE_ADDR']
            if redis_client.get(client_id) is None:
                return HttpResponse('Authentication failed.', status=401)
            try:
                with open(path, 'rb') as file:
                    content = file.read()
                    return HttpResponse(content,status=200)
            except FileNotFoundError:
                return HttpResponse('File not found.', status=404)
            
    else:
        return HttpResponse('Cannot access the file.', status=400)
