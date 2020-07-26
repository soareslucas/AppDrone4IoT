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

from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import proj3d
from mpl_toolkits.mplot3d.proj3d import proj_transform
from mpl_toolkits.mplot3d.axes3d import Axes3D
from matplotlib.text import Annotation
from matplotlib.patches import FancyArrowPatch

import matplotlib.pyplot as plt

import numpy as np



import math
import utm
rnd = np.random

minimoEnergia = 0

class Annotation3D(Annotation):
    def __init__(self, text, xyz, *args, **kwargs):
        super().__init__(text, xy=(0,0), *args, **kwargs)
        self._xyz = xyz

    def draw(self, renderer):
        x2, y2, z2 = proj_transform(*self._xyz, renderer.M)
        self.xy=(x2,y2)
        super().draw(renderer)


def _annotate3D(ax,text, xyz, *args, **kwargs):
    '''Add anotation `text` to an `Axes3d` instance.'''

    annotation= Annotation3D(text, xyz, *args, **kwargs)
    ax.add_artist(annotation)





class Arrow3D(FancyArrowPatch):

    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        FancyArrowPatch.draw(self, renderer)

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


        """         powerHovering = np.sqrt(W/2*rho) * np.sqrt(w/ np.power(W,2) * 3,14)
                energyHovering = powerHovering x timeHovering
        """


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

        edges = [e for e in non_zero_edges if e[0]==parent]
        for e in edges:
                non_zero_edges.remove(e)
        return edges



def get_next_site_cv(parent, non_zero_edges):

        #print(non_zero_edges)
        edges = []
        for e in non_zero_edges:
                if(parent == e[0]):
                        edges.append(e)

        for e in edges:
                non_zero_edges.remove(e)
        return edges



def getMax(listaSites, vehicles):

        # Autonomia em J |||  (59940 - 1500 mAh - 11.1V )   (99900 - 2500 mAh - 11.1V ) (159840 - 4000 mAh - 11.1V )
        autonomy = [80000, 80000]
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

        hover = [0]
        W = 19
        rho = 1.225
        a = float(W/2*rho)
        b =  float ( W/ math.pow(W,2) *  (3.14))

        #print(a)
        #print(b)
        powerHovering = (math.sqrt(a) * math.sqrt(b) )
        
        for k in range(customer_count):
                sec = listaSites[k].getBuffer()
                energy =  powerHovering * sec
                hover.append(energy)

        
        

        index = 0
        sites = []
        for site in listaSites:
            site.setIdArray(index)
            sites.append(site)
            index += 1

       # positions = dict( (int(a.getIdArray()), a.getNewPosicao() ) for a in listaSites )

        positions = dict( (int(a.getIdArray()), a.getPosicao() ) for a in listaSites )


        energy_costs = np.zeros((customer_count, customer_count, vehicle_count))

        for k in range(vehicle_count):
                for j in range(customer_count):
                        for i in range(customer_count):
                                energy_costs[i][j][k] = calculateEnergyCost(positions[i], positions[j], vehicles[k])
                                #print('Custo energético entre '+ str(i)+' e '+ str(j)+' no veículo ' + str(k) +' :'+ str( energy_costs[i][j][k] ) )
                                energy_costs[i][j][k] += hover[i]
                                #print('Custo energético entre '+ str(i)+' e '+ str(j)+' no veículo ' + str(k) +' :'+ str( energy_costs[i][j][k] ) )
                

        prob=LpProblem("vehicle",LpMaximize)
        x = [[[LpVariable("x%s_%s,%s"%(i,j,k), cat="Binary") if i != j else None for k in range(vehicle_count)]for j in range(customer_count)] for i in range(customer_count)]

        #objective function
        cost = lpSum(x[i][j][k] if i != j else 0
                          for k in range(vehicle_count) 
                          for j in range(customer_count) 
                          for i in range (customer_count) ) 
        prob+=cost

        for k in range(vehicle_count):
                for i in range(customer_count):
                        prob += lpSum(x[i][j][k] if i != j else 0  for j in range( customer_count) ) == lpSum(x[j][i][k]  if i != j else 0  for j in range(customer_count) )


        for i in range(1,customer_count):
                prob += lpSum(x[i][j][k] if i != j else 0  for j in range(customer_count)  for k in range(vehicle_count) ) <= 1
                prob +=  lpSum(x[j][i][k]  if i != j else 0  for j in range(customer_count)  for k in range(vehicle_count)  ) <= 1



        for k in range(vehicle_count):
                prob += lpSum(x[0][i][k]  for i in range(customer_count) ) == 1
                prob += lpSum(x[i][0][k]  for i in range(customer_count)  ) == 1


        for k in range(vehicle_count):
                        prob += lpSum([ q[j] * x[i][j][k] if i != j else 0 for i in range(customer_count) for j in range (customer_count) ]) <= Q[k] 

        for k in range(vehicle_count):
                prob += lpSum([ energy_costs[i][j][k] * x[i][j][k] if i != j else 0 for i in range(customer_count) for j in range (customer_count) ]) <= autonomy[k]


        #prob += lpSum( energy_costs[i][j][k] * x[i][j][k] if i != j else 0 for i in range(customer_count) for j in range (customer_count) for k in range(vehicle_count) for k in range(vehicle_count)) <= 100000


        subtours = []
        for i in range(2,customer_count):
                subtours += itertools.combinations(range(1,customer_count), i)

        for s in subtours:
                prob += lpSum(x[i][j][k] if i !=j else 0 for i, j in itertools.permutations(s,2) for k in range(vehicle_count)) <= len(s) - 1


        prob.solve()
        print('Status: '+ str(LpStatus[prob.status]))  


        #print('Máximo de sensores: ' + str(value(prob.objective) -2))
        #print('Total capacidade armazenamento drone: ' + str(Q[0] + Q[1]) )
        
        totalSync = 0        
        for i in range(customer_count):
                for j in range(customer_count):
                        for k in range(vehicle_count):
                                if i != j:
                                        totalSync += q[j] * value(x[i][j][k])

        #print('Total sincronizado: '+ str(totalSync))



        normalEnergy = 0        
        for i in range(customer_count):
                for j in range(customer_count):
                        for k in range(vehicle_count):
                                if i != j:
                                        normalEnergy += energy_costs[i][j][k] * value(x[i][j][k])

        #print('Total gasto energértico: '+ str(normalEnergy))


        totalSensorsV1 = 0
        totalSensorsV2 = 0
        totalSyncV1 = 0
        totalSyncV2 = 0

        for k in range(vehicle_count):
                for i in range(customer_count):
                        for j in range(customer_count):
                                if ( (i != j) and value(x[i][j][k]) == 1):
                                        if k == 0:
                                                totalSyncV1 += q[j] * value(x[i][j][k])
                                                totalSensorsV1 += 1
                                        else:
                                                totalSyncV2 += q[j] * value(x[i][j][k])
                                                totalSensorsV2 += 1
                                                        

        non_zero_edges = []
        for i in range(customer_count):
                for j in range(customer_count):
                        for k in range(vehicle_count):
                                if ( (i != j) and  value( x[i][j][k]) != 0 ):
                                        a = [i,j,k]
                                        non_zero_edges.append(a)


        #for n in non_zero_edges:
                #print (n)
        

        tours = get_next_site_cv(0, non_zero_edges)
        tours = [ [e] for e in tours ]

        for t in tours:
                while t[-1][1] != 0:
                        t.append(get_next_site_cv(t[-1][1], non_zero_edges)[-1])

        #for t in tours:
        #        print(' -> '.join(str([ a for a,b,c in t]+[0]) ))


        maxSensors = value(prob.objective)
        
        res = getMinimoEnergiaComMaxSensores(vehicles, maxSensors, energy_costs, listaSites, positions, autonomy)

        minEnergy = res[0]
        totalSyncMinEnergy = res[1]

        totalStorageV1 = Q[0]
        totalStorageV2 = Q[1]
        totalStorage = Q[0] + Q[1]

        #return maxSensors-2, normalEnergy, totalSensorsV1-1, totalSensorsV2-1, totalStorage , totalStorageV1, totalStorageV2, totalSync, totalSyncV1, totalSyncV2, minEnergy, totalSyncMinEnergy
        return maxSensors-2, normalEnergy, minEnergy



