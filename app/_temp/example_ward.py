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

import matplotlib.pyplot as plt

from scipy.cluster.hierarchy import fclusterdata
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import FeatureAgglomeration
from sklearn.cluster import Birch 
from sklearn.cluster import KMeans
from sklearn import metrics


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



""" Xyz = np.random.randint(500, size=(20, 3))
Z =  np.zeros(20); 
Xyz[:, 2] = Z """


#print(Xyz); 
pointsTemp = [[170, 136,   0], [416,  64,   0],    [240, 453,   0],    [ 77, 119,   0],    [ 30, 390,   0],    [312, 337,   0],    [374, 165,   0],    [ 90,  98,   0],    [294, 295,   0],    [256, 298 ,  0],    [ 15, 477,   0],    [131, 428,   0],    [301, 392,   0],    [435, 475,   0],    [ 80, 202,   0],    [499, 326,   0],    [325,  78,   0]]

Xyz = np.array(list(pointsTemp))

threshold = 120
clustering = AgglomerativeClustering(affinity='euclidean',  distance_threshold=threshold, linkage='complete', n_clusters=None)

#clustering = Birch( threshold=100, branching_factor=50, n_clusters=None, compute_labels=True, copy=True)
#amountClusters = len(clustering.subcluster_centers_)

clustering.fit(Xyz)

labels = clustering.labels_

print(labels)

amountClusters = 0
for i in range(len(labels)):
    if(amountClusters < labels[i]): 
        amountClusters = labels[i]

amountClusters +=1
#print(labels)
print(amountClusters)

#Kmean = KMeans(n_clusters=amountClusters)
#Kmean.fit(Xyz)
#y_kmeans = Kmean.fit_predict(Xyz)
#centroids = Kmean.cluster_centers_
#print(centroids)


#-----------------CREATING DICT WITH CLUSTERS AND THEIR POINTS-------------
arrayLabels =   { i : {} for i in range(amountClusters)}
for i in range(amountClusters):
    temp =   { ( (Xyz[ j , 0], Xyz[ j , 1], Xyz[ j , 2]) ) for j in range(len(Xyz)) if  (i == labels[j])   }
    arrayLabels[i] = temp


#my_dict =   { Kmean.cluster_centers_[i, 0] : np.where(Kmean.labels_ == i)[0] for i in range(Kmean.n_clusters)}

#---------------- CENTROIDS--------------------------------------------------
centroids = np.random.randint(1, size=(amountClusters, 3))
for i in range(amountClusters):

    _temp = arrayLabels[i].copy()
    arrayTemp = np.array(list(_temp))

    x = arrayTemp[:, 0]
    y = arrayTemp[:, 1]
    z = arrayTemp[:, 2]
    centroid = [statistics.mean(x), statistics.mean(y), 0]
    centroids[i] = np.array(centroid)

#---------------- MAX DISTANCE BETWEEN POINTS OF A CLUSTER AND ITS CENTROID-----
maxDistanceFromCentroid =  np.zeros(amountClusters)
for i in range(len(centroids)):
    pointsOfCluster = arrayLabels[i]
    #print(pointsOfCluster)
    for j in range(len(pointsOfCluster)):

        __temp = pointsOfCluster.copy()
        _arrayTemp = np.array(list(__temp))

        d = np.sqrt( (centroids[i][0]-_arrayTemp[ j , 0])**2+ (centroids[i][1]- _arrayTemp[ j , 1])**2 + (centroids[i][2]-_arrayTemp[ j, 2])**2)
        if ( d > maxDistanceFromCentroid[i]):
            maxDistanceFromCentroid[i] = d

print(maxDistanceFromCentroid)



#centroids = clustering.subcluster_centers_

#---------------- PLOTTING-------------------------------

fig = plt.figure()
ax = Axes3D(fig)
ax.scatter(Xyz[ : , 0], Xyz[ :, 1], Xyz[ :, 2], s = 50, c = "b")


for j in range(len(Xyz)):
    text = str(labels[j]) 
    _annotate3D(ax ,text, (Xyz[ j , 0], Xyz[ j , 1], Xyz[ j , 2]), xytext=(3,3),textcoords='offset points')

for i in range(amountClusters):
    ax.scatter(centroids[i][0], centroids[i][1],centroids[i][2], s=50, c="r", marker="s")

for i in range(amountClusters):
    text = str(i) 
    _annotate3D(ax ,text, (centroids[i][0], centroids[i][1], centroids[i][2]), xytext=(3,3),textcoords='offset points')






 



plt.show()











