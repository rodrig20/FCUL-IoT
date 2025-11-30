import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import pandas as pd


def perform_clustering(data):
    """
    Performs K-Means clustering on the given data, finding the optimal number of clusters.
    Returns the cluster centroids and the labeled data points.

    Args:
        data (list of dict): A list of dictionaries, where each dictionary represents a data point.

    Returns:
        dict: A dictionary containing:
              - 'centroids': A list of cluster centroids.
              - 'labeled_data': The original data with an added 'cluster' key for each point.
    """
    if not data or len(data) < 2:
        return {"centroids": [], "labeled_data": []}

    feature_names = list(data[0].keys())
    if len(feature_names) != 2:
        raise ValueError("Data should have exactly two features for 2D clustering.")

    df = pd.DataFrame(data)
    df.dropna(subset=feature_names, inplace=True)

    if df.empty:
        return {"centroids": [], "labeled_data": []}
        
    X = df[feature_names].values

    best_k = -1
    best_score = -1

    max_clusters = min(11, len(X))

    if max_clusters <= 2:
        best_k = 1
    else:
        for k in range(2, max_clusters):
            kmeans = KMeans(n_clusters=k, random_state=0, n_init=10)
            kmeans.fit(X)
            score = silhouette_score(X, kmeans.labels_)
            if score > best_score:
                best_score = score
                best_k = k

    if best_k == -1:
        best_k = 3

    # Rerun with the best k
    kmeans = KMeans(n_clusters=best_k, random_state=0, n_init=10)
    kmeans.fit(X)

    centroids = kmeans.cluster_centers_.tolist()
    labels = kmeans.labels_.tolist()

    # Add cluster label to each data point
    labeled_data = df.to_dict("records")
    for i, point in enumerate(labeled_data):
        point["cluster"] = labels[i]

    return {"centroids": centroids, "labeled_data": labeled_data}
