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
import Otimizacao as otim
import Sensor as Sensor
import Site as Site
import TabuSearch as tabu
import HybridAlgorithm as ha
import Utils as util
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

latitude = 41.176877
longitude = -8.604733
textFile = ''
# Autonomia em J |||  (59940 - 1500 mAh - 11.1V )   (99900 - 2500 mAh - 11.1V ) (159840 - 4000 mAh - 11.1V )
autonomy = 59940


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

@app.route("/set_depot")
def set_depot():
    global listaSites
    global latitude
    global longitude

    location = []

    latitude = float(request.args.get('latitude'))
    longitude = float(request.args.get('longitude'))

    listaSites[0].setPosicao((latitude, longitude, 0))

    return Response(json.dumps('ok'),  mimetype='application/json')



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

        results = str(result[0])
        results += '  '+ str(result[1])
        util.generate_file_flight_plan(result[2], listaSites, 'milp_flightplan')


        """         percentual = (float(min_energy)/autonomy) * 100
        results = ('O uso da autonomia para visitar todos os sensores está em  ' 
        + str(percentual) + '% <br>'
        + 'o gasto mínimo de energia é: ' + str(min_energy) + ' <br>'
        + 'Estatísticas para realização do voo: <br>' 
        + otim.getMaximoDeSensores(listaSites, autonomy) )  """

    if algorithm == '2':
        dict_of_neighbours = tabu.generate_neighbours(listaSites)
        first = tabu.generate_first_solution(dict_of_neighbours)
        result = tabu.tabu_search(first[0], first[1], dict_of_neighbours, 5, len(listaSites)*10)
        results = str(result[0])

        route = []
        route = result[0]
        route.append(0)

        util.generate_file_flight_plan(result[0], listaSites, 'tabu_flightplan')


        results += '  '+ str(result[1])

    if algorithm == '3':
        individual = ha.run_ga(listaSites, 500, 20, 50, 0.02, verbose=1)
        result = individual['route']
        genes = result.genes
        
        route_list = []

        route = genes[0].getId()
        for g in range(1, len(genes)):
            route += '--> ' + genes[g].getId()
            route_list.append(int(genes[g].getId()))
        
        route_list.append(0)
        util.generate_file_flight_plan(route_list, listaSites, 'hybrid_flightplan')


        results = route
        results += '  '+ str(result.travel_cost)

    if algorithm == '4':

        # MILP
        result = otim.getMinimoEnergia(listaSites)
        results = str(result[0])
        results += '  '+ str(result[1])

        # Tabu
        dict_of_neighbours = tabu.generate_neighbours(listaSites)
        first = tabu.generate_first_solution(dict_of_neighbours)
        result = tabu.tabu_search(first[0], first[1], dict_of_neighbours, 5, len(listaSites)*10)
        results += str(result[0])
        results += ' '+ str(result[1])

        # Hybrid
        individual = ha.run_ga(listaSites, 500, 20, 50, 0.02, verbose=1)
        result = individual['route']
        genes = result.genes
        route = ''

        for g in genes:
            route += '-> ' + g.getId()

        results += route
        results += '  '+ str(result.travel_cost)

        
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

    _temp = []
    _temp = listaSites.copy()

    for y in listaSites:
        if str(y.getSensorType()) == tipoSensor:
            _temp.remove(y)

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

@app.route("/newPoints", methods=['GET'])
def new_points():

    global listaSensores
    global listaSites
    
    site = Site.Site(str(0), (latitude, longitude, 0) , "false", 0)
    listaSites = [site]

    idSite = 1

    sitesList = util.generate_random_data(latitude, longitude, 5, idSite, 1)
    sensor = Sensor.Sensor(1,"umidade",5, sitesList)
    lastSite = sitesList[len(sitesList) -1]
    idSite = lastSite.getId()
    listaSensores = [sensor]

    idSite = int(idSite) + 1
    sitesList = util.generate_random_data(latitude, longitude, 15, int(idSite), 2)
    sensor = Sensor.Sensor( 2,"temperatura",15, sitesList)
    lastSite = sitesList[len(sitesList) -1]
    idSite = lastSite.getId()
    listaSensores.append(sensor)

    idSite = int(idSite) + 1
    sitesList = util.generate_random_data(latitude, longitude, 25, int(idSite), 3)
    sensor = Sensor.Sensor( 3,"phSolo",25,sitesList)
    lastSite = sitesList[len(sitesList) -1]
    idSite = lastSite.getId()
    listaSensores.append(sensor)

    idSite = int(idSite) + 1
    sitesList = util.generate_random_data(latitude, longitude, 10, int(idSite), 4)
    sensor = Sensor.Sensor(4,"lixeira",10, sitesList)
    lastSite = sitesList[len(sitesList) -1]
    idSite = lastSite.getId()
    listaSensores.append(sensor)  

    return Response(json.dumps('ok'),  mimetype='application/json')


if __name__ == "__main__":


    new_points()

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    