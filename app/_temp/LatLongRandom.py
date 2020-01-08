import random
import sys
import math

latitude = 48.87
longitude = 02.36

def generate_random_data(lat, lon, num_rows):
    for _ in range(num_rows):
        dec_lat = random.random()/100
        dec_lon = random.random()/100
        print ('%.6f %.6f \n' % (lat+dec_lat, lon+dec_lon) )

generate_random_data(latitude, longitude, 5)