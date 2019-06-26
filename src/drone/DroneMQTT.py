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
        print('Inscrevendo-se no tópico "/buteco/topico" (%d)' % mid)
    else:
        client.bad_connection_flag=True
        print("Bad connection Returned code=",rc)


def on_subscribe(client, userdata, mid, granted_qos):
    print('Inscrito no tópico: %d' % mid)


def on_message(client, userdata, msg):
    print('Mensagem recebida no tópico: %s' % msg.topic)

    if msg.topic == '/buteco/topico':
        print('Conteúdo da mensagem: %s' % msg.payload)
    else:
        print('Tópico desconhecido.')


def loop():
    mqtt.Client.connected_flag=False#create flag in class
    mqtt.Client.bad_connection_flag=False #
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    # descomente esta linha caso seu servidor possua autenticação.
    # client.username_pw_set(MQTT_AUTH.user, MQTT_AUTH.pwd)
    #client.loop_start()

    try:
        client.connect(MQTT_ADDRESS, MQTT_PORT, MQTT_TIMEOUT)
        print("connected")
    except:
        print("connection failed")
        
    # while not client.connected_flag: #wait in loop
    #     print("In wait loop")
    #     print(client.connected_flag)
    #     time.sleep(1)

    client.loop_forever()

