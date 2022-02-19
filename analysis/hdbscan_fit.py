import pandas as pd
import numpy as np


from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans, DBSCAN, OPTICS
from sklearn.metrics import  silhouette_score
from sklearn import datasets
from scipy.cluster.hierarchy import dendrogram, linkage
from yellowbrick.cluster import SilhouetteVisualizer, KElbowVisualizer

from hdbscan import HDBSCAN
from joblib import Memory, dump

df3 = pd.read_csv('../data/data_final.csv', index_col=0)

scaler = MinMaxScaler()
scaled = scaler.fit_transform(df3)

mem = Memory(location='./cache')

hd = HDBSCAN(min_cluster_size=3, min_samples=100, memory=mem)

hd.fit(scaled)

filename = 'hdbscan_model.sav'
dump(hd, filename)