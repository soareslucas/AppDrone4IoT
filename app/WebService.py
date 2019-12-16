'''
Created on Jun 1, 2019

@author: lucassoares
'''
from flask import Flask
from flask import request
import numpy as np
import app.Otimizacao as otim
import app.Sensor as Sensor
import app.Site as Site
import app.TabuSearch as tabu


#import app.DroneMQTT as ServiceSchedule
from threading import Thread
import os
import random
import sys
import math
from flask import Response

app = Flask(__name__)
started = 'false'
latitude = 48.8790
longitude = 2.3674

textFile = ''

# Autonomia em J |||  (59940 - 1500 mAh - 11.1V )   (99900 - 2500 mAh - 11.1V ) (159840 - 4000 mAh - 11.1V )
autonomy = 59940

idSite = 1

def generate_random_data(lat, lon, num_rows,idSite):
    sitesTemp = []
    for _ in range(num_rows):
        dec_lat = random.random()/10000
        dec_lon = random.random()/10000
        site = Site.Site(str(idSite), (lat+dec_lat, lon+dec_lon, np.random.randint(1,20)) , "false")
        idSite += 1
        sitesTemp.append(site)
    return sitesTemp

def generate_file_data():
        global textFile
        file = open("flightplan.txt", "w") 
        file.write(textFile) 
        return file

if( started == 'false'):
    sitesList = generate_random_data(latitude, longitude, 3, idSite)
    sensor = Sensor.Sensor(1,"umidade",3, sitesList)
    lastSite = sitesList[len(sitesList) -1]
    idSite = lastSite.getId()
    print(idSite)
    listaSensores = [sensor]

    idSite = int(idSite) + 1
    sitesList = generate_random_data(latitude, longitude, 4, int(idSite))
    sensor = Sensor.Sensor( 2,"temperatura",4, sitesList)
    lastSite = sitesList[len(sitesList) -1]
    idSite = lastSite.getId()
    print(idSite)
    listaSensores.append(sensor)

    idSite = int(idSite) + 1
    sitesList = generate_random_data(latitude, longitude, 2, int(idSite))
    sensor = Sensor.Sensor( 3,"phSolo",2,sitesList)
    lastSite = sitesList[len(sitesList) -1]
    idSite = lastSite.getId()
    print(idSite)
    listaSensores.append(sensor)

    idSite = int(idSite) + 1
    sitesList = generate_random_data(latitude, longitude, 5, int(idSite))
    sensor = Sensor.Sensor(4,"lixeira",5, sitesList)
    lastSite = sitesList[len(sitesList) -1]
    idSite = lastSite.getId()
    print(idSite)
    listaSensores.append(sensor)  

    started = 'true'

listaAppsCadastradas = []
dadosColetados = []

@app.route("/")
def web_service():
    retorno = 'Id  !!  Lista De Sensores  !!   Quantidade !! Foi Solicitado? <br>'
    for s in listaSensores:
        retorno += str(s.getId())+ "&nbsp;!!&nbsp;" + s.getNome()+ "&nbsp;!!&nbsp;" + str(s.getQuantidade()) + "&nbsp;!!&nbsp;" + str(s.getSolicitado())+  "<br> "
    return retorno

@app.route("/get-file")
def get_file():
    results = generate_file_data()
    generator = (cell for row in results
                    for cell in row)
    return Response(generator,
                       mimetype="text/plain",
                       headers={"Content-Disposition":
                                    "attachment;filename=flightplan.mavlink"})

@app.route("/autonomia", methods=['GET'])
def set_autonomy():
    new_autonomy = request.args.get('autonomia')
    global autonomy
    old_autonomy = autonomy
    autonomy = float(new_autonomy)
    return( 'Nova autonomia:' + str(autonomy) + '<br>'
            'Autonomia antiga:' + str(old_autonomy) )

@app.route("/cadastraApp", methods=['GET'])
def create_app():
    nomeApp = request.args.get('nomeApp')
    isCadastrado = False
    for x in listaAppsCadastradas:
        if nomeApp == x:
            isCadastrado = True           
    
    if isCadastrado == False:
        listaAppsCadastradas.append(nomeApp)
        return( 'App cadastrado com sucesso')
    else:
        return( 'App já está cadastrado')

@app.route("/planejaVoo", methods=['GET'])
def plan_flight():

    listaSites = []
    for x in listaSensores:
        if x.getSolicitado() == True:
            sites = x.getSites()
            for y in sites:
                listaSites.append(y)

    print('Lista de Sites: ' +str(listaSites))
    minimoEnergia = otim.getMinimoEnergia(listaSites)
    #percentual = (float(minimoEnergia)/autonomy) * 100

    print('o gasto mínimo de energia é: ' + str(minimoEnergia) + '% <br>')
    
    tabu.get_flight_plan_tabu_search(listaSites, minimoEnergia)


    """    retorno = ('O uso da autonomia para visitar todos os sensores está em  ' 
        + str(percentual) + '% <br>'
        + 'o gasto mínimo de energia é: ' + str(minimoEnergia) + '% <br>'
        + 'Estatísticas para realização do voo: <br>' 
        + otim.getMaximoDeSensores(listaSites, autonomy) ) """
        
    return ('retorno')    
    
@app.route("/solicitaDadosSensor", methods=['GET'])
def subscribe_for_sensors_data():
    nomeApp = request.args.get('nomeApp')
    tipoSensor = request.args.get('tipoSensor')

    isCadastrado = False
    
    for x in listaAppsCadastradas:
        if nomeApp == x:
            isCadastrado = True
                
    if isCadastrado == False:
        return( 'Você precisa cadastrar a aplicação' 
        + 'antes de solicitar dados de sensores!')
    else:
        for x in listaSensores:
            if x.getId() == int(tipoSensor):
                listaSensores.remove(x)
                x.setSolicitado(True)
                listaSensores.append(x)
    
    return (plan_flight())          

def run_drone_mqtt(arg, arg2):
    print ("Running thread! Args:", (arg, arg2))
    print ("Done!")    
  #  ServiceSchedule.loop()

@app.route("/setDados", methods=['GET'])
def set_data():
    dados = request.args.get('data')
    print('msg no webservice:' + dados)
    dados = dados.replace('b','')
    dadosColetados.append(dados)
    
    return 'ok'
    
    
@app.route("/getDados", methods=['GET'])
def get_data():
    retorno = ''
    id = 1
    for s in dadosColetados:
        retorno += str(id)+': ' + str (s)+  "<br> "
        id += 1
        
    return retorno


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    

    