'''
Created on May 30, 2019

@author: lucassoares
'''


# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import sys

from collections import namedtuple

MQTT_ADDRESS = '127.0.0.1'
MQTT_PORT = 1883
MQTT_TIMEOUT = 600

if sys.version_info[0] == 3:
    input_func = input
else:
    input_func = input()


def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        print('Conectado. Resultado: %s' % str(rc))
        result, mid = client.subscribe('/drone/sensores')
        print('Inscrevendo-se no t�pico "/drone/sensores" (%d)' % mid)
    else:
        client.bad_connection_flag=True
        print("Bad connection Returned code=",rc)


def send_message(msg):
    mqtt.Client.connected_flag=False#create flag in class
    mqtt.Client.bad_connection_flag=False #
    broker="127.0.0.1"
    client = mqtt.Client()
    client.on_connect=on_connect  #bind call back function
    
    print("Conectando ao broker ",broker)
    try:
        client.connect(MQTT_ADDRESS, MQTT_PORT, MQTT_TIMEOUT)
    except:
        print("Conexão Falhou!")

    result, mid = client.publish('/drone/sensores', msg)
    print('Mensagem enviada ao canal: %d' % mid)


    
msg = input_func('Digite um dado para o sensor :\n')


send_message(msg)