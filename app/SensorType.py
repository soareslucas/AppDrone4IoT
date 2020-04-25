'''
Created on Jun 1, 2019

@author: lucassoares
'''
import json

class SensorType:
    def __init__(self, id, type):
        self.id = id
        self.type = type


    def setId(self, id):
        self.id = id

    def setType(self, type):
        self.type = type
     
    def getId(self):
        return self.id
    
    def getType(self):
        return self.type


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)