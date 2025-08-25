import numpy as np
from math import radians, cos, sin, asin, sqrt
from sklearn.cluster import KMeans

def haversine(lat1, lon1, lat2, lon2):
    # returns kilometers
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return 6371 * c

def distance_matrix(coords):
    n = len(coords)
    mat = np.zeros((n,n))
    for i in range(n):
        for j in range(n):
            if i==j: continue
            mat[i,j] = haversine(coords[i][0], coords[i][1], coords[j][0], coords[j][1])
    return mat

def cluster_coords(coords, k):
    if k <= 0 or k >= len(coords):
        return {0: list(range(len(coords)))}
    X = np.array(coords)
    kmeans = KMeans(n_clusters=k, random_state=0).fit(X)
    labels = kmeans.labels_
    clusters = {}
    for i,l in enumerate(labels):
        clusters.setdefault(int(l), []).append(i)
    return clusters
