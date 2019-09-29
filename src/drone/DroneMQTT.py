'''
Created on May 30, 2019

@author: lucassoares
'''


# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import sys
import requests

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
        print('Inscrevendo-se no tópico "/drone/sensores" (%d)' % mid)
    else:
        client.bad_connection_flag=True
        print("Bad connection Returned code=",rc)


def on_subscribe(client, userdata, mid, granted_qos):
    print('Inscrito no tópico: %d' % mid)


def on_message(client, userdata, msg):
    print('Mensagem recebida no tópico: %s' % msg.topic)

    if msg.topic == '/drone/sensores':
        dados = ('%s' % msg.payload)
        print(dados)
        r = requests.get("http://127.0.0.1:5000/setDados?data="+dados) 
        
        print(r.status_code)
        client.loop_stop()  
        
    else:
        print('Tópico desconhecido.')


def loop():
    
    mqtt.Client.connected_flag=False#create flag in class
    mqtt.Client.bad_connection_flag=False #
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    client.loop_start()

    try:
        client.connect(MQTT_ADDRESS, MQTT_PORT, MQTT_TIMEOUT)
        print("connected")
    except:
        print("connection failed")
          