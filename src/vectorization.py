import numpy as np  # https://numpy.org/doc/2.2/
import matplotlib.pyplot as plt  # https://matplotlib.org/3.10.7/api/pyplot_summary.html
from sklearn.cluster import KMeans  # https://scikit-learn.org/1.7/modules/generated/sklearn.cluster.KMeans.html
from sklearn.preprocessing import normalize  # https://scikit-learn.org/1.7/modules/generated/sklearn.preprocessing.normalize.html
from sklearn.decomposition import TruncatedSVD  # https://scikit-learn.org/1.7/modules/generated/sklearn.decomposition.TruncatedSVD.html
from sklearn.pipeline import make_pipeline  # https://scikit-learn.org/1.7/modules/generated/sklearn.pipeline.make_pipeline.html
import logging

# Suppress matplotlib debug messages
logging.getLogger('matplotlib').setLevel(logging.WARNING)

def vectorize_terms(MY_COLLECTION_inverted_index: dict) -> np.ndarray:
    """
    Converts inverted index to L2-normalized document-term matrix.
    
    Args:
        MY_COLLECTION_inverted_index: {'term': {'doc_id': tfidf_weight}}
    
    Returns:
        L2-normalized array (num_docs x num_terms)
    """
    terms = MY_COLLECTION_inverted_index.keys()
    documents_with_weights = list(MY_COLLECTION_inverted_index.values())
    
    # Extract unique document IDs
    document_ids = set()
    for postings in documents_with_weights:
        document_ids.update(postings.keys())
    
    doc_id_rows = sorted(list(document_ids))
    term_columns = list(terms)

    # Initialize weight matrix
    weight_matrix = np.zeros((len(doc_id_rows), len(term_columns)))
    
    # Populate matrix iterate by term since in a hashmap
    for col, term in enumerate(term_columns):
        for row, doc_id in enumerate(doc_id_rows):
            weight = MY_COLLECTION_inverted_index[term].get(doc_id, 0)
            weight_matrix[row][col] = weight

    # normalize the weight matrix
    weight_matrix = normalize(weight_matrix, norm='l2')
    print(weight_matrix)
    # print(weight_matrix.shape)    
    return weight_matrix

def visualize_clusters(weight_matrix: np.ndarray, MY_COLLECTION: dict, num_clusters: int, cmap: str):
    """
    Performs K-Means clustering and visualizes in 2D using LSA.
    
    Args:
        weight_matrix: Document-term matrix (num_docs x num_terms)
        MY_COLLECTION: Inverted index for term names
        num_clusters: Number of clusters (k)
        cmap: Matplotlib colormap name
    
    Outputs:
        - Scatter plot (documents colored by cluster)
        - Text file with top 50 terms per cluster
    """
    # K-Means clustering
    kmeans = KMeans(init="k-means++", n_clusters=num_clusters, n_init=10, random_state=42)
    #  cluster assignment for each document
    labels = kmeans.fit_predict(weight_matrix)
    
    # Reduce to 2D for visualization and put documents on 2D space
    lsa = TruncatedSVD(n_components=2, random_state=42)
    weight_matrix_lsa = lsa.fit_transform(weight_matrix)
    cluster_centers_lsa = lsa.transform(kmeans.cluster_centers_)
    
    # Create scatter plot
    plt.figure(figsize=(10, 6))
    
#  2d scatter plot 
    scatter = plt.scatter(weight_matrix_lsa[:, 0], weight_matrix_lsa[:, 1], 
                         c=labels, cmap=cmap, s=50)
    
    plt.scatter(cluster_centers_lsa[:, 0], cluster_centers_lsa[:, 1], 
               s=180, c='black', marker='X',  label='Centroids')
    
    cbar = plt.colorbar(scatter)
    cbar.set_label('Cluster ID', rotation=270, labelpad=15)
    


    #sort indices of cluster centers in descending order 
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    terms = list(MY_COLLECTION.keys())

    # Write results to file
    with open(f'Cluster_Results/clustering_results_k{num_clusters}.txt', 'w') as file:
        file.write(f'K-Means Clustering Results (K={num_clusters})\n')
        file.write(f'Top 50 terms ranked by TF-IDF weight in cluster\n')
        file.write('=' * 200 + '\n\n')
        
        for cluster_id in range(num_clusters):
            file.write(f'Cluster {cluster_id + 1 }:\n')
            file.write('-' * 200 + '\n')
            
            # Get the top terms per cluster
            # go through the top indices for the current cluster
            for term_number, index in enumerate(order_centroids[cluster_id, :50], start=1):
                term_name = terms[index]
                tfidf_weight = kmeans.cluster_centers_[cluster_id][index]
                file.write(f' {term_number}.  {term_name}. TF-IDF: {tfidf_weight:.8f}\n')
            
            
    
    plt.title(f'K-Means Clustering of Documents (K={num_clusters})', fontsize=14, fontweight='bold')    
    plt.show()