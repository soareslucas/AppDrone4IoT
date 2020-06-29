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


import utm
rnd = np.random


minimoEnergia = 0

def getValueMinimoEnergia():
        global minimoEnergia
        return(minimoEnergia)

def calculateEnergyCost(p1,p2,veh):
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


def get_next_site(parent, non_zero_edges):
        '''helper function to get the next edge'''
        edges = [e for e in non_zero_edges if e[0]==parent]
        for e in edges:
                non_zero_edges.remove(e)
        return edges



def getMinimoEnergia(listaSites):

        # Autonomia em J |||  (59940 - 1500 mAh - 11.1V )   (99900 - 2500 mAh - 11.1V ) (159840 - 4000 mAh - 11.1V )
        autonomy = 59940

        vehicles = []
        vehicle = Vehicle.Vehicle( 2000 )
        vehicle.setId("1")
        vehicles.append(vehicle)
        vehicle = Vehicle.Vehicle( 2000 )
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
                

        prob=LpProblem("vehicle",LpMaximize)

        # definition of variables which are 0/1
        x = [[[LpVariable("x%s_%s,%s"%(i,j,k), cat="Binary") if i != j else None for k in range(vehicle_count)]for j in range(customer_count)] for i in range(customer_count)]

        #u = LpVariable.dicts('u', range(customer_count), 0, customer_count-1, LpInteger)

        #objective function
        cost = lpSum( x[i][j][k] if i != j else 0
                          for k in range(vehicle_count) 
                          for j in range(customer_count) 
                          for i in range (customer_count) ) 
        prob+=cost


        # formula (2) obriga passar em todos os lugares
        """         for i in range(customer_count):
                cap = 1 if i != 0 else vehicle_count
                prob+= lpSum([ x[i][j][k]  for j in range( customer_count) for k in range( vehicle_count) ]) == cap
                prob+= lpSum([ x[i][j][k]  for j in range( customer_count) for k in range( vehicle_count) ]) == cap """

        # foluma (3)
        for k in range(vehicle_count):
                prob += lpSum(x[0][j][k] for j in range(1,customer_count)) == 1
                prob += lpSum(x[i][0][k] for i in range(1,customer_count)) == 1

        # foluma (4)
        for j in range(customer_count):
                prob += lpSum(x[i][j][k] if i != j  else 0 
                        for i in range(customer_count) for k in range(vehicle_count)) -  lpSum(x[j][i][k]   if i != j else 0 for i in range(customer_count) for k in range(vehicle_count)) == 0


        for k in range(vehicle_count):
                prob += lpSum([ q[j] * x[i][j][k] if i != j else 0 for i in range(customer_count) for j in range (1,customer_count) ]) <= Q[k] 


        prob += lpSum(energy_costs[i][j][k] * x[i][j][k] if i != j else 0
                                for k in range(vehicle_count) 
                                for j in range(customer_count) 
                                for i in range (customer_count) ) <= autonomy


        

        #subtour elimination
        subtours = []
        for i in range(2,customer_count):
                subtours += itertools.combinations(range(1,customer_count), i)

        for s in subtours:
                prob += lpSum(x[i][j][k] if i !=j else 0 for i, j in itertools.permutations(s,2) for k in range(vehicle_count)) <= len(s) - 1


        prob.solve()

        print('Valor mínimo gasto energético: ' + str(value(prob.objective)))
        print('Total capacidade amarzenamento drone: ' + str(Q[0] + Q[1]) )
        
        data = 0
        
        #objetivo = int(value(prob.objective))


        #print('objetivo: '+str(objetivo))

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


        plt.figure(figsize=(8,8))
        for i in range(customer_count):    
                a =  positions[i]
                if i == 0:
                        plt.scatter(a[0], a[1], c='green', s=200)
                        plt.text(a[0], a[1], "depot", fontsize=12)
                else:
                        plt.scatter(a[0], a[1], c='orange', s=200)
                        plt.text(a[0], a[1], str(sites[i].getId()), fontsize=12)

        a =  positions[0]

        
        plt.xlim(a[0], 530190)
        plt.ylim(a[1], 4570690)

        print (a[0])
        print (a[1])

        for k in range(vehicle_count):
                for i in range(customer_count):
                        for j in range(customer_count):
                                if i != j and value(x[i][j][k]) == 1:
                                        a =  positions[i]
                                        b = positions[j]
                                        plt.plot([a[0], b[0]], [a[1], b[1]], c="black")

        plt.show()

        """ 
                non_zero_edges = [ e for e in x if value(x[e]) != 0 ]
                tours = get_next_site(0, non_zero_edges)
                tours = [ [e] for e in tours ]
                print(tours)

                for t in tours:
                        while t[-1][1] !='0':
                                t.append(get_next_site(t[-1][1], non_zero_edges)[-1])

                for t in tours:
                        print(' -> '.join([ a for a,b in t]+['0']))

                for t in tours:
                        z = (' -> '.join([ a for a,b in t]+['0']))

                route = []
                for t in tours:
                        route = ([a for a,b in t]+['0'])

                for r in route:
                        array.append(int(r))

                print(array)
        """
 
        return( z, value(prob.objective), array)

def getMaximoDeSensores(listaSites, autonomia):
        
        sites = []
        for site in listaSites:
            sites.append(site.getId())

        positions = dict( (a.getId(), a.getNewPosicao() ) for a in listaSites )
        energy_costs=dict( ((s1,s2), calculateEnergyCost(positions[s1],positions[s2])) for s1 in positions for s2 in positions if s1!=s2)

        #the number of sales people 
        K = 1 

        prob=LpProblem("vehicle",LpMaximize)

        x = LpVariable.dicts('x',energy_costs, 0,1,LpBinary)

        #dummy vars to eliminate subtours
        u = LpVariable.dicts('u', sites, 0, len(sites)-1, LpInteger)

        cost = (lpSum([x[(i,j)] for (i,j) in x]))
        prob+=cost      

        for k in sites:
                prob+= lpSum([ x[(i,k)] for i in sites if (i,k) in x]) == lpSum([ x[(k,i)] for i in sites if (k,i) in x])
        
        for k in sites:
                prob+= lpSum([ x[('0',k)] for k in sites if ('0',k) in x]) == 1
        
        for k in sites:
                prob+= lpSum([ x[(k,'0')] for k in sites if (k, '0') in x]) == 1

        prob+= lpSum([  x[(i,j)]  * energy_costs[(i,j)]for (i,j) in energy_costs ]) <= autonomia

        
        #subtour elimination
        N=len(sites)/K
        for i in sites:
                for j in sites:
                        if i != j and (i != '0' and j!= '0') and (i,j) in x:
                                prob += u[i] - u[j] <= (N)*(1-x[(i,j)]) - 1

        prob.solve()                
        
        total_energy_cost = 0
        for i in sites:
            for j in sites:
                if i != j :
                    total_energy_cost += value(x[(i,j)])  * energy_costs[(i,j)]
        

        maxSensores = value(prob.objective)
        global minimoEnergia
        minimoEnergia = getMinimoEnergiaComMaxSensores(maxSensores, energy_costs, listaSites)
            
        return('O maximo de sensores é: ' 
        + str(maxSensores-1) 
        +' <br> O custo inicial para realização do voo seria: '
        + str(total_energy_cost)
        +' <br> O mínimo de custo alcançado é: '
        +str(minimoEnergia))
    


def getMinimoEnergiaComMaxSensores(maxSensores, energy_costs, listaSites):

        sites = []
                
        for site in listaSites:
            sites.append(site.getId())
         
        #create the problme
        prob=LpProblem("vehicle",LpMinimize)
        #indicator variable if site i is connected to site j in the tour
        x = LpVariable.dicts('x',energy_costs, 0,1,LpBinary)
        #dummy vars to eliminate subtours
        u = LpVariable.dicts('u', sites, 0, len(sites)-1, LpInteger)
        #the objective
        cost =  ( lpSum([  x[(i,j)]  * energy_costs[(i,j)]for (i,j) in energy_costs ])) 
        prob+=cost

        for k in sites:
                prob+= lpSum([ x[(i,k)] for i in sites if (i,k) in x]) == lpSum([ x[(k,i)] for i in sites if (k,i) in x])
        
        for k in sites:
                prob+= lpSum([ x[('0',k)] for k in sites if ('0',k) in x]) == 1
        
        for k in sites:
                prob+= lpSum([ x[(k,'0')] for k in sites if (k, '0') in x]) == 1
        
        prob+= lpSum([x[(i,j)] for (i,j) in x]) == maxSensores
        
        #subtour elimination
        N=len(sites)/1
        for i in sites:
                for j in sites:
                        if i != j and (i != '0' and j!= '0') and (i,j) in x:
                                prob += u[i] - u[j] <= (N)*(1-x[(i,j)]) - 1

        prob.solve()

        non_zero_edges = [ e for e in x if value(x[e]) != 0 ]
        tours = get_next_site('0', non_zero_edges)
        tours = [ [e] for e in tours ]

        for t in tours:
                while t[-1][1] !='0':
                        t.append(get_next_site(t[-1][1], non_zero_edges)[-1])

        z = ''
        for t in tours:
                z = (' -> '.join([ a for a,b in t]+['0']))


        generate_file_flight_plan(tours, listaSites)
        
        return value(prob.objective)



        """ 
                plt.figure(figsize=(8,8))
                for i in range(customer_count):    
                        a =  positions[i]
                        if i == 0:
                                plt.scatter(a[0], a[1], c='green', s=200)
                                plt.text(a[0], a[1], "depot", fontsize=12)
                        else:
                                plt.scatter(a[0], a[1], c='orange', s=200)
                                plt.text(a[0], a[1], str(sites[i].getId()), fontsize=12)

                a =  positions[0]

                
                plt.xlim(a[0], 530190)
                plt.ylim(a[1], 4570690)

                print (a[0])
                print (a[1])

                for k in range(vehicle_count):
                        for i in range(customer_count):
                                for j in range(customer_count):
                                        if i != j and value(x[i][j][k]) == 1:
                                                a =  positions[i]
                                                b = positions[j]
                                                plt.plot([a[0], b[0]], [a[1], b[1]], c="black")

                plt.show() """