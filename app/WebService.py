'''
Created on Jun 1, 2019
@author: lucassoares
'''
from flask import Flask
import json
from flask import jsonify
from flask import Response
from flask import request
from flask_cors import CORS, cross_origin
import numpy as np
import app.Otimizacao as otim
import app.Sensor as Sensor
import app.Site as Site
import app.tabu_search as tabu
import app.HybridAlgorithm as ha
from threading import Thread
import os
import random
import sys
import math
from flask import Response

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
listaAppsCadastradas = []
dadosColetados = []
listaSensores = []
listaSites = []

latitude = 48.8790
longitude = 2.3674
textFile = ''
# Autonomia em J |||  (59940 - 1500 mAh - 11.1V )   (99900 - 2500 mAh - 11.1V ) (159840 - 4000 mAh - 11.1V )
autonomy = 59940


def generate_random_data(lat, lon, num_rows,idSite, idSensor):
    sitesTemp = []
    for _ in range(num_rows):
        dec_lat = random.random()/100
        dec_lon = random.random()/100
        site = Site.Site(str(idSite), (lat+dec_lat, lon+dec_lon, np.random.randint(1,20)) , "false", idSensor)
        idSite += 1
        sitesTemp.append(site)
    return sitesTemp

def generate_file_data():
        global textFile
        file = open("flightplan.txt", "w") 
        file.write(textFile) 
        return file

@app.route("/")
def web_service():
    retorno = 'Id  !!  Lista De Sensores  !!   Quantidade !! Foi Solicitado? <br>'
    for s in listaSensores:
        retorno += str(s.getId())+ "&nbsp;!!&nbsp;" + s.getNome()+ "&nbsp;!!&nbsp;" + str(s.getQuantidade()) + "&nbsp;!!&nbsp;" + str(s.getSolicitado())+  "<br> "
    return retorno

@app.route("/get_sites")
def get_sites():
    global listaSites

    _tmp = []
    for l in listaSites:
        _tmp +=  [l.toJSON()]
    return Response(json.dumps(_tmp),  mimetype='application/json')

@app.route("/get_sensors")
def get_sensors():
    _tmp = []
    for l in listaSensores:
        _tmp +=  [l.toJSON()]
    return Response(json.dumps(_tmp),  mimetype='application/json')

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

@app.route("/generateFlightPlan", methods=['GET'])
def plan_flight():
    algorithm = request.args.get('algorithm')

    if algorithm == '1':

        result = otim.getMinimoEnergia(listaSites)

        print(result)
        results = str(result[0])
        results += '  '+ str(result[1])

        """         percentual = (float(min_energy)/autonomy) * 100
        results = ('O uso da autonomia para visitar todos os sensores está em  ' 
        + str(percentual) + '% <br>'
        + 'o gasto mínimo de energia é: ' + str(min_energy) + ' <br>'
        + 'Estatísticas para realização do voo: <br>' 
        + otim.getMaximoDeSensores(listaSites, autonomy) )  """

    if algorithm == '2':
        dict_of_neighbours = tabu.generate_neighbours(listaSites)
        first = tabu.generate_first_solution(dict_of_neighbours)
        print(first)
        result = tabu.tabu_search(first[0], first[1], dict_of_neighbours, 5, len(listaSites)*10)
        results = str(result[0])
        results += '  '+ str(result[1])

    if algorithm == '3':

    results = ha.run_ga(listaSites, 500, n_gen, 50, 0.02, verbose=1):
        
    return Response(json.dumps(results),  mimetype='application/json')
    
@app.route("/addSensors", methods=['GET'])
def subscribe_for_sensors_data():
    #nomeApp = request.args.get('nomeApp')
    tipoSensor = request.args.get('tipoSensor')
    #isCadastrado = False   

    for x in listaSensores:
        if x.getId() == int(tipoSensor):
            listaSensores.remove(x)
            x.setSolicitado(True)
            listaSensores.append(x)


    for x in listaSensores:
        if x.getSolicitado() == True:
            sites = x.getSites()
            for y in sites:
                if not (y in listaSites):
                    listaSites.append(y)
    
    print(listaSites)

    return Response(json.dumps('ok'),  mimetype='application/json')

"""     for x in listaAppsCadastradas:
        if nomeApp == x:
            isCadastrado = True
                
    if isCadastrado == False:
        return( 'Você precisa cadastrar a aplicação' 
        + 'antes de solicitar dados de sensores!')
    else: """

@app.route("/removeSensors", methods=['GET'])
def unsubscribe_sensors():
    tipoSensor = request.args.get('tipoSensor')
    global listaSensores
    global listaSites
    #isCadastrado = False

    for x in listaSensores:
        if x.getId() == int(tipoSensor):
            listaSensores.remove(x)
            x.setSolicitado(False)
            listaSensores.append(x)

    print(tipoSensor)

    _temp = []
    _temp = listaSites.copy()

    for y in listaSites:
        if str(y.getSensorType()) == tipoSensor:
            print(str(y.getSensorType()))
            _temp.remove(y)

    print(_temp)

    listaSites = _temp.copy()

    return Response(json.dumps('ok'),  mimetype='application/json')

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



@app.route("/newPoints", methods=['GET'])
def new_points():

    global listaSensores
    global listaSites
    
    site = Site.Site(str(0), (48.879049, 2.367448, 0) , "false", 0)
    listaSites = [site]
    idSite = 1

    sitesList = generate_random_data(latitude, longitude, 16, idSite, 1)
    sensor = Sensor.Sensor(1,"umidade",16, sitesList)
    lastSite = sitesList[len(sitesList) -1]
    idSite = lastSite.getId()
    print(idSite)
    listaSensores = [sensor]

    idSite = int(idSite) + 1
    sitesList = generate_random_data(latitude, longitude, 42, int(idSite), 2)
    sensor = Sensor.Sensor( 2,"temperatura",42, sitesList)
    lastSite = sitesList[len(sitesList) -1]
    idSite = lastSite.getId()
    print(idSite)
    listaSensores.append(sensor)

    idSite = int(idSite) + 1
    sitesList = generate_random_data(latitude, longitude, 32, int(idSite), 3)
    sensor = Sensor.Sensor( 3,"phSolo",32,sitesList)
    lastSite = sitesList[len(sitesList) -1]
    idSite = lastSite.getId()
    print(idSite)
    listaSensores.append(sensor)

    idSite = int(idSite) + 1
    sitesList = generate_random_data(latitude, longitude, 25, int(idSite), 4)
    sensor = Sensor.Sensor(4,"lixeira",25, sitesList)
    lastSite = sitesList[len(sitesList) -1]
    idSite = lastSite.getId()
    print(idSite)
    listaSensores.append(sensor)  

    return Response(json.dumps('ok'),  mimetype='application/json')


if __name__ == "__main__":

    new_points()

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    