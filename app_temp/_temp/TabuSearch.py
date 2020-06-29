'''
Created on May 24, 2019

@author: lucassoares
'''
import math
from pulp import *
import numpy as np
import app.Site as Site
import app.Vehicle as Vehicle
import utm
import random
import sys


vehicles = [Vehicle.Vehicle(59940)]
BestSolutionVehicles = [Vehicle.Vehicle(59940)]
cost = 0
BestSolutionCost = 0
iterations = 5
TABU_Horizon = 10

def calculate_energy_cost(p1,p2):
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

def get_energy_cost(listaSites):
    
        sites = ['0']
        for site in listaSites:
            sites.append(site.getId())

        positions = dict( (a.getId(), a.getNewPosicao() ) for a in listaSites )

        utm_conversion = utm.from_latlon(48.879049,2.367448)
        positions['0']=(utm_conversion[0], utm_conversion[1], 0)

        distances=dict( ((s1,s2), calculate_energy_cost(positions[s1],positions[s2])) for s1 in positions for s2 in positions if s1!=s2)

        for i in sites:
            for j in sites:
                if i!=j:
                    print('Custo energético entre '+ i+' e '+ j+' :'+ str(distances[(i,j)]))
        K = 1 
        prob=LpProblem("vehicle",LpMinimize)

        x = LpVariable.dicts('x',distances, 0,1,LpBinary)
        u = LpVariable.dicts('u', sites, 0, len(sites)-1, LpInteger)

        cost = (lpSum([  x[(i,j)]  * distances[(i,j)]for (i,j) in distances ]))
        prob+=cost

        for k in sites:
            prob+= lpSum([ x[(i,k)] for i in sites if (i,k) in x]) ==1
            prob+=lpSum([ x[(k,i)] for i in sites if (k,i) in x]) ==1

        N=len(sites)/K
        for i in sites:
                for j in sites:
                        if i != j and (i != '0' and j!= '0') and (i,j) in x:
                                prob += u[i] - u[j] <= (N)*(1-x[(i,j)]) - 1

        prob.solve()
        return(value(prob.objective))

def unassigned_customer_exists(sites):
    for s in sites:
        if (s.IsRouted()):
            return "true"
    return "false"


def get_flight_plan_tabu_search(listaSites, min_cost_energy):
    global cost
    global vehicles
    global BestSolutionVehicles
    global BestSolutionCost
    global TABU_Horizon
    global iterations

    cost = min_cost_energy

    #We use 1-0 exchange move
    routesFrom = []
    routesTo = []

    #MovingNodeDemand = 0
    VehIndexFrom = 0 
    VehIndexTo = 0

    BestNCost = sys.float_info.max

    print(BestNCost)

    NeighborCost = 0 

    SwapIndexA = -1
    SwapIndexB = -1
    SwapRouteFrom = -1
    SwapRouteTo = -1
    iteration_number = 0

    positions = dict( (a.getId(), a.getNewPosicao() ) for a in listaSites )
    utm_conversion = utm.from_latlon(48.879049,2.367448)
    positions['0']=(utm_conversion[0], utm_conversion[1], 0)

    #straight line distance for simplicity
    distances=dict( ((s1,s2), calculate_energy_cost(positions[s1],positions[s2])) for s1 in positions for s2 in positions if s1!=s2)

    DimensionCustomer = len(listaSites)
    TABU_Matrix = []

    BestSolutionCost = cost

    site = Site.Site(str(0), (48.879049, 2.367448, 0) , False)
    
    vehicles[0].add_node(site, 0)


    while (True):
        print ("Done 1")    


        for veh in vehicles:

            
            routesFrom = veh.routes

            print ("Done 2")    


            ##Not possible to move depot!
            for i in range(len(routesFrom)):         

                print ("Done 3")    

                for VehIndexTo in range(len(vehicles)):
                    routesTo = vehicles[VehIndexTo].routes
                    print ("Done 4")

                    for j in range(len(routesTo)):         

                        print ("Done 5")
                        ##Not possible to move after last Depot!
                        
                        # MovingNodeDemand = routesFrom[i].demand

                        #if ( (VehIndexFrom == VehIndexTo) or vehicles(VehIndexTo).CheckIfFits(MovingNodeDemand) ):
                            ##If we assign to a different route check capacity constrains
                            ##if in the new route is the same no need to check for capacity

                        if ( not (((j == i) or (j == i - 1)))): 
                            print ("Done 6")
                            # Not a move that Changes solution cost
                            MinusCost1 = distances[routesFrom(i - 1).getId()][routesFrom(i).getId()]
                            MinusCost2 = distances[routesFrom(i).getId()][routesFrom(i + 1).getId()]
                            MinusCost3 = distances[routesTo(j).getId()][routesTo(j + 1).getId()]

                            AddedCost1 = distances[routesFrom(i - 1).getId()][routesFrom(i + 1).getId()]
                            AddedCost2 = distances[routesTo(j).getId()][routesFrom(i).getId()]
                            AddedCost3 = distances[routesFrom(i).getId()][routesTo(j + 1).getId()]

                            ##Check if the move is a Tabu! - If it is Tabu break
                            if ((TABU_Matrix[routesFrom(i - 1).getId()][routesFrom(i + 1).getId()] != 0)
                                    or (TABU_Matrix[routesTo(j).getId()][routesFrom(i).getId()] != 0)
                                    or (TABU_Matrix[routesFrom(i).getId()][routesTo(j + 1).getId()] != 0)):
                                break

                            NeighborCost = AddedCost1 + AddedCost2 + AddedCost3 - MinusCost1 - MinusCost2 - MinusCost3

                            if (NeighborCost < BestNCost):

                                print ("Done 7")
                                BestNCost = NeighborCost
                                SwapIndexA = i
                                SwapIndexB = j
                                SwapRouteFrom = VehIndexFrom
                                SwapRouteTo = VehIndexTo


            if ( not len(TABU_Matrix) == 0):
                for o in range(len(TABU_Matrix(0))):
                    for p in range(len(TABU_Matrix(0))):
                        if (TABU_Matrix[o][p] > 0):
                            TABU_Matrix[o][p] -= 1
                    

            routesFrom = vehicles[SwapRouteFrom].routes
            routesTo = vehicles[SwapRouteTo].routes
            vehicles[SwapRouteFrom].routes = None
            vehicles[SwapRouteTo].routes = None

            if ( len(routesFrom) > 1):
                SwapNode = routesFrom[SwapIndexA]
                NodeIDBefore = routesFrom(SwapIndexA - 1).getId()
                NodeIDAfter = routesFrom(SwapIndexA + 1).getId()
            else:
                NodeIDBefore

            if ( len(routesTo) > 1):
                NodeID_F = routesTo(SwapIndexB).getId()
                NodeID_G = routesTo(SwapIndexB + 1).getId()

            
            randomDelay1 = random.randrange(5)
            randomDelay2 = random.randrange(5)
            randomDelay3 = random.randrange(5)

            TABU_Matrix[NodeIDBefore][SwapNode.getId()] = TABU_Horizon + randomDelay1
            TABU_Matrix[SwapNode.getId()][NodeIDAfter] = TABU_Horizon + randomDelay2
            TABU_Matrix[NodeID_F][NodeID_G] = TABU_Horizon + randomDelay3

            routesFrom.remove(SwapIndexA)

            if (SwapRouteFrom == SwapRouteTo):
                if (SwapIndexA < SwapIndexB):
                    routesTo.insert(SwapIndexB, SwapNode)
                else:
                    routesTo.insert(SwapIndexB + 1, SwapNode)
                
            else:
                routesTo.insert(SwapIndexB + 1, SwapNode)
            

            vehicles[SwapRouteFrom].routes = routesFrom
            #vehicles[SwapRouteFrom].load -= MovingNodeDemand

            vehicles[SwapRouteTo].routes = routesTo
           # vehicles[SwapRouteTo].load += MovingNodeDemand

            cost += BestNCost

            if (cost < BestSolutionCost):
                iteration_number = 0
                SaveBestSolution()
            else:
                iteration_number += 1

            if (iterations == iteration_number):
                break

        vehicles = BestSolutionVehicles
        cost = BestSolutionCost


def SaveBestSolution():
    global cost
    global vehicles
    global BestSolutionVehicles
    global BestSolutionCost

    BestSolutionCost = cost

    for j in range(len(vehicles)):

        BestSolutionVehicles[j].routes = []

        if ( not vehicles[j].routes.isEmpty()):
            for k in range(len(vehicles[j].routes)):
                n = vehicles[j].routes(k)
                BestSolutionVehicles[j].routes.append(n)


def printsolution():

    global cost
    global vehicles
    global BestSolutionVehicles
    global BestSolutionCost

    for j in range(len(vehicles)):
        if (not vehicles[j].routes.isEmpty()):
            print("Vehicle " + j + ":")
            RoutSize = len(vehicles[j].routes)
            for k in range(len(vehicles[j].routes)):

                if (k == RoutSize - 1):
                    print(vehicles[j].routes(k).getId())
                else:
                    print(vehicles[j].routes(k).getId() + "->")

    print("\nBest Value: " + cost + "\n");
 
