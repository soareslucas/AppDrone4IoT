'''
Created on Jun 1, 2019

@author: lucassoares
'''


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
        return self.posicao
    
    def toString(self):
        return str(id)