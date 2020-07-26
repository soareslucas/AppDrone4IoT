import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display
from sklearn import datasets
from mpl_toolkits.mplot3d import axes3d, Axes3D
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import proj3d
from mpl_toolkits.mplot3d.proj3d import proj_transform
from matplotlib.text import Annotation
from matplotlib.patches import FancyArrowPatch
import statistics 
import plotly.graph_objects as go
import matplotlib.pyplot as plt

from scipy.cluster.hierarchy import fclusterdata, median, maxdists
from scipy.spatial.distance import pdist

from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import FeatureAgglomeration
from sklearn.cluster import Birch 
from sklearn.cluster import KMeans
from sklearn import metrics


from mpl_toolkits.mplot3d import Axes3D
from scipy.linalg import norm
import pylab as plt

class Annotation3D(Annotation):
    def __init__(self, text, xyz, *args, **kwargs):
        super().__init__(text, xy=(0,0), *args, **kwargs)
        self._xyz = xyz

    def draw(self, renderer):
        x2, y2, z2 = proj_transform(*self._xyz, renderer.M)
        self.xy=(x2,y2)
        super().draw(renderer)


def _annotate3D(ax,text, xyz, *args, **kwargs):
    annotation= Annotation3D(text, xyz, *args, **kwargs)
    ax.add_artist(annotation)


def truncated_cone(p0, p1, R0, R1, color):
    """
    Based on https://stackoverflow.com/a/39823124/190597 (astrokeat)
    """
    # vector in direction of axis
    v = p1 - p0
    # find magnitude of vector
    mag = norm(v)
    # unit vector in direction of axis
    v = v / mag
    # make some vector not in the same direction as v
    not_v = np.array([1, 1, 0])
    if (v == not_v).all():
        not_v = np.array([0, 1, 0])
    # make vector perpendicular to v
    n1 = np.cross(v, not_v)
    # print n1,'\t',norm(n1)
    # normalize n1
    n1 /= norm(n1)
    # make unit vector perpendicular to v and n1
    n2 = np.cross(v, n1)
    # surface ranges over t from 0 to length of axis and 0 to 2*pi
    n = 80
    t = np.linspace(0, mag, n)
    theta = np.linspace(0, 2 * np.pi, n)
    # use meshgrid to make 2d arrays
    t, theta = np.meshgrid(t, theta)
    R = np.linspace(R0, R1, n)
    # generate coordinates for surface
    X, Y, Z = [p0[i] + v[i] * t + R *
               np.sin(theta) * n1[i] + R * np.cos(theta) * n2[i] for i in [0, 1, 2]]
    ax.plot_surface(X, Y, Z, color=color, linewidth=0, antialiased=False)





Xyz = np.random.randint(500, size=(50, 3))
Z =  np.zeros(50); 
Xyz[:, 2] = Z 

#pointsTemp = [[170, 136,   0], [416,  64,   0],    [240, 453,   0],    [ 77, 119,   0],    [ 30, 390,   0],    [312, 337,   0],    [374, 165,   0],    [ 90,  98,   0],    [294, 295,   0],    [256, 298 ,  0],    [ 15, 477,   0],    [131, 428,   0],    [301, 392,   0],    [435, 475,   0],    [ 80, 202,   0],    [499, 326,   0],    [325,  78,   0],  [ 25, 100,   0],    [89, 200,   0],    [76,  325,   0]]
#Xyz = np.array(list(pointsTemp))

threshold = 120
labels = fclusterdata(Xyz, t=threshold, criterion='distance', metric='euclidean', method='complete')
#print(labels)


amountClusters = 0
for i in range(len(labels)):
    if(amountClusters < labels[i]): 
        amountClusters = labels[i]

print(amountClusters)

#-----------------CREATING DICT WITH CLUSTERS AND THEIR POINTS-------------
arrayLabels =   { i : {} for i in range(1,amountClusters+1)}
for i in range(amountClusters+1):
    temp =   { ( (Xyz[ j , 0], Xyz[ j , 1], Xyz[ j , 2]) ) for j in range(len(Xyz)) if  (i == labels[j])   }
    arrayLabels[i] = temp

#print(arrayLabels)

#---------------- CENTROIDS--------------------------------------------------
centroids = np.random.randint(1, size=(amountClusters+1, 3))
for i in range(1,amountClusters+1):

    _temp = arrayLabels[i].copy()
    arrayTemp = np.array(list(_temp))

    x = arrayTemp[:, 0]
    y = arrayTemp[:, 1]
    z = arrayTemp[:, 2]
    centroid = [statistics.mean(x), statistics.mean(y), 0]
    centroids[i] = np.array(centroid)
#print(centroids)

#---------------- MAX DISTANCE BETWEEN POINTS OF A CLUSTER AND ITS CENTROID-----
maxDistanceFromCentroid =  np.zeros(amountClusters+1)
for i in range(1,len(centroids)):
    pointsOfCluster = arrayLabels[i]
    _arrayTemp = np.array(list(pointsOfCluster))

    print('------------------------'+ str(i))
    for j in range(len(pointsOfCluster)):


        d = np.sqrt( (centroids[i][0]-_arrayTemp[ j , 0])**2+ (centroids[i][1]- _arrayTemp[ j , 1])**2 + (centroids[i][2]-_arrayTemp[ j, 2])**2)

        print(d)

        if ( d > maxDistanceFromCentroid[i]):
            maxDistanceFromCentroid[i] = d

        #Z = median(pdist(_arrayTemp))
        # print(maxdists(Z))

print(maxDistanceFromCentroid)

#---------------- DIAMETER----------------------------------------------- 
diameter =  np.zeros(amountClusters+1)
newCentroids = np.random.randint(1, size=(amountClusters+1, 3))

for i in range(1,len(centroids)):
    pointsOfCluster = arrayLabels[i]
    _arrayTemp = np.array(list(pointsOfCluster))

    for j in range(len(pointsOfCluster)):
        for k in range(len(pointsOfCluster)):
            d = np.sqrt( (_arrayTemp[k][0]-_arrayTemp[ j , 0])**2+ (_arrayTemp[k][1]- _arrayTemp[ j , 1])**2 + (_arrayTemp[k][2]-_arrayTemp[ j, 2])**2)
            if ( d > diameter[i]):
                newCentroids[i] = np.array(list( [ ((_arrayTemp[k][0]+_arrayTemp[ j , 0])/2) ,((_arrayTemp[k][1]+_arrayTemp[ j , 1])/2) ,((_arrayTemp[k][2]+_arrayTemp[ j , 2])/2) ] ))
                diameter[i] = d
                raio = d/2
                
                if(d != 0):
                    h = np.sqrt( (60**2)-(raio**2) )
                else:
                    h = 60
                
                centroid = [centroids[i][0] ,centroids[i][1], h]
                centroids[i] = np.array(centroid)



            point = np.array(list( [ ((_arrayTemp[k][0]) ,(_arrayTemp[k][1]) ,(_arrayTemp[k][2] )) ] ))

    if ( diameter[i] == 0):
        newCentroids[i] = point


print(diameter)

print(newCentroids)


#---------------- MAX DISTANCE BETWEEN POINTS OF A CLUSTER AND ITS CENTROID-----
maxDistance =  np.zeros(amountClusters+1)
for i in range(1,len(newCentroids)):
    pointsOfCluster = arrayLabels[i]
    __temp = pointsOfCluster.copy()
    _arrayTemp = np.array(list(__temp))

    for j in range(len(pointsOfCluster)):

        d = np.sqrt( (newCentroids[i][0]-_arrayTemp[ j , 0])**2+ (newCentroids[i][1]- _arrayTemp[ j , 1])**2 + (newCentroids[i][2]-_arrayTemp[ j, 2])**2)
        if ( d > maxDistance[i]):
            maxDistance[i] = d
        
print(maxDistance)




#---------------- PLOTTING-------------------------------

fig = plt.figure()
ax = Axes3D(fig)

ax.scatter(Xyz[ : , 0], Xyz[ :, 1], Xyz[ :, 2], s = 20, c = "b")

for j in range(len(Xyz)):
    text = str(labels[j]) 
    _annotate3D(ax ,text, (Xyz[ j , 0], Xyz[ j , 1], Xyz[ j , 2]), xytext=(3,3),textcoords='offset points')

for i in range(1,amountClusters+1):
    ax.scatter(centroids[i][0], centroids[i][1],centroids[i][2], s=10, c="r", marker="s")



for i in range(1,amountClusters+1):
    text = str(i) 
    _annotate3D(ax ,text, (centroids[i][0], centroids[i][1], centroids[i][2]), xytext=(3,3),textcoords='offset points')


""" 

A0 = np.array([1, 3, 2])
A1 = np.array([8, 5, 9])

truncated_cone(A0, A1, 100, 300, 'blue')
 """


plt.show()











