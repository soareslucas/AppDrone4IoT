
'''
Created on May 24, 2019

@author: lucassoares
'''
import math
from pulp import *
import numpy as np
#import seaborn as sn
import random
#from mpl_toolkits import mplot3d
import Site as Site
import Vehicle as Vehicle
import itertools
import matplotlib.pyplot as plt




def getMinimoEnergia(listaSites):

        # Autonomia em J |||  (59940 - 1500 mAh - 11.1V )   (99900 - 2500 mAh - 11.1V ) (159840 - 4000 mAh - 11.1V )
        autonomy = 59940

        vehicles = []
        vehicle = Vehicle.Vehicle( 1000 )
        vehicle.setId("1")
        vehicles.append(vehicle)
        vehicle = Vehicle.Vehicle( 5000 )
        vehicle.setId("2")
        vehicles.append(vehicle)

        customer_count = len(listaSites)
        vehicle_count = len(vehicles)
        
        # BLE
        # 50 to 100m
        # 1Mb/s 

        
        q = dict( (a.getId(), a.getBuffer() ) for a in listaSites )

        q = []
        for k in range(customer_count):
                q.append(listaSites[k].getBuffer())
        
        Q = []
        for k in range(vehicle_count):
                Q.append(vehicles[k].getCapacity())

        hover = []
        for k in range(customer_count):
              sec = listaSites[k].getBuffer()


        index = 0
        sites = []
        for site in listaSites:
            site.setIdArray(index)
            sites.append(site)
            index += 1


        positions = dict( (int(a.getIdArray()), a.getNewPosicao() ) for a in listaSites )

        energy_costs = np.zeros((customer_count, customer_count, vehicle_count))

        for k in range(vehicle_count):
                for j in range(customer_count):
                        for i in range(customer_count):
                                energy_costs[i][j][k] = calculateEnergyCost(positions[i], positions[j], vehicles[k])
                                print('Custo energético entre '+ str(i)+' e '+ str(j)+' no veículo ' + str(k) +' :'+ str( energy_costs[i][j][k] ) )
                

        prob=LpProblem("vehicle",LpMinimize)

        # definition of variables which are 0/1
        x = [[[LpVariable("x%s_%s,%s"%(i,j,k), cat="Binary") if i != j else None for k in range(vehicle_count)]for j in range(customer_count)] for i in range(customer_count)]

        #u = LpVariable.dicts('u', range(customer_count), 0, customer_count-1, LpInteger)

        #objective function
        cost = lpSum(energy_costs[i][j][k] * x[i][j][k] if i != j else 0
                          for k in range(vehicle_count) 
                          for j in range(customer_count) 
                          for i in range (customer_count) ) 
        prob+=cost

        # constraints
        # foluma (2)
        for j in range(1, customer_count):
                prob += lpSum(x[i][j][k] if i != j else 0 
                                for i in range(customer_count) 
                                for k in range(vehicle_count)) == 1 

        # foluma (3)
        for k in range(vehicle_count):
                prob += lpSum(x[0][j][k] for j in range(1,customer_count)) == 1
                prob += lpSum(x[i][0][k] for i in range(1,customer_count)) == 1

        # foluma (4)
        for k in range(vehicle_count):
                for j in range(customer_count):
                        prob += lpSum(x[i][j][k] if i != j else 0 
                                for i in range(customer_count)) -  lpSum(x[j][i][k] for i in range(customer_count)) == 0

        for k in range(vehicle_count):
                prob += lpSum([ q[j] * x[i][j][k] if i != j else 0 for i in range(customer_count) for j in range (1,customer_count) ]) <= Q[k] 


        #subtour elimination
        subtours = []
        for i in range(2,customer_count):
                subtours += itertools.combinations(range(1,customer_count), i)

        for s in subtours:
                prob += lpSum(x[i][j][k] if i !=j else 0 for i, j in itertools.permutations(s,2) for k in range(vehicle_count)) <= len(s) - 1


        prob.solve()

        print('Valor mínimo gasto energético: ' + str(value(prob.objective)))
        print('Total capacidade armazenamento drone: ' + str(Q[0] + Q[1]) )
        
        data = 0
        
        for i in range(customer_count):
                for j in range(customer_count):
                        for k in range(vehicle_count):
                                if i != j:
                                        data += q[j] * value(x[i][j][k])

        print('Total sincronizado: '+ str(data))

        z = ''
        array = [0]

        non_zero_edges = []
        for i in range(customer_count):
                for j in range(customer_count):
                        for k in range(vehicle_count):
                                if ( (i != j) and  value( x[i][j][k]) != 0 ):
                                        a = [i,j,k]
                                        non_zero_edges.append(a)


        for n in non_zero_edges:
                print (n)
        
        def get_next_site_cv(parent, non_zero_edges):
                '''helper function to get the next edge'''
                print(non_zero_edges)
                edges = []
                for e in non_zero_edges:
                        if(parent == e[0]):
                                edges.append(e)

                for e in edges:
                        non_zero_edges.remove(e)
                return edges


        tours = get_next_site_cv(0, non_zero_edges)
        tours = [ [e] for e in tours ]

        for t in tours:
                while t[-1][1] != 0:
                        t.append(get_next_site_cv(t[-1][1], non_zero_edges)[-1])

        for t in tours:
                print(' -> '.join(str([ a for a,b,c in t]+[0]) ))

 
        return( z, value(prob.objective), array)