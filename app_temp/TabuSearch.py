import copy
import math
import numpy as np



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


def generate_neighbours(points):
    """This function geenrates a 2D distance matrix between all points
    Parameters
    ----------
    points : type
        Description of parameter `points`.
    Returns
    -------
    type
        Description of returned object.
    """
    dict_of_neighbours = {}

    for i in points:
        dict_of_neighbours[int(i.getId())] = {}
        for j in points:
            if i!=j:
                    dict_of_neighbours[int(i.getId())][int(j.getId())]= calculate_energy_cost(i.getNewPosicao(), j.getNewPosicao())

    return dict_of_neighbours

def generate_first_solution( dict_of_neighbours):

    start_node = 0
    end_node = start_node

    first_solution = []
    distance = 0
    visiting = start_node
    pre_node = None


    _tmp = copy.deepcopy(dict_of_neighbours[visiting])

    while not len(_tmp) == 0:
        next_node = min(_tmp.items(), key=lambda x: x[1])[0]
        distance += dict_of_neighbours[visiting][next_node]
        first_solution.append(visiting)
        pre_node = visiting
        visiting = next_node
        _tmp.pop(next_node, None)

    first_solution.append(visiting)
    pre_node = visiting
    first_solution.append(0)
    distance += dict_of_neighbours[pre_node][end_node]
    return first_solution, distance

def find_neighborhood(solution, dict_of_neighbours, n_opt=1):
    neighborhood_of_solution = []
    for n in solution[1:-n_opt]:

        idx1 = []
        n_index = solution.index(n)
        for i in range(n_opt):
            idx1.append(n_index+i)

        for kn in solution[1:-n_opt]:

            idx2 = []
            kn_index = solution.index(kn)
            for i in range(n_opt):
                idx2.append(kn_index+i)
            if bool(
                set(solution[idx1[0]:(idx1[-1]+1)]) &
                set(solution[idx2[0]:(idx2[-1]+1)])):
          
                continue

            _tmp = copy.deepcopy(solution)
            for i in range(n_opt):
                _tmp[idx1[i]] = solution[idx2[i]]
                _tmp[idx2[i]] = solution[idx1[i]]

            distance = 0
            for k in _tmp[:-1]:
                next_node = _tmp[_tmp.index(k) + 1]
                distance = distance + dict_of_neighbours[k][next_node]
                
            _tmp.append(distance)
            if _tmp not in neighborhood_of_solution:
                neighborhood_of_solution.append(_tmp)

    indexOfLastItemInTheList = len(neighborhood_of_solution[0]) - 1

    neighborhood_of_solution.sort(key=lambda x: x[indexOfLastItemInTheList])
    return neighborhood_of_solution


def tabu_search(first_solution, distance_of_first_solution, dict_of_neighbours, iters, size, n_opt=1):
    count = 1
    solution = first_solution
    tabu_list = list()
    best_cost = distance_of_first_solution
    best_solution_ever = solution
    while count <= iters:

        neighborhood = find_neighborhood(solution, dict_of_neighbours, n_opt=n_opt)
        index_of_best_solution = 0
        best_solution = neighborhood[index_of_best_solution]
        best_cost_index = len(best_solution) - 1
        found = False
        while found is False:
            i = 0
            first_exchange_node, second_exchange_node = [], []
            n_opt_counter = 0
            while i < len(best_solution):
                print (best_solution) 
                if best_solution[i] != solution[i]:
                    first_exchange_node.append(best_solution[i])
                    second_exchange_node.append(solution[i])
                    n_opt_counter += 1
                    if n_opt_counter == n_opt:
                        break
                i = i + 1

            exchange = first_exchange_node + second_exchange_node
            if first_exchange_node + second_exchange_node not in tabu_list and second_exchange_node + first_exchange_node not in tabu_list:
                tabu_list.append(exchange)
                found = True
                solution = best_solution[:-1]
                cost = neighborhood[index_of_best_solution][best_cost_index]
                if cost < best_cost:
                    best_cost = cost
                    best_solution_ever = solution
            elif index_of_best_solution < len(neighborhood):
                best_solution = neighborhood[index_of_best_solution]
                index_of_best_solution = index_of_best_solution + 1

        while len(tabu_list) > size:
            tabu_list.pop(0)

        count = count + 1
    best_solution_ever.pop(-1)
    return best_solution_ever, best_cost