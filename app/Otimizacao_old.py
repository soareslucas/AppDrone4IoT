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

import utm


def getMinimoEnergia(listaSites):
    
        sites = []
        for site in listaSites:
            sites.append(site.getId())

        positions = dict( (a.getId(), a.getNewPosicao() ) for a in listaSites )

        energy_costs = dict( ((s1,s2), calculateEnergyCost(positions[s1],positions[s2])) for s1 in positions for s2 in positions if s1!=s2)

        #for i in sites:
            #for j in sites:
                #if i!=j:
                        #print('Custo energético entre '+ i+' e '+ j+' :'+ str(energy_costs[(i,j)]))
        
        K = 1 
        prob=LpProblem("vehicle",LpMinimize)

        x = LpVariable.dicts('x',energy_costs, 0,1,LpBinary)
        u = LpVariable.dicts('u', sites, 0, len(sites)-1, LpInteger)

        cost = (lpSum([  x[(i,j)]  * energy_costs[(i,j)]for (i,j) in energy_costs ]))
        prob+=cost

        for k in sites:
            prob+= lpSum([ x[i][k] for i in sites] ) ==1
            prob+=lpSum([ x[k][i] for i in sites if (k,i) in x]) ==1

            

        N=len(sites)/K
        for i in sites:
                for j in sites:
                        if i != j and (i != 0 and j!= 0) :
                                prob += u[i] - u[j] <= (N)*(1-x[i][j]) - 1

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

        route = []
        for t in tours:
                route = ([a for a,b in t]+['0'])

        array = []
        for r in route:
                array.append(int(r))


        #print('Valor mínimo:' + str(value(prob.objective)))

        return( z, value(prob.objective), array)



def get_next_site(parent, non_zero_edges):
        '''helper function to get the next edge'''
        edges = [e for e in non_zero_edges if e[0]==parent]
        for e in edges:
                non_zero_edges.remove(e)
        return edges

def calculateEnergyCost(p1,p2, buffer):
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


        a = float(W/2*rho)
        b =  float ( W/ math.pow(W,2) *  (3.14))

        powerHovering = (math.sqrt(a) * math.sqrt(b) )
        
        sec = buffer
        energyHover =  powerHovering * int(sec)

        

        return(energy + energyHover)



def getMaximoDeSensores(listaSites, autonomia):
        
        sites = []

        sites_length = len(listaSites)
        for site in listaSites:
            sites.append(int(site.getId()))

        #positions = dict( (a.getId(), a.getNewPosicao() ) for a in listaSites )
        positions = dict( ( int(a.getId()), a.getPosicao() ) for a in listaSites )

        energy_costs = np.random.randint(1, size=(sites_length, sites_length))

        for j in range(len(sites)):
                for i in range(len(sites)):
                        if(i!=j):
                            energy_costs[i][j] = calculateEnergyCost(positions[i], positions[j], listaSites[j].getBuffer())

        """         for i in range(len(sites)):
                    for j in range(len(sites)):
                        if i!=j:
                                print('Custo energético entre '+ str(i)+' e '+ str(j)+' :'+ str(energy_costs[i][j])) """

        #the number of sales people 
        K = 1 

        prob=LpProblem("vehicle",LpMaximize)

        x = [[LpVariable("x%s_%s"%(i,j), cat="Binary") if i != j else None for j in range(sites_length)] for i in range(sites_length)]

        #dummy vars to eliminate subtours
        u = LpVariable.dicts('u', sites, 0, len(sites)-1, LpInteger)

        cost = lpSum(x[i][j] if i != j else 0
                          for j in range(sites_length) 
                          for i in range (sites_length) ) 
        prob+=cost      

        for i in range(sites_length):
                prob += lpSum(x[i][j] if i != j else 0  for j in range( sites_length) ) == lpSum(x[j][i]  if i != j else 0  for j in range(sites_length) )
        
        prob += lpSum(x[0][i]  for i in range(sites_length) ) == 1
        prob += lpSum(x[i][0]  for i in range(sites_length)  ) == 1
                
        prob += lpSum([ energy_costs[i][j] * x[i][j] if i != j else 0 for i in range(sites_length) for j in range (sites_length) ]) <= autonomia



        
        #subtour elimination
        N=len(sites)/K
        for i in range(sites_length):
            for j in range(sites_length):
                        if i != j and (i != 0 and j != 0) :
                                prob += u[i] - u[j] <= (N)*(1-x[i][j]) - 1

        prob.solve()              

        print('Status: '+ str(LpStatus[prob.status]))  
        
        total_energy_cost = 0
        for i in sites:
            for j in sites:
                if i != j :
                    total_energy_cost += value(x[i][j])  * energy_costs[i][j]
        

        maxSensores = value(prob.objective)

        minimoEnergia = getMinimoEnergiaComMaxSensores(maxSensores, energy_costs, listaSites)
            
        return (maxSensores-1 ), total_energy_cost, minimoEnergia
    



def getMinimoEnergiaComMaxSensores(maxSensores, energy_costs, listaSites):

        sites = []
                
        sites_length = len(listaSites)

        for site in listaSites:
            sites.append(int(site.getId()))
         
        #create the problme
        prob=LpProblem("vehicle",LpMinimize)
        #indicator variable if site i is connected to site j in the tour
        x = [[LpVariable("x%s_%s"%(i,j), cat="Binary") if i != j else None for j in range(sites_length)] for i in range(sites_length)]

        #dummy vars to eliminate subtours
        u = LpVariable.dicts('u', sites, 0, len(sites)-1, LpInteger)

        cost = lpSum(energy_costs[i][j] * x[i][j] if i != j else 0
                          for j in range(sites_length) 
                          for i in range (sites_length) ) 
        prob+=cost      

        for i in range(sites_length):
                prob += lpSum(x[i][j] if i != j else 0  for j in range( sites_length) ) == lpSum(x[j][i]  if i != j else 0  for j in range(sites_length) )
        
        for k in range(sites_length):
                prob += lpSum(x[0][i]  for i in range(sites_length) ) == 1
                prob += lpSum(x[i][0]  for i in range(sites_length)  ) == 1
                
        prob+= lpSum([x[i][j] for i in sites for j in sites]) == maxSensores



        K = 1
        
        #subtour elimination
        N=len(sites)/K
        for i in range(sites_length):
            for j in range(sites_length):
                        if i != j and (i != 0 and j != 0) :
                                prob += u[i] - u[j] <= (N)*(1-x[i][j]) - 1


        prob.solve()

        """         non_zero_edges = [ e for e in x if value(x[e]) != 0 ]
                tours = get_next_site('0', non_zero_edges)
                tours = [ [e] for e in tours ]

                for t in tours:
                        while t[-1][1] !='0':
                                t.append(get_next_site(t[-1][1], non_zero_edges)[-1])

                z = ''
                for t in tours:
                        z = (' -> '.join([ a for a,b in t]+['0'])) """


        #generate_file_flight_plan(tours, listaSites)
        
        return value(prob.objective)