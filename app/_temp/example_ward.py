import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display
from sklearn import datasets
from mpl_toolkits.mplot3d import axes3d, Axes3D
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans
from sklearn import metrics


Xyz = np.random.randint(1000, size=(50, 3))
Z =  np.zeros(50); 
Xyz[:, 2] = Z

fig = plt.figure()
ax = Axes3D(fig)
ax.scatter(Xyz[ : , 0], Xyz[ :, 1], Xyz[ :, 2], s = 50, c = "b")

print(Xyz); 

clustering = AgglomerativeClustering(affinity='euclidean', compute_full_tree='auto', connectivity=None, distance_threshold=50, linkage='complete', memory=None, n_clusters=None)

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

y_kmeans = Kmean.fit_predict(Xyz)

centroids = Kmean.cluster_centers_

print(centroids)



ax.scatter(Xyz[ : , 0], Xyz[ : , 1],  Xyz[ :, 2], s =50, c="b")


for i in range(len(centroids)):
    ax.scatter(centroids[i][0], centroids[i][1], 30, s=200, c="r", marker="s")


xy = np.random.randint(1000, size=(50, 2))

xy[:,0] = Xyz[ : , 0]
xy[:,1] = Xyz[ : , 1] 



for ind,i in enumerate(centroids):
    class_inds=np.where(Kmean.labels_==ind)

    max_dist=np.max(metrics.pairwise_distances(i, xy[class_inds]))

    print('teste')
    print(max_dist)
    plt.gca().add_artist(plt.Circle(i, max_dist, fill=False))
 



plt.show()











