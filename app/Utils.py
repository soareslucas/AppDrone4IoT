import random
import sys
import math
import os
import numpy as np
import Site as Site
rnd = np.random


def get_line_flight_plan(sites, id):
        for s in sites:
                if(int(s.getId()) == id ): 
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

def generate_file_flight_plan(tours, listaSites, file_name):
        text = ('GC WPL 120\n')
        
        tourFlightPlan = ''

        _temp = tours[:(len(tours) - 1)]
        for t in _temp:
                tourFlightPlan += str(get_line_flight_plan(listaSites, t)) 

        
        last = listaSites[0]
        coordinates = last.getPosicao()
        lat = str(coordinates[0])
        lon = str(coordinates[1])
        height = str(coordinates[2])
        digits = len(height)
        
        if (digits == 1):
                height = '00'+height
        if (digits == 2):
                height = '0'+height

        tourFlightPlan += ('1       0       3       21      0.000000        '
        + '0.000000        0.000000        0.000000        ' + lat[:9] 
        +'       ' + lon[:8] +'        '+height+'.000000      1breakline')

        tourFlightPlan = tourFlightPlan.replace(']', '')
        tourFlightPlan = tourFlightPlan.replace('[', '')
        tourFlightPlan = tourFlightPlan.replace(',', '')
        tourFlightPlan = tourFlightPlan.replace("'", '')

        tourFlightPlan = tourFlightPlan.split('breakline')
        del tourFlightPlan[-1]

        index = 0
        for fp in tourFlightPlan:
                fpTemp = ''
                f = list(fp)
                if (str(f[0]) == ' '):
                        fpTemp = fp.replace(' ' , '', 1) 
                else:
                        fpTemp = fp

                fpTemp = fpTemp.replace('1' , str(index), 1) 
                index += 1
                text += str(fpTemp) + '\n'

        file = open(file_name+".mavlink", "w") 
        file.write(text) 
        file.close()


def generate_random_data(lat, lon, num_rows,idSite, idSensor):
    sitesTemp = []
    for _ in range(num_rows):
        dec_lat = random.random()/100
        dec_lon = random.random()/100
        site = Site.Site(str(idSite), (lat+dec_lat, lon+dec_lon, np.random.randint(1,2)) , False, idSensor, False, rnd.randint(512, 1024))
        idSite += 1
        sitesTemp.append(site)
    return sitesTemp


def generate_random_data_cartesian(num_rows,idSite, idSensor):
    sitesTemp = []
    for _ in range(num_rows):
        site = Site.Site(str(idSite), (rnd.randint(0, 2000), rnd.randint(0, 2000), rnd.randint(30, 50)) , False, idSensor, False, rnd.randint(512, 1024))
        idSite += 1
        sitesTemp.append(site)
    return sitesTemp

def generate_file_data():
        global textFile
        file = open("flightplan.txt", "w") 
        file.write(textFile) 
        return file