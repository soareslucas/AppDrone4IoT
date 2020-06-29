import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display
from sklearn import datasets
from mpl_toolkits.mplot3d import axes3d, Axes3D
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans


Xyz = np.random.randint(1000, size=(50, 3))
Z =  np.zeros(50); 
Xyz[:, 2] = Z

fig = plt.figure()
ax = Axes3D(fig)
ax.scatter(Xyz[ : , 0], Xyz[ :, 1], Xyz[ :, 2], s = 50, c = "b")

print(Xyz); 

clustering = AgglomerativeClustering(affinity='euclidean', compute_full_tree='auto', connectivity=None, distance_threshold=569, linkage='ward', memory=None, n_clusters=None)

clustering.fit(Xyz)

labels = clustering.labels_

amountClusters = 0

for i in range(len(labels)):
    if(amountClusters < labels[i]): 
        amountClusters = labels[i] + 1

print(clustering.labels_);
print(amountClusters)

Kmean = KMeans(n_clusters=amountClusters)
Kmean.fit(Xyz)
centroids = Kmean.cluster_centers_

print(centroids)


ax.scatter(Xyz[ : , 0], Xyz[ : , 1],  Xyz[ :, 2], s =50, c="b")

for i in range(len(centroids)):
    ax.scatter(centroids[i][0], centroids[i][1], 30, s=200, c="r", marker="s")


plt.show()











