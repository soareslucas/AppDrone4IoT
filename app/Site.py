'''
Created on Jun 1, 2019

@author: lucassoares
'''
import math
import numpy as np

import utm

import json


class Site():
    def __init__(self, id, posicao, isRouted):
        self.id = id
        self.posicao = posicao
        self.isRouted = isRouted
     #   self.demand = demand

    def setId(self, id):
        self.id = id

    def getId(self):
        return self.id
        
    def setPosicao(self, posicao):
        self.posicao = posicao

    def getPosicao(self):
        return self.posicao
    
    def setIsRouted(self, isRouted):
        self.isRouted = isRouted

    def isRouted(self):
        return self.isRouted


    #def setDemand(self, demand):
    #    self.demand = demand

   # def getDemand(self):
   #     return self.demand


    def getNewPosicao(self):

        print( 'Posicao dos pontos  : ' + self.id + ' ' + str(self.posicao[0]) + ' e '+ str(self.posicao[1]) + ' ' + str(self.posicao[2])  )
        utm_conversion = utm.from_latlon(self.posicao[0],self.posicao[1])
        newPosition = [0,0,0]
        newPosition[0] = utm_conversion[0]
        newPosition[1] = utm_conversion[1]
        newPosition[2] = self.posicao[2]
        print(str())
        return newPosition
    
    def toString(self):
        return str(id)  
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)