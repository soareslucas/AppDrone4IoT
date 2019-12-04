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
import app.Site as Site

minimoEnergia = 0

def getValueMinimoEnergia():
        global minimoEnergia
        return(minimoEnergia)



def get_next_site(parent, non_zero_edges):
        '''helper function to get the next edge'''
        edges = [e for e in non_zero_edges if e[0]==parent]
        for e in edges:
                non_zero_edges.remove(e)
        return edges

def get_line_flight_plan(sites, id):
        print(str(id))
        for s in sites:
                if(s.getId() == id ): 
                        coordinates = s.getPosicao()
                        lat = str(coordinates[0])
                        lon = str(coordinates[1])
                        height = str(coordinates[2])
                        digits = len(height)

                        if (digits == 1):
                                height = '00'+height
                        if (digits == 2):
                                height = '0'+height

                        return ('1       0       3       16      0.000000        '
                        + '0.000000        0.000000        0.000000        ' + lat[:9] 
                        +'       ' + lon[:8] +'        '+height+'.000000      1breakline')



def generate_file_flight_plan(tours, listaSites):
        text = ('GC WPL 110\n'
        + '0       1       0       0       0       0       0       0       0       0       0       1\n' 
        + '1       0       3       16      0.000000        0.000000        0.000000        0.000000        48.878940       2.368091        000.000000      1\n')
        
        tourFlightPlan = ''
        for t in tours:
                tourFlightPlan += (str([ get_line_flight_plan(listaSites, a) for a,b in t if a != 'org' ] ) )

        tourFlightPlan = tourFlightPlan.replace(']', '')
        tourFlightPlan = tourFlightPlan.replace('[', '')
        tourFlightPlan = tourFlightPlan.replace(',', '')
        tourFlightPlan = tourFlightPlan.replace("'", '')

        tourFlightPlan = tourFlightPlan.split('breakline')
        del tourFlightPlan[-1]

        print(tourFlightPlan)

        index = 2
        for fp in tourFlightPlan:
                fpTemp = ''
                f = list(fp)
                print(f)
                if (str(f[0]) == ' '):
                        fpTemp = fp.replace(' ' , '', 1) 
                else:
                        fpTemp = fp

                fpTemp = fpTemp.replace('1' , str(index), 1) 
                index += 1
                text += str(fpTemp) + '\n'

        text+=  str(index)+'       0       3       16      0.000000        0.000000        0.000000        0.000000        48.878940       2.368091        000.000000      1'

        file = open("flightplan.txt", "w") 
        file.write(text) 
        file.close() 


def calculateEnergyCost(p1,p2):
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


def getMinimoEnergia(listaSites):
    
        sites = ['org']
                
        for site in listaSites:
            sites.append(site.getId())

        #make some positions (so we can plot this)
        positions = dict( (a.getId(), a.getNewPosicao() ) for a in listaSites )
        positions['org']=(453668.79, 5414190.73,0)

        #calculate all the pairs
        distances=dict( ((s1,s2), calculateEnergyCost(positions[s1],positions[s2])) for s1 in positions for s2 in positions if s1!=s2)

        for i in sites:
            for j in sites:
                if i!=j:
                    print('Custo energético entre '+ i+' e '+ j+' :'+ str(distances[(i,j)]))
        
        #the number of sales people 
        K = 1 

        #create the problme
        prob=LpProblem("vehicle",LpMinimize)


        #indicator variable if site i is connected to site j in the tour
        x = LpVariable.dicts('x',distances, 0,1,LpBinary)
        #dummy vars to eliminate subtours
        u = LpVariable.dicts('u', sites, 0, len(sites)-1, LpInteger)


        #the objective
        cost = (lpSum([  x[(i,j)]  * distances[(i,j)]for (i,j) in distances ]))
        prob+=cost

        for k in sites:
            #every site has exactly one inbound connection
            prob+= lpSum([ x[(i,k)] for i in sites if (i,k) in x]) ==1
            #every site has exactly one outbound connection
            prob+=lpSum([ x[(k,i)] for i in sites if (k,i) in x]) ==1

        
        #subtour elimination
        N=len(sites)/K
        for i in sites:
                for j in sites:
                        if i != j and (i != 'org' and j!= 'org') and (i,j) in x:
                                prob += u[i] - u[j] <= (N)*(1-x[(i,j)]) - 1


        prob.solve()

        non_zero_edges = [ e for e in x if value(x[e]) != 0 ]
        tours = get_next_site('org', non_zero_edges)
        tours = [ [e] for e in tours ]

        for t in tours:
                while t[-1][1] !='org':
                        t.append(get_next_site(t[-1][1], non_zero_edges)[-1])
                
        for t in tours:
                print(' -> '.join([ a for a,b in t]+['org']))

        return(value(prob.objective))


def getMaximoDeSensores(listaSites, autonomia):
        sites = ['org']
                
        for site in listaSites:
            sites.append(site.getId())

        #make some positions (so we can plot this)
        positions = dict( (a.getId(), a.getNewPosicao() ) for a in listaSites )
        
        positions['org']=(453668.79, 5414190.73,0)

        #straight line distance for simplicity
        d = lambda p1,p2: np.sqrt( (p1[0]-p2[0])**2+ (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)

        #calculate all the pairs
        distances=dict( ((s1,s2), d(positions[s1],positions[s2])) for s1 in positions for s2 in positions if s1!=s2)

        #the number of sales people 
        K = 1 

        #create the problme
        prob=LpProblem("vehicle",LpMaximize)


        #indicator variable if site i is connected to site j in the tour
        x = LpVariable.dicts('x',distances, 0,1,LpBinary)
        #dummy vars to eliminate subtours
        u = LpVariable.dicts('u', sites, 0, len(sites)-1, LpInteger)


        #the objective
        cost = (lpSum([x[(i,j)] for (i,j) in x]))
        prob+=cost      

        for k in sites:
                prob+= lpSum([ x[(i,k)] for i in sites if (i,k) in x]) == lpSum([ x[(k,i)] for i in sites if (k,i) in x])
        
        for k in sites:
                prob+= lpSum([ x[('org',k)] for k in sites if ('org',k) in x]) == 1
        
        for k in sites:
                prob+= lpSum([ x[(k,'org')] for k in sites if (k, 'org') in x]) == 1

        prob+= lpSum([  x[(i,j)]  * distances[(i,j)]for (i,j) in distances ]) <= autonomia

        
        #subtour elimination
        N=len(sites)/K
        for i in sites:
                for j in sites:
                        if i != j and (i != 'org' and j!= 'org') and (i,j) in x:
                                prob += u[i] - u[j] <= (N)*(1-x[(i,j)]) - 1

        prob.solve()                
        
        distanciaTotal = 0
        for i in sites:
            for j in sites:
                if i != j :
                    distanciaTotal += value(x[(i,j)])  * distances[(i,j)]
        
        totalSensores = -1
        for i in sites:
            for j in sites:
                if i != j:
                    totalSensores += value(x[(i,j)])

        maxSensores = value(prob.objective)
        global minimoEnergia
        minimoEnergia = getMinimoEnergiaComMaxSensores(maxSensores, distances, listaSites)
            
        return('O maximo de sensores é: ' + str(maxSensores-1) +' <br> O custo inicial para realização do voo seria: '+ str(distanciaTotal)+' <br> O mínimo de custo alcançado é: '+str(minimoEnergia))
    
    
def getMinimoEnergiaComMaxSensores(maxSensores, distances, listaSites):

        sites = ['org']
                
        for site in listaSites:
            sites.append(site.getId())
         
        #create the problme
        prob=LpProblem("vehicle",LpMinimize)
        #indicator variable if site i is connected to site j in the tour
        x = LpVariable.dicts('x',distances, 0,1,LpBinary)
        #dummy vars to eliminate subtours
        u = LpVariable.dicts('u', sites, 0, len(sites)-1, LpInteger)
        #the objective
        cost =  ( lpSum([  x[(i,j)]  * distances[(i,j)]for (i,j) in distances ])) 
        prob+=cost

        for k in sites:
                prob+= lpSum([ x[(i,k)] for i in sites if (i,k) in x]) == lpSum([ x[(k,i)] for i in sites if (k,i) in x])
        
        for k in sites:
                prob+= lpSum([ x[('org',k)] for k in sites if ('org',k) in x]) == 1
        
        for k in sites:
                prob+= lpSum([ x[(k,'org')] for k in sites if (k, 'org') in x]) == 1
        
        prob+= lpSum([x[(i,j)] for (i,j) in x]) == maxSensores
        
        #subtour elimination
        N=len(sites)/1
        for i in sites:
                for j in sites:
                        if i != j and (i != 'org' and j!= 'org') and (i,j) in x:
                                prob += u[i] - u[j] <= (N)*(1-x[(i,j)]) - 1

        prob.solve()

        non_zero_edges = [ e for e in x if value(x[e]) != 0 ]
        tours = get_next_site('org', non_zero_edges)
        tours = [ [e] for e in tours ]

        for t in tours:
                while t[-1][1] !='org':
                        t.append(get_next_site(t[-1][1], non_zero_edges)[-1])

        for t in tours:
                print(' -> '.join([ a for a,b in t]+['org']))


        generate_file_flight_plan(tours, listaSites)
        
        return value(prob.objective)