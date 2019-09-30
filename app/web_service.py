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
import app.DroneMQTT as ServiceSchedule
from threading import Thread
import os

app = Flask(__name__)

autonomia = 2500
idSite = 1

sites = []
for i in range(0, 3):
    site = Site.Site(str(idSite), (np.random.randint(1,1000), np.random.randint(1,1000), np.random.randint(1,100) ))
    sites.append(site)
    idSite += 1
    
sensorUmidade = Sensor.Sensor(1,"umidade",3,sites)
listaSensores = [sensorUmidade]

sites = []
for i in range(0, 4):
    site = Site.Site(str(idSite), (np.random.randint(1,1000), np.random.randint(1,1000), np.random.randint(1,100) ))
    sites.append(site)
    idSite += 1
    
sensor = Sensor.Sensor(2,"temperatura",4,sites)
listaSensores.append(sensor)

sites = []
for i in range(0, 2):
    site = Site.Site(str(idSite), (np.random.randint(1,1000), np.random.randint(1,1000), np.random.randint(1,100) ))
    sites.append(site)
    idSite += 1
    
sensor = Sensor.Sensor(3,"phSolo",2,sites)
listaSensores.append(sensor)


sites = []
for i in range(0, 5):
    site = Site.Site(str(idSite), (np.random.randint(1,1000), np.random.randint(1,1000), np.random.randint(1,100) ))
    sites.append(site)
    idSite += 1
    
sensor = Sensor.Sensor(4,"lixeira",5,sites)
listaSensores.append(sensor)
 

listaAppsCadastradas = []

dadosColetados = []


@app.route("/")
def web_service():
    retorno = 'Id  !!  Lista De Sensores  !!   Quantidade !! Foi Solicitado? <br>'
    for s in listaSensores:
        retorno += str(s.getId())+ "&nbsp;!!&nbsp;" + s.getNome()+ "&nbsp;!!&nbsp;" + str(s.getQuantidade()) + "&nbsp;!!&nbsp;" + str(s.getSolicitado())+  "<br> "
    return retorno

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

@app.route("/autonomia")
def autonomiaDefinition():
    autonomiaUsu = request.args.get('autonomia')
    global autonomia;
    autonomiaAntiga = autonomia
    autonomia = float(autonomiaUsu)
    return( 'Nova autonomia:' + str(autonomiaUsu) + '<br>'
            'Autonomia antiga:' + str(autonomiaAntiga) )

@app.route("/cadastraApp")
def cadastraApp():
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

@app.route("/planejaVoo")
def planejaVoo():

    listaSites = []
                
    for x in listaSensores:
        if x.getSolicitado() == True:
            sites = x.getSites()
            for y in sites:
                listaSites.append(y)
                
    
    minimoEnergia = otim.getMinimoEnergia(listaSites)
    
    percentual = (float(minimoEnergia)/autonomia) * 100
    
    if percentual > 80:

        retorno = 'O uso da autonomia para visitar todos os sensores está em  ' + str(percentual) + '% <br>' + 'Estatísticas para realização do voo: <br>'  + otim.getMaximoDeSensores(listaSites, autonomia)
     
       # thread = Thread(target=runDroneMQTT, args=("MQTT", "CLIENT"))
        #thread.start()
        
        return (retorno)

    return( 'O uso da autonomia está em  '+ str(percentual) +'%')
    
    
@app.route("/solicitaDadosSensor")
def solicitaDadosSensor():
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
    
    return (planejaVoo())          

def runDroneMQTT(arg, arg2):
    print ("Running thread! Args:", (arg, arg2))
    print ("Done!")    
    ServiceSchedule.loop()

@app.route("/setDados")
def setDados():
    dados = request.args.get('data')
    print('msg no webservice:' + dados)
    
    dados = dados.replace('b','')

    dadosColetados.append(dados);
    
    return 'ok'
    
    
    
@app.route("/getDados")
def getDados():
    retorno = ''
    id = 1
    
    for s in dadosColetados:
        retorno += str(id)+': ' + str (s)+  "<br> "
        id += 1
        
    return retorno

    

    