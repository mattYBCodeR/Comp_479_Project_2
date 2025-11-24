import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
from sklearn.decomposition import PCA
import logging

# Suppress matplotlib debug messages
logging.getLogger('matplotlib').setLevel(logging.WARNING)

def vectorize_terms(MY_COLLECTION_inverted_index: dict) -> np.ndarray:
    '''
    Constructs a normalized document-term weight matrix from an inverted index.
    
    Args:
        MY_COLLECTION_inverted_index (dict): Inverted index structure where:
            - Keys are terms (str)
            - Values are dictionaries {doc_id: tf-idf_weight}
    
    Returns:
        np.ndarray: L2-normalized weight matrix with shape (num_docs, num_terms)
            - Rows represent documents (sorted by doc_id)
            - Columns represent terms (in order of inverted index keys)
            - Each cell contains the tf-idf weight for that term in that document
    
    Process:
        1. Extracts all unique document IDs from the inverted index
        2. Creates a zero matrix with dimensions (num_docs × num_terms)
        3. Populates matrix by iterating through terms (efficient lookup)
        4. Applies L2 normalization to each document vector
    '''
    terms = MY_COLLECTION_inverted_index.keys()
    documents_with_weights = list(MY_COLLECTION_inverted_index.values())
        

    #  need doc ids to be the rows 

    document_ids =  set()
    for postings in documents_with_weights:
        document_ids.update(postings.keys())
            
    doc_id_rows = sorted(list(document_ids))
    term_columns = list(terms)

    # Initialize weight matrix with zeros
    weight_matrix = np.zeros((len(doc_id_rows), len(term_columns)))
        
    

    # Iterate by column (term) first because the inverted index is keyed by term.
    # This allows direct lookup: MY_COLLECTION_inverted_index[term].get(doc_id, 0)
    # Row-first iteration would require inefficiently searching through all terms per document.

    # CORRECT
    for col, term in enumerate(term_columns):
        for row, doc_id in enumerate(doc_id_rows):
            weight = MY_COLLECTION_inverted_index[term].get(doc_id, 0)
            weight_matrix[row][col] = weight

    # for row, doc_id in enumerate(doc_id_rows):
    #     for col, term in enumerate(term_columns):
    #         weight = MY_COLLECTION_inverted_index[term].get(doc_id, 0)
    #         weight_matrix[row][col] = weight

    # normalize the weight matrix
    weight_matrix = normalize(weight_matrix, norm='l2')
    print(weight_matrix)
    # print(weight_matrix.shape)    
    return weight_matrix

def visualize_clusters(weight_matrix: np.ndarray, num_clusters: int, cmap: str):
    '''
    Performs K-Means clustering on documents and visualizes results in 2D using PCA.
    
    args:
        weight_matrix (np.ndarray): Document-term weight matrix (num_docs × num_terms)
        num_clusters (int): Number of clusters (k) for K-Means algorithm
        cmap (str): Matplotlib colormap name for visualizing different clusters
    
    Process:
        1. Runs K-Means clustering on the weight matrix
        2. Reduces dimensionality to 2D using PCA for visualization
        3. Transforms cluster centers to the same 2D PCA space
        4. Plots documents as colored points (color = cluster assignment)
        5. Plots cluster centers as red 'X' markers
    
    output:
        - Displays scatter plot of clustered documents
        - Prints cluster labels (array of cluster assignments per document)
        - Prints cluster center coordinates in 2D PCA space
    '''
    kmeans = KMeans(init = "k-means++", n_clusters=num_clusters, random_state=42)
    labels = kmeans.fit_predict(weight_matrix)
    
    pca = PCA(n_components=2)
    weight_matrix_pca = pca.fit_transform(weight_matrix)
    cluster_centers_pca = pca.transform(kmeans.cluster_centers_)

    plt.figure(figsize=(10, 6))
    
    # CORRECT
    scatter = plt.scatter(weight_matrix_pca[:, 0], weight_matrix_pca[:, 1], 
                         c=labels, cmap=cmap, s=50)
    

    # scatter = plt.scatter(weight_matrix[:, 0], weight_matrix[:, 1], 
    #                      c=labels, cmap=cmap, s=50)
    
    # CORRECT
    plt.scatter(cluster_centers_pca[:, 0], cluster_centers_pca[:, 1], 
               s=200, c='black', marker='X',  label='Centroids')
    
    # plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], 
    #            s=200, c='black', marker='X',  label='Centroids')

    cbar = plt.colorbar(scatter)
    cbar.set_label('Cluster ID', rotation=270, labelpad=15)
    
    plt.title(f'K-Means Clustering of Documents (K={num_clusters})', fontsize=14, fontweight='bold')    
    plt.show()