import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from mpl_toolkits.mplot3d import axes3d, Axes3D

Xyz =  np.random.randint(5, size=(50, 3))

#X1 = 1 + 2 * np.random.rand(50,2)
#X[50:100, :] = X1

for i in range(0, 50):
    centers[i, ] = cluster_mean
    
Xy[:, :, 1:50] = Z

fig = plt.figure()
ax = Axes3D(fig)

ax.scatter(Xy[ : , 0], Xy[ :, 1], Z[ :, :], s = 50, c = "b")


#plt.show()

from sklearn.cluster import KMeans

Kmean = KMeans(n_clusters=3)
Kmean.fit(Xy)
centroids = Kmean.cluster_centers_
ax.scatter(Xy[ : , 0], Xy[ : , 1],  Z[ :, :], s =50, c="b")
ax.scatter(centroids[0][0], centroids[0][1], [30], s=200, c="g", marker="s")
ax.scatter(centroids[1][0], centroids[1][1], [30], s=200, c="r", marker="s")
ax.scatter(centroids[2][0], centroids[2][1], [30], s=200, c="y", marker="s")

plt.show()