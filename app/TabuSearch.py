'''
Created on May 24, 2019

@author: lucassoares
'''
import math
from pulp import *
import numpy as np
import app.Site as Site
import utm
import random



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

        distances=dict( ((s1,s2), calculateEnergyCost(positions[s1],positions[s2])) for s1 in positions for s2 in positions if s1!=s2)

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


def get_flight_plan_tabu_search(listaSites, vehicles, BestSolutionVehicles, noOfVehicles, cost, TABU_Horizon, iterations, min_cost_energy):

    //We use 1-0 exchange move
    routes_from = []
    routes_to = []

    moving_node_demand = 0

    veh_index_from = 0 
    veh_index_to = 0

    best_n_cost = 0
    neighbor_cost = 0 

    swap_index_a = -1
    swap_index_b = -1
    swap_route_from = -1
    swap_route_to = -1
    iteration_number = 0


    #make some positions (so we can plot this)
    positions = dict( (a.getId(), a.getNewPosicao() ) for a in listaSites )
    
    utm_conversion = utm.from_latlon(48.879049,2.367448)
    positions['0']=(utm_conversion[0], utm_conversion[1], 0)

    #straight line distance for simplicity
    d = lambda p1,p2: np.sqrt( (p1[0]-p2[0])**2+ (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)

    distances=dict( ((s1,s2), d(positions[s1],positions[s2])) for s1 in positions for s2 in positions if s1!=s2)


    DimensionCustomer = listaSites.length
    TABU_Matrix = []

    min_cost_energy


    while (true):

        for veh in vehicles:
            
            routes_from = veh.routes


            ##Not possible to move depot!
            for i in range(len(routes_from)):         
                for VehIndexTo in range(len(vehicles)):         
                    routesTo = vehicles[VehIndexTo].routes

                    for j in range(len(routesTo)):         
                        ##Not possible to move after last Depot!
                        
                        MovingNodeDemand = routes_from.

                        if ((VehIndexFrom == VehIndexTo) || this.vehicles[VehIndexTo].CheckIfFits(MovingNodeDemand)):
                            //If we assign to a different route check capacity constrains
                            //if in the new route is the same no need to check for capacity

                            if (!((VehIndexFrom == VehIndexTo) && ((j == i) || (j == i - 1)))):  // Not a move that Changes solution cost
                                double MinusCost1 = this.distances[routesFrom.get(i - 1).NodeId][routesFrom.get(i).NodeId]
                                double MinusCost2 = this.distances[routesFrom.get(i).NodeId][routesFrom.get(i + 1).NodeId]
                                double MinusCost3 = this.distances[routesTo.get(j).NodeId][routesTo.get(j + 1).NodeId]

                                double AddedCost1 = this.distances[routesFrom.get(i - 1).NodeId][routesFrom.get(i + 1).NodeId]
                                double AddedCost2 = this.distances[routesTo.get(j).NodeId][routesFrom.get(i).NodeId]
                                double AddedCost3 = this.distances[routesFrom.get(i).NodeId][routesTo.get(j + 1).NodeId]

                                //Check if the move is a Tabu! - If it is Tabu break
                                if ((TABU_Matrix[routesFrom.get(i - 1).NodeId][routesFrom.get(i + 1).NodeId] != 0)
                                        || (TABU_Matrix[routesTo.get(j).NodeId][routesFrom.get(i).NodeId] != 0)
                                        || (TABU_Matrix[routesFrom.get(i).NodeId][routesTo.get(j + 1).NodeId] != 0)):
                                    break

                                NeighborCost = AddedCost1 + AddedCost2 + AddedCost3 - MinusCost1 - MinusCost2 - MinusCost3

                                if (NeighborCost < BestNCost):
                                    BestNCost = NeighborCost
                                    SwapIndexA = i
                                    SwapIndexB = j
                                    SwapRouteFrom = VehIndexFrom
                                    SwapRouteTo = VehIndexTo

       #     for (int o = 0; o < TABU_Matrix[0].length; o++) {
        #        for (int p = 0; p < TABU_Matrix[0].length; p++) {
       #             if (TABU_Matrix[o][p] > 0):
       #                 TABU_Matrix[o][p]--
       #         }
      #      }

            routesFrom = this.vehicles[SwapRouteFrom].routes
            routesTo = this.vehicles[SwapRouteTo].routes
            this.vehicles[SwapRouteFrom].routes = null
            this.vehicles[SwapRouteTo].routes = null

            Node SwapNode = routesFrom.get(SwapIndexA)

            int NodeIDBefore = routesFrom.get(SwapIndexA - 1).NodeId
            int NodeIDAfter = routesFrom.get(SwapIndexA + 1).NodeId
            int NodeID_F = routesTo.get(SwapIndexB).NodeId
            int NodeID_G = routesTo.get(SwapIndexB + 1).NodeId

            Random TabuRan = new Random()
            int randomDelay1 = TabuRan.nextInt(5)
            int randomDelay2 = TabuRan.nextInt(5)
            int randomDelay3 = TabuRan.nextInt(5)

            TABU_Matrix[NodeIDBefore][SwapNode.NodeId] = this.TABU_Horizon + randomDelay1
            TABU_Matrix[SwapNode.NodeId][NodeIDAfter] = this.TABU_Horizon + randomDelay2
            TABU_Matrix[NodeID_F][NodeID_G] = this.TABU_Horizon + randomDelay3

            routesFrom.remove(SwapIndexA)

            if (SwapRouteFrom == SwapRouteTo):
                if (SwapIndexA < SwapIndexB):
                    routesTo.add(SwapIndexB, SwapNode)
                else:
                    routesTo.add(SwapIndexB + 1, SwapNode)
                
            else:
                routesTo.add(SwapIndexB + 1, SwapNode)
            

            vehicles[SwapRouteFrom].routes = routesFrom
            vehicles[SwapRouteFrom].load -= MovingNodeDemand

            vehicles[SwapRouteTo].routes = routesTo
            vehicles[SwapRouteTo].load += MovingNodeDemand

            cost += BestNCost

            if (cost < BestSolutionCost):
                iteration_number = 0
                SaveBestSolution()
            else:
                iteration_number += 1

            if (iterations == iteration_number):
                break

        ##this.vehicles = this.BestSolutionVehicles
        ##this.cost = this.BestSolutionCost