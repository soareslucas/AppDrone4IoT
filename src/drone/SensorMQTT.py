'''
Created on May 30, 2019

@author: lucassoares
'''


# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import sys
import time

from collections import namedtuple

Auth = namedtuple('Auth', ['user', 'pwd'])

MQTT_ADDRESS = '127.0.0.1'
# descomente esta linha para usar o servidor da Funda��o Eclipse.
# MQTT_ADDRESS = 'iot.eclipse.org'
MQTT_PORT = 1883
# descomente esta linha caso seu servidor possua autentica��o.
# MQTT_AUTH = Auth('login', 'senha')
MQTT_TIMEOUT = 600

if sys.version_info[0] == 3:
    input_func = input
else:
    input_func = input()


def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        print('Conectado. Resultado: %s' % str(rc))
        result, mid = client.subscribe('/buteco/topico')
        print('Inscrevendo-se no t�pico "/buteco/topico" (%d)' % mid)
    else:
        client.bad_connection_flag=True
        print("Bad connection Returned code=",rc)


def send_message(msg):
    mqtt.Client.connected_flag=False#create flag in class
    mqtt.Client.bad_connection_flag=False #
    broker="127.0.0.1"
    client = mqtt.Client()
    client.on_connect=on_connect  #bind call back function
    
    print("Connecting to broker ",broker)
    #while not client.connected_flag: #wait in loop

    #lient.loop_start()
    try:
        client.connect(MQTT_ADDRESS, MQTT_PORT, MQTT_TIMEOUT)
        #  client.connected_flag = True
    except:
        print("connection failed")
       # time.sleep(1)

    # while not client.connected_flag: 
    #      print("In wait loop")
    #      print(client.connected_flag)
    #      time.sleep(1)

    # print("in Main Loop")
    # client.loop_stop()    #Stop loop 
    # client.disconnect() # disconnect

    result, mid = client.publish('/buteco/topico', msg)
    print('Mensagem enviada ao canal: %d' % mid)


    
msg = input_func('Digite uma mensagem:\n')


send_message(msg)