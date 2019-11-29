'''
Created on Jun 1, 2019

@author: lucassoares
'''
import math
import numpy as np

import utm



class Site():
    def __init__(self, id, posicao):
        self.id = id
        self.posicao = posicao

    def setId(self, id):
        self.id = id
        
    def setPosicao(self, posicao):
        self.posicao = posicao
     
    def getId(self):
        return self.id
    
    def getPosicao(self):


        print( 'Posicao dos pontos  : ' + self.id + ' ' + str(self.posicao[0]) + ' e '+ str(self.posicao[1]) + ' ' + str(self.posicao[2])  )
        utm_conversion = utm.from_latlon(self.posicao[0],self.posicao[1])

#        a =  6378137
#        b =  6356752.314245   
#        e2 = 1 - ( math.sqrt(b)/  math.sqrt(a))
        
#        seno = math.sin(phi)
#        square =  e2 * math.pow( seno , 2)
#        N = a / math.sqrt(1 - square )

#        X1 = (N+h) * math.cos(phi) * math.cos(lamb)
#        Y1 = (N+h) * math.cos(phi) * math.sin(lamb)
#        Z1 = ((  math.sqrt(b)/math.sqrt(a)) * N + h) * math.sin(phi)

        newPosition = [0,0,0]
        newPosition[0] = utm_conversion[0]
        newPosition[1] = utm_conversion[1]
        newPosition[2] = self.posicao[2]


        print(str(newPosition))

        return newPosition
    
    def toString(self):
        return str(id)  