import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from mpl_toolkits.mplot3d import axes3d, Axes3D

Xyz =  np.random.randint(1000, size=(50, 3))
Z =  np.zeros(50); 
Xyz[:, 2] = Z

fig = plt.figure()
ax = Axes3D(fig)

print(Xyz); 

ax.scatter(Xyz[ : , 0], Xyz[ :, 1], Xyz[ :, 2], s = 50, c = "b")

plt.show()

fig = plt.figure()
ax = Axes3D(fig)

from sklearn.cluster import KMeans

n_clusters = 10
Kmean = KMeans(n_clusters)
Kmean.fit(Xyz)
centroids = Kmean.cluster_centers_
ax.scatter(Xyz[ : , 0], Xyz[ : , 1],  Xyz[ :, 2], s =50, c="b")
ax.scatter(centroids[0][0], centroids[0][1], 30, s=200, c="g", marker="s")
ax.scatter(centroids[1][0], centroids[1][1], 30, s=200, c="r", marker="s")
ax.scatter(centroids[2][0], centroids[2][1], 30, s=200, c="y", marker="s")

plt.show()