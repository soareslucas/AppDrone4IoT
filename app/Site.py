'''
Created on Jun 1, 2019
@author: lucassoares
'''
import math
import numpy as np
import utm
from haversine import haversine

import json


class Site():

    __distances_table = {}  

    def __init__(self, id, posicao, routed, sensorType, active, buffer):
        self.id = id
        self.posicao = posicao
        self.routed = routed
        self.active = active
        self.sensorType = sensorType
        self.buffer = buffer
        self.idArray = 0

     #   self.demand = demand

    def calculateEnergyCost(self,p1,p2):
        # velocity in m/s
        velocidade = 15
        # kg/m^-3
        rho = 1.225
        # rad/s
        omega = 20
        # cm
        R = 0.5
        # weight in Newtons
        W = 19
        # Drag Coefficient (zero-lift Drag Coefficient)
        Cd = 0.0225
        # Frontal Area of the UAV  (m2) 
        frontalArea = 0.07992

        energy = 0
        d = np.sqrt( (p1[0]-p2[0])**2+ (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)

        #straight line distance for simplicity
        phi =  np.arcsin((  np.abs(p1[2]-p2[2] ) / d))
        Vh =  velocidade * np.cos(phi)
        Vv =  velocidade * np.sin(phi)
        Pp = (1/2) * rho * Cd * frontalArea * np.power(Vh,3)  
        + ((3.14/4)*4*10*rho*Cd*np.power(omega,2)*np.power(R,4))
        + ((3.14/4)*4*10*rho*Cd*np.power(omega,2)*np.power(R,4))*3* np.power(Vh/omega*R,2)
        dividendo =  ( np.power(Vh,2)/ (np.power(omega,2) * np.power(R,2) ) )
        + np.sqrt( np.power((np.power(Vh,2)/ (np.power(omega,2) * np.power(R,2) )  ),2) 
        - (4* np.power(W,2)/ (4* (np.power(rho,2)) * np.power(3.14,2) * np.power(omega, 4) * np.power(R,8) ))) 
        raiz = dividendo / 2
        lamb =  np.sqrt((raiz))
        Pi = omega*R*W * lamb 
        Ph = Pp + Pi;	
        Pv = 0

        if( ( p1[2]-p2[2] ) > 0 ):
                raizPv = np.power(Vv, 2) - (  (2*W)/ (rho *3.14* np.power(R,2) ) )
                if(raizPv < 0):
                        raizPv = np.power(15, 2) - (  (2*W)/ (rho *3.14* np.power(R,2) ) )
                        Pv = ( (W/2) * 15) - ( (W/2) * np.sqrt(raizPv) )
                else:
                        Pv = ((W/2) * Vv) - ((W/2) * np.sqrt(raizPv));			
        else:
                if( (p1[2]-p2[2] ) < 0 ):
                        Pv = ( (W/2) * Vv) + ( (W/2) * np.sqrt( np.power(Vv, 2) + (  (2*W)/ (rho *3.14* np.power(R,2) ) ) ) )

        energy = (d / velocidade) * (Pv + Ph)  

        return(energy)

    def setId(self, id):
        self.id = id

    def getId(self):
        return self.id

    def setActive(self, active):
        self.active = active

    def getActive(self):
        return self.active
        
    def setPosicao(self, posicao):
        self.posicao = posicao

    def getPosicao(self):
        return self.posicao
    
    def setRouted(self, routed):
        self.routed = routed
    
    def setBuffer(self, buffer):
        self.buffer = buffer

    def getBuffer(self):
        return self.buffer

    def isRouted(self):
        return self.routed

    def getNewPosicao(self):
        utm_conversion = utm.from_latlon(float(self.posicao[0]),float(self.posicao[1]))
        newPosition = [0,0,0]
        newPosition[0] = utm_conversion[0]
        newPosition[1] = utm_conversion[1]
        newPosition[2] = self.posicao[2]
        return newPosition
    
    def toString(self):
        return str(id)  
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def setSensorType(self, sensorType):
        self.sensorType = sensorType

    def getSensorType(self):
        return self.sensorType

    def get_distance_to(self, dest):

        origin = (self.id)
        destination = (dest.getId())

        key = origin +'_'+ destination

        if key in Site.__distances_table:
            return Site.__distances_table[key]

        p1 = self.getNewPosicao()
        p2 = dest.getNewPosicao()

        dist = self.calculateEnergyCost(p1,p2)
        Site.__distances_table[key] = dist

        return dist

    def setIdArray(self, idArray):
        self.idArray= idArray

    def getIdArray(self):
        return self.idArray