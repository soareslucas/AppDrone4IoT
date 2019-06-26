'''
Created on Jun 1, 2019

@author: lucassoares
'''


class Sensor:
    def __init__(self, id, nome, quantidade, sites):
        self.id = id
        self.nome = nome
        self.quantidade = quantidade
        self.sites = sites
        self.solicitado = False

    def setId(self, id):
        self.id = id
             
    def setNome(self, nome):
        self.nome = nome
     
    def setQuantidade(self, quantidade):
        self.quantidade = quantidade
        
    def setSolicitado(self, solicitado):
        self.solicitado = solicitado
        
    def setSites(self, sites):
        self.sites = sites
     
    def getId(self):
        return self.id
    
    def getNome(self):
        return self.nome
         
    def getQuantidade(self):
        return self.quantidade

    def getSolicitado(self):
        return self.solicitado
    
    def getSites(self):
        return self.sites