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
import SensorType as SensorType

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
listaTypes = []
listaSitesManual = []
listSensorsManual = []



sensorType = SensorType.SensorType( 1,"PhSolo")
listaTypes.append(sensorType)
sensorType = SensorType.SensorType( 2,"Umidade")
listaTypes.append(sensorType)
sensorType = SensorType.SensorType( 3,"Temperatura")
listaTypes.append(sensorType)
sensorType = SensorType.SensorType( 4,"Lixeira")
listaTypes.append(sensorType)



#latitude = 41.176877
#longitude = -8.604733
latitude = 41.287083
longitude = -8.639556
#latitude = 48.879026
#longitude = 2.367448

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


@app.route("/change_active")
def change_active():
    global listaSitesManual

    id = request.args.get('id')


    for idx, item in enumerate(listaSitesManual):
        if str(item.getId()) == id:
            if(item.getActive() == False):
                item.setActive(True)
            else:
                item.setActive(False)
            listaSitesManual[idx] = item
        print(listaSitesManual[idx].getActive())


    return Response(json.dumps("ok"),  mimetype='application/json')

@app.route("/change_site_plan")
def change_site_plan():
    global listaSitesManual

    id = request.args.get('id')


    for idx, item in enumerate(listaSitesManual):
        if str(item.getId()) == id:
            if(item.isRouted() == False):
                item.setRouted(True)
            else:
                item.setRouted(False)
            listaSitesManual[idx] = item

    return Response(json.dumps("ok"),  mimetype='application/json')


@app.route("/change_site_plan")
def add_sensors_plan():
    global listaSitesManual


@app.route("/get_sites_manual")
def get_sites_manual():
    global listaSitesManual

    _tmp = []
    for l in listaSitesManual:
        _tmp +=  [l.toJSON()]
    return Response(json.dumps(_tmp),  mimetype='application/json')

@app.route("/get_types")
def get_types():
    global listaTypes

    _tmp = []
    for l in listaTypes:
        _tmp +=  [l.toJSON()]
    return Response(json.dumps(_tmp),  mimetype='application/json')


@app.route("/add_type", methods=['GET'])
def add_type():
    global listaTypes
    typeName = request.args.get('type')


    if(len(listaTypes) == 0):
        index = 1
    else:
        lastType =  listaTypes[-1]
        index = int(lastType.getId())+1


    sensorType = SensorType.SensorType( index,typeName)
    listaTypes.append(sensorType)

    return Response(json.dumps('ok'),  mimetype='application/json')



@app.route("/add_sensor", methods=['GET'])
def add_sensor():
    global listaSitesManual
    global listSensorsManual
    global listaTypes

    typeName = ""
    latManual = request.args.get('latitude')
    longManual = request.args.get('longitude')    
    typeSensor = request.args.get('sensorType')

    print(typeSensor)

    if(len(listaSitesManual) == 0):
        index = 1
    else:
        lastType =  listaSitesManual[-1]
        index = int(lastType.getId())+1

    siteManual = Site.Site(str(index), (latManual, longManual, 0) , False, typeSensor, False)
    listaSitesManual.append(siteManual)

    
    index = ""
    for idx, item in enumerate(listSensorsManual):
        print(item.getNome())
        print(typeSensor)
        print(idx)
        print(item.getNome() == typeSensor)
        if ( item.getNome() == typeSensor ):
            index = idx

    print(index)

    if (index == ""):
        listaSites = []
        listaSites.append(siteManual)
        sensor = Sensor.Sensor( 1,typeSensor,1,listaSites)
        listSensorsManual.append(sensor)
    else:
        listaSites = []
        sensor = listSensorsManual[index]
        listaSites = sensor.getSites()
        listaSites.append(siteManual)
        sensor.setQuantidade(len(listaSites))
        sensor.setSites(listaSites)
        listSensorsManual[index] = sensor


    return Response(json.dumps('ok'),  mimetype='application/json')




@app.route("/remove_type", methods=['GET'])
def remove_type():
    idType = request.args.get('id')
    global listaTypes

    _temp = []
    _temp = listaTypes.copy()

    for y in listaTypes:
        if str(y.getId()) == idType:
            _temp.remove(y)

    listaTypes = _temp.copy()

    return Response(json.dumps('ok'),  mimetype='application/json')


@app.route("/get_sensors_manual")
def get_sensors_manual():
    global listSensorsManual

    _tmp = []
    for l in listSensorsManual:
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

    #all
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
    global listaTypes

    
    site = Site.Site(str(0), (latitude, longitude, 0) , False, 0, False)
    listaSites = [site]

    idSite = 1

    sitesList = util.generate_random_data(latitude, longitude, 5, idSite, 1)
    sensor = Sensor.Sensor(1,listaTypes[0],5, sitesList)
    lastSite = sitesList[len(sitesList) -1]
    idSite = lastSite.getId()
    listaSensores = [sensor]

    idSite = int(idSite) + 1
    sitesList = util.generate_random_data(latitude, longitude, 15, int(idSite), 2)
    sensor = Sensor.Sensor( 2,listaTypes[1],15, sitesList)
    lastSite = sitesList[len(sitesList) -1]
    idSite = lastSite.getId()
    listaSensores.append(sensor)

    idSite = int(idSite) + 1
    sitesList = util.generate_random_data(latitude, longitude, 25, int(idSite), 3)
    sensor = Sensor.Sensor( 3,listaTypes[2],25,sitesList)
    lastSite = sitesList[len(sitesList) -1]
    idSite = lastSite.getId()
    listaSensores.append(sensor)

    idSite = int(idSite) + 1
    sitesList = util.generate_random_data(latitude, longitude, 10, int(idSite), 4)
    sensor = Sensor.Sensor(4,listaTypes[3],10, sitesList)
    lastSite = sitesList[len(sitesList) -1]
    idSite = lastSite.getId()
    listaSensores.append(sensor)  

    return Response(json.dumps('ok'),  mimetype='application/json')


if __name__ == "__main__":


    new_points()

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    