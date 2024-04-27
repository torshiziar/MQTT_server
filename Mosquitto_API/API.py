import os
import re
import subprocess
from dotenv import load_dotenv
load_dotenv()

dynsec = ["mosquitto_ctrl", "-u", os.environ.get("USER"), "-P", os.environ.get("PASSWORD"), "dynsec"]


def createClient(username, password, client=None):
    bashCmd = dynsec + ["createClient", username, "-p", password]
    if client:
        bashCmd += ["-c", client]
    subprocess.Popen(bashCmd, stdout=subprocess.PIPE).communicate()
    return listClients()


def deleteClient(username):
    bashCmd = dynsec + ["deleteClient", username]
    subprocess.Popen(bashCmd, stdout=subprocess.PIPE).communicate()
    return listClients()


def setClientPassword(username, password):
    bashCmd = dynsec + ["setClientPassword", username, password]
    subprocess.Popen(bashCmd, stdout=subprocess.PIPE).communicate()
    return getClient(username)


def setClientId(username, clientid):
    bashCmd = dynsec + ["setClientId", username, clientid]
    subprocess.Popen(bashCmd, stdout=subprocess.PIPE).communicate()
    return getClient(username)


def getClient(username):
    bashCmd = dynsec + ["getClient", username]
    process = subprocess.Popen(bashCmd, stdout=subprocess.PIPE)
    return re.findall(r"(.*):(.*)", process.communicate()[0].decode("UTF-8"))


def listClients():
    bashCmd = dynsec + ["listClients"]
    process = subprocess.Popen(bashCmd, stdout=subprocess.PIPE)
    return re.findall(r"(\w+)", process.communicate()[0].decode("UTF-8"))


def enableClient(username):
    bashCmd = dynsec + ["enableClient", username]
    subprocess.Popen(bashCmd, stdout=subprocess.PIPE).communicate()
    return getClient(username)


def disableClient(username):
    bashCmd = dynsec + ["disableClient", username]
    subprocess.Popen(bashCmd, stdout=subprocess.PIPE).communicate()
    return getClient(username)


# print(createClient("dead", "123456", "789"))
print(getClient("dead"))
print(deleteClient("dead"))
print(listClients())
print(enableClient("test1"))
print(disableClient("test1"))
print("----------------------------------------")
print(setClientPassword("test1", "456789"))
print("----------------------------------------")
print(setClientId("test1", "89888"))
