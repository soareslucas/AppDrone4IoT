

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
        text = ('GC WPL 110\n'
        + '0       1       0       0       0       0       0       0       0       0       0       1\n')
        
        tourFlightPlan = ''
        for t in tours:
                tourFlightPlan += str(get_line_flight_plan(listaSites, t)) 

        tourFlightPlan = tourFlightPlan.replace(']', '')
        tourFlightPlan = tourFlightPlan.replace('[', '')
        tourFlightPlan = tourFlightPlan.replace(',', '')
        tourFlightPlan = tourFlightPlan.replace("'", '')

        tourFlightPlan = tourFlightPlan.split('breakline')
        del tourFlightPlan[-1]

        index = 1
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