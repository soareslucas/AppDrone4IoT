'''
Created on May 24, 2019

@author: lucassoares
'''
import pulp as opt
import numpy as np
#import seaborn as sn
import random
#from mpl_toolkits import mplot3d
import app.Site as Site


minimoEnergia = 0

# total number of clusters (customers)
N = 0

# total number of UAVs (vehicles)
K = 1

# total number of launch sites
L = 1

# total number of landing sites
C = 1

# i = index for traveling from node i
# j = index for traveling to node j
# k = index for the vehicle
# xijk = binary variable indicating whether UAV k traveled from node i to j
# cij = distance from node i to j
# tijk = travel time from node i to node j for vehicle k
# ti = arrival time of UAV at target i
# tjk = arrival time of UAV k at landing site j
# sik = service time for node i for UAV k
# rk = max route time allowed for UAV k


def getValueMinimoEnergia():
    global minimoEnergia
    return(minimoEnergia)



def get_next_site(parent, non_zero_edges):
        '''helper function to get the next edge'''
        edges = [e for e in non_zero_edges if e[0]==parent]
        for e in edges:
                non_zero_edges.remove(e)
        return edges



def getMinimoEnergia(listaSites):
    
        sites = ['org']
                
        for site in listaSites:
            sites.append(site.getId())

        #make some positions (so we can plot this)
        positions = dict( (a.getId(), a.getPosicao() ) for a in listaSites )
        
        positions['org']=(0,0,0)

        #straight line distance for simplicity
        d = lambda p1,p2: np.sqrt( (p1[0]-p2[0])**2+ (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)

        #calculate all the pairs
        distances=dict( ((s1,s2), d(positions[s1],positions[s2])) for s1 in positions for s2 in positions if s1!=s2)

        for i in sites:
            for j in sites:
                if i!=j:
                    print('distancia entre: '+ i+' e '+ j+' '+ str(distances[(i,j)]))
        
        #the number of sales people 
        K = 1 

        #create the problem
        prob= opt.LpProblem("vehicle",opt.LpMinimize)
        #indicator variable if site i is connected to site j in the tour
        x = opt.LpVariable.dicts('x',distances, 0,1,opt.LpBinary)
        #dummy vars to eliminate subtours
        u = opt.LpVariable.dicts('u', sites, 0, len(sites)-1, opt.LpInteger)

        #the objective
        cost = (opt.lpSum([  x[(i,j)]  * distances[(i,j)]for (i,j) in distances ]))
        prob+=cost

        for k in sites:
            #every site has exactly one inbound connection
            prob+= opt.lpSum([ x[(i,k)] for i in sites if (i,k) in x]) ==1
            #every site has exactly one outbound connection
            prob+=opt.lpSum([ x[(k,i)] for i in sites if (k,i) in x]) ==1

        
        #subtour elimination
        N=len(sites)/K
        for i in sites:
                for j in sites:
                        if i != j and (i != 'org' and j!= 'org') and (i,j) in x:
                                prob += u[i] - u[j] <= (N)*(1-x[(i,j)]) - 1


        prob.solve()

        non_zero_edges = [ e for e in x if opt.value(x[e]) != 0 ]
        tours = get_next_site('org', non_zero_edges)
        tours = [ [e] for e in tours ]

        for t in tours:
                while t[-1][1] !='org':
                        t.append(get_next_site(t[-1][1], non_zero_edges)[-1])
                
        for t in tours:
                print(' -> '.join([ a for a,b in t]+['org']))

        
        return(opt.value(prob.objective))




def getMaximoDeSensores(listaSites, autonomia):
        sites = ['org']
                
        for site in listaSites:
            sites.append(site.getId())

        #make some positions (so we can plot this)
        positions = dict( (a.getId(), a.getPosicao() ) for a in listaSites )
        
        positions['org']=(0,0,0)

        xdata = [None] * len(sites)
        ydata = [None] * len(sites)
        zdata = [None] * len(sites)

        count = 0

        for s in sites:
                p = positions[s]
                xdata[count] = p[0]
                ydata[count] = p[1]
                zdata[count] = p[2]
                count = count + 1


        #straight line distance for simplicity
        d = lambda p1,p2: np.sqrt( (p1[0]-p2[0])**2+ (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)

        #calculate all the pairs
        distances=dict( ((s1,s2), d(positions[s1],positions[s2])) for s1 in positions for s2 in positions if s1!=s2)

        #the number of sales people 
        K = 1 

        #create the problme
        prob= opt.LpProblem("vehicle",opt.LpMaximize)


        #indicator variable if site i is connected to site j in the tour
        x = opt.LpVariable.dicts('x',distances, 0,1,opt.LpBinary)
        #dummy vars to eliminate subtours
        u = opt.LpVariable.dicts('u', sites, 0, len(sites)-1, opt.LpInteger)


        #the objective
        cost = (opt.lpSum([x[(i,j)] for (i,j) in x]))
        prob+=cost

        for k in sites:
                prob+= opt.lpSum([ x[(i,k)] for i in sites if (i,k) in x]) == opt.lpSum([ x[(k,i)] for i in sites if (k,i) in x])
        
        for k in sites:
                prob+= opt.lpSum([ x[('org',k)] for k in sites if ('org',k) in x]) == 1
        
        for k in sites:
                prob+= opt.lpSum([ x[(k,'org')] for k in sites if (k, 'org') in x]) == 1

        prob+= opt.lpSum([  x[(i,j)]  * distances[(i,j)]for (i,j) in distances ]) <= autonomia

        
        #subtour elimination
        N=len(sites)/K
        for i in sites:
                for j in sites:
                        if i != j and (i != 'org' and j!= 'org') and (i,j) in x:
                                prob += u[i] - u[j] <= (N)*(1-x[(i,j)]) - 1


        prob.solve()

        non_zero_edges = [ e for e in x if opt.value(x[e]) != 0 ]
        tours = get_next_site('org', non_zero_edges)
        tours = [ [e] for e in tours ]

        for t in tours:
                while t[-1][1] !='org':
                        t.append(get_next_site(t[-1][1], non_zero_edges)[-1])
                
        for t in tours:
                print(' -> '.join([ a for a,b in t]+['org']))
                
        
        distanciaTotal = 0
        for i in sites:
            for j in sites:
                if i != j :
                    distanciaTotal += opt.value(x[(i,j)])  * distances[(i,j)]
        
        totalSensores = -1
        for i in sites:
            for j in sites:
                if i != j:
                    totalSensores += opt.value(x[(i,j)])
            

        maxSensores = opt.value(prob.objective)
        
        global minimoEnergia
        
        minimoEnergia = getMinimoEnergiaComMaxSensores(maxSensores, distances, sites)
            
        return('O maximo de sensores é: ' + str(maxSensores-1) +' <br> O custo inicial para realização do voo seria: '+ str(distanciaTotal)+' <br> O mínimo de custo alcançado é: '+str(minimoEnergia))
    
    
def getMinimoEnergiaComMaxSensores(maxSensores, distances, sites):
       #create the problme
        prob= opt.LpProblem("vehicle",opt.LpMinimize)


        #indicator variable if site i is connected to site j in the tour
        x = opt.LpVariable.dicts('x',distances, 0,1,opt.LpBinary)
        #dummy vars to eliminate subtours
        u = opt.LpVariable.dicts('u', sites, 0, len(sites)-1, opt.LpInteger)


        #the objective
        cost =  ( opt.lpSum([  x[(i,j)]  * distances[(i,j)]for (i,j) in distances ])) 
        prob+=cost

        for k in sites:
                prob+=opt.lpSum([ x[(i,k)] for i in sites if (i,k) in x]) == opt.lpSum([ x[(k,i)] for i in sites if (k,i) in x])
        
        for k in sites:
                prob+= opt.lpSum([ x[('org',k)] for k in sites if ('org',k) in x]) == 1
        
        for k in sites:
                prob+= opt.lpSum([ x[(k,'org')] for k in sites if (k, 'org') in x]) == 1
        
        prob+= opt.lpSum([x[(i,j)] for (i,j) in x]) == maxSensores
        
        
        #subtour elimination
        N=len(sites)/1
        for i in sites:
                for j in sites:
                        if i != j and (i != 'org' and j!= 'org') and (i,j) in x:
                                prob += u[i] - u[j] <= (N)*(1-x[(i,j)]) - 1


        prob.solve()
        
        return opt.value(prob.objective)

