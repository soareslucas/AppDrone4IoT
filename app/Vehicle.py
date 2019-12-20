'''
Created on Dec 13, 2019

@author: lucassoares
'''
import json

class Vehicle():
    def __init__(self, capacity):
        self.routes = []
        self.capacity = capacity
        self.total_energy_spent = 0
        self.current_location = 0

    def add_node(self, site, energy_cost):
        self.routes.append(site)
        self.total_energy_spent +=  energy_cost
        self.current_location = site.id

    def check_if_fits(self, energy_cost):
        return total_energy_spent + energy_cost <= capacity