def getMinimoEnergiaComMaxSensores(vehicles, maxSensores, energy_costs, listaSites, positions, autonomy):

        customer_count = len(listaSites)
        vehicle_count = len(vehicles)

        q = []
        for k in range(customer_count):
                q.append(listaSites[k].getBuffer())
        
        Q = []
        for k in range(vehicle_count):
                Q.append(vehicles[k].getCapacity())
                

        prob=LpProblem("vehicle",LpMinimize)
        x = [[[LpVariable("x%s_%s,%s"%(i,j,k), cat="Binary") if i != j else None for k in range(vehicle_count)]for j in range(customer_count)] for i in range(customer_count)]


        #objective function
        cost = lpSum(energy_costs[i][j][k] * x[i][j][k] if i != j else 0
                          for k in range(vehicle_count) 
                          for j in range(customer_count) 
                          for i in range (customer_count) ) 
        prob+=cost

        for k in range(vehicle_count):
                for i in range(customer_count):
                        prob += lpSum(x[i][j][k] if i != j else 0  for j in range( customer_count) ) == lpSum(x[j][i][k]  if i != j else 0  for j in range(customer_count) )


        for i in range(1,customer_count):
                prob += lpSum(x[i][j][k] if i != j else 0  for j in range(customer_count)  for k in range(vehicle_count) ) <= 1
                prob +=  lpSum(x[j][i][k]  if i != j else 0  for j in range(customer_count)  for k in range(vehicle_count)  ) <= 1


        for k in range(vehicle_count):
                prob += lpSum(x[0][i][k]  for i in range(customer_count) ) == 1
                prob += lpSum(x[i][0][k]  for i in range(customer_count)  ) == 1

    
        for k in range(vehicle_count):
                prob += lpSum([ q[j] * x[i][j][k] if i != j else 0 for i in range(customer_count) for j in range (customer_count) ]) <= Q[k] 

        for k in range(vehicle_count):
                prob += lpSum([ energy_costs[i][j][k] * x[i][j][k] if i != j else 0 for i in range(customer_count) for j in range (customer_count) ]) <= autonomy[k]

        
        prob+= lpSum( x[i][j][k] if i != j else 0
                          for k in range(vehicle_count) 
                          for j in range(customer_count) 
                          for i in range (customer_count) ) == maxSensores

        subtours = []
        for i in range(2,customer_count):
                subtours += itertools.combinations(range(1,customer_count), i)

        for s in subtours:
                prob += lpSum(x[i][j][k] if i !=j else 0 for i, j in itertools.permutations(s,2) for k in range(vehicle_count)) <= len(s) - 1



        prob.solve()

        
        totalSync = 0
        
        for i in range(customer_count):
                for j in range(customer_count):
                        for k in range(vehicle_count):
                                if i != j:
                                        totalSync += q[j] * value(x[i][j][k])

       #print('Total sincronizado: '+ str(totalSync))

        non_zero_edges = []
        for i in range(customer_count):
                for j in range(customer_count):
                        for k in range(vehicle_count):
                                if ( (i != j) and  value( x[i][j][k]) != 0 ):
                                        a = [i,j,k]
                                        non_zero_edges.append(a)


        tours = get_next_site_cv(0, non_zero_edges)
        tours = [ [e] for e in tours ]

        for t in tours:
                while t[-1][1] != 0:
                        t.append(get_next_site_cv(t[-1][1], non_zero_edges)[-1])

        #for t in tours:
                #print(' -> '.join(str([ a for a,b,c in t]+[0]) ))


       

        fig = plt.figure()
        
        ax = fig.add_subplot(111, projection='3d')


        for i in range(customer_count):    
                a =  positions[i]
                if i == 0:
                        ax.scatter(a[0], a[1], a[2], c='green', marker='o')
                        #plt.text(a[0], a[1], "depot", fontsize=12)
                else:
                        ax.scatter(a[0], a[1], a[2], c='yellow', marker='o')
                        #plt.text(a[0], a[1], str(sites[i].getId()), fontsize=12)


        

        vehicleTour = tours[0]
        for vt in vehicleTour:
                A = positions[vt[0]]
                B = positions[vt[1]]

                a = Arrow3D([A[0], B[0]], [A[1], B[1]], [A[2], B[2]], mutation_scale=20, lw=1, arrowstyle="-|>", color="k")
                
                text = str(vt[0]) 

                _annotate3D(ax ,text, (A[0], A[1], A[2]), xytext=(3,3),textcoords='offset points')


                ax.add_artist(a)

        vehicleTour = tours[1]
        for vt in vehicleTour:
                A = positions[vt[0]]
                B = positions[vt[1]]

                a = Arrow3D([A[0], B[0]], [A[1], B[1]], [A[2], B[2]], mutation_scale=20, lw=1, arrowstyle="-|>", color="g")
                
                text = str(vt[0]) 
                _annotate3D(ax,text, (A[0], A[1], A[2]), xytext=(3,3),textcoords='offset points')


                ax.add_artist(a)




        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')

        #plt.show()



 
        return( value(prob.objective), totalSync)