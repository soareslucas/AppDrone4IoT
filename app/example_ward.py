# Usual imports

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display
from sklearn import datasets


#Z =  np.zeros(50); 
#Xyz[:, 2] = Z

from sklearn.cluster import AgglomerativeClustering
import numpy as np

X = np.random.randint(1000, size=(50, 2))
clustering = AgglomerativeClustering(affinity='euclidean', compute_full_tree='auto', connectivity=None, distance_threshold=350, linkage='ward', memory=None, n_clusters=None, pooling_func='deprecated')

clustering.fit(X)


print(clustering.labels_);

# MinMax scale the data so that it fits nicely onto the 0.0->1.0 axes of the plot.
# from sklearn import preprocessing
# X_plot = preprocessing.MinMaxScaler().fit_transform(X)

#for i in range(X.shape[0]):
#    plt.text(X_plot[i, 0], X_plot[i, 1], str(clustering.labels_[i]),
#             fontdict={'weight': 'bold', 'size': 9}
#        )



#enters = np.zeros((self.number_of_clusters, 3))
#for i in range(0, self.number_of_clusters):
#    cluster_points = image_cols[ward.labels_ == i]
#    cluster_mean = np.mean(cluster_points, axis=0)
#    centers[i, :] = cluster_mean

# plt.show()






from sklearn.cluster import AgglomerativeClustering
import numpy as np
X = np.array([[1, 2], [1, 4], [1, 0],[4, 2], [4, 4], [4, 0]])
clustering = AgglomerativeClustering(affinity='euclidean', compute_full_tree='auto', connectivity=None, distance_threshold=3, linkage='ward', memory=None, n_clusters=None, pooling_func='deprecated')

clustering.fit(X)

#clustering.labels_
#array([1, 1, 1, 0, 0, 0])