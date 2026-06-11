# COMP 479 Project 2: Document Clustering with Inverted Index

## Project Overview

This project crawls Concordia Spectrum's thesis repository, builds an inverted index with TF-IDF weights, and performs K-Means clustering on documents related to sustainability and waste management.

## Installation

### Using requirements.txt

```bash
pip install -r requirements.txt
```

### Post-Installation Setup

```bash
# Download NLTK punkt tokenizer data
python -c "import nltk; nltk.download('punkt_tab')"
```

## Running the Project

```bash
python main.py
```

**Choose Execution Mode:**

- **Option A (Use Existing)**: Enter `y` Select collection | Skip crawling
- **Option B (Crawl New)**: Enter `n` Specify PDF count (e.g., 200)

## Output Files

### Generated Files

1. **`index.json`**

   - Full inverted index with TF weights
   - Structure: `{'term': {'doc_id': tf_weight, ...}, ...}`

2. **`pdf_links.json`**

   - Used for evaluating the pdfs being crawled (only testing purposes and not used for anything else)
   - Mapping of document IDs to PDF URLs
   - Structure: `{'doc_id': 'pdf_url', ...}`

3. **`MY_COLLECTION_OUTPUTS/MY_COLLECTION_index_{N}.json`**

   - Filtered collection index with TF-IDF weights
   - `{N}` = number of documents crawled
   - Structure: `{'term': {'doc_id': tfidf_weight, ...}, ...}`

4. **`Cluster_Results/clustering_results_k{2,10,20}.txt`**
   - Top 50 terms per cluster with TF-IDF weights
   - Document count per cluster
   - Separate file for each k value

## Package Versions & Documentation

### Core Dependencies

- **Python**: 3.10+

- **Scrapy**: 2.13.3

  - Documentation: https://docs.scrapy.org/en/2.13/
  - Used for: Web crawling and spider management

- **PyMuPDF**: 1.26.6

  - Documentation: https://pymupdf.readthedocs.io/en/1.26.6/
  - Used for: PDF text extraction

- **NLTK**: 3.9.2

  - Documentation: https://www.nltk.org/
  - Tokenization: https://www.nltk.org/api/nltk.tokenize.html
  - Used for: Text tokenization (word_tokenize)

- **NumPy**: 2.2.6

  - Documentation: https://numpy.org/doc/2.2/
  - Used for: Matrix operations and numerical computations

- **Scikit-learn**: 1.7.2

  - Documentation: https://scikit-learn.org/1.7/
  - KMeans: https://scikit-learn.org/1.7/modules/generated/sklearn.cluster.KMeans.html
  - Normalize: https://scikit-learn.org/1.7/modules/generated/sklearn.preprocessing.normalize.html
  - TruncatedSVD: https://scikit-learn.org/1.7/modules/generated/sklearn.decomposition.TruncatedSVD.html
  - Used for: K-Means clustering, LSA dimensionality reduction, vector normalization

- **Matplotlib**: 3.10.7

  - Documentation: https://matplotlib.org/3.10.7/contents.html
  - Used for: Visualization and plotting

- **Requests**: 2.32.5
  - Documentation: https://requests.readthedocs.io/en/v2.32.5/
  - Used for: HTTP requests to fetch PDFs

## Project Structure

```
Project2/
├── main.py                          # Main entry point
├── requirements.txt                 # Package dependencies
├── README.md
├── SpectrumScraper/
│   └── SpectrumScraper/
│       └── spiders/
│           └── spectrum_spider.py   # Web crawler
├── src/
│   ├── text_extractor.py           # PDF text extraction & TF calculation
│   ├── inverted_index_constructor.py # Index construction & TF-IDF
│   ├── query_processor.py          # Query processing
│   └── vectorization.py            # Vectorization & clustering
├── MY_COLLECTION_OUTPUTS/          # Saved MY COLLECTION inverted indexes (TF-IDF weights)
├── Cluster_Results/                # Clustering output files for k = 2, 10, 20
├── index.json                      # Main inverted index (TF weights only)
└── pdf_links.json                  # PDF URL mappings
```

## Pipeline Explanation

### High-Level Overview

This project implements a complete document clustering pipeline that transforms raw PDFs into numerical representations and groups similar documents together. The process involves data collection, text processing, statistical weighting, and machine learning-based clustering.

### Pipeline Stages

#### 1. **Web Crawling & PDF Collection**
The pipeline begins by using Scrapy to crawl the Concordia Spectrum thesis repository. The spider navigates through thesis types (Master/PhD), years, and individual thesis listings to locate PDF links. Documents are downloaded and processed in real-time during the crawl rather than batching them afterward. This streaming approach keeps memory usage manageable for large collections.

#### 2. **Text Extraction & Tokenization**
Once a PDF is downloaded, PyMuPDF extracts all text from every page into a continuous string. This raw text is then tokenized using NLTK's `word_tokenize()` function, which breaks it into individual words and punctuation. The tokens are filtered to retain only:
- Lowercase alphabetic words
- Length greater than 2 characters
- This filtering removes common punctuation and single-character tokens that add noise

The result is a clean list of terms representing the document's meaningful content.

#### 3. **TF (Term Frequency) Calculation**
For each document, term frequencies are calculated using logarithmic weighting to prevent high-frequency terms from dominating:

**TF = 1 + log₁₀(count)**

Examples:
- A term appearing 1 time: TF = 1.0
- A term appearing 10 times: TF = 2.0
- A term appearing 100 times: TF = 3.0

This logarithmic scaling reflects that the importance of a term doesn't increase proportionally with its frequency. All TF-weighted terms are accumulated in a global **inverted index**, where each term maps to the documents containing it and their respective TF scores.

#### 4. **Collection Filtering (Query-Based)**
Instead of clustering all crawled documents, the project filters the collection by searching for documents containing domain-specific terms: "sustainability" or "waste". This query-based filtering creates **MY_COLLECTION**—a focused subset of documents most relevant to the research domain.

#### 5. **TF-IDF Transformation**
For documents in MY_COLLECTION, raw TF weights are transformed into TF-IDF weights:

**TF-IDF = TF × IDF**

where **IDF = log₁₀(N / document_frequency)**

- **N** = total documents in MY_COLLECTION
- **document_frequency** = number of documents containing that term

IDF serves as a penalization factor:
- **Common terms** (appearing in many documents): Lower IDF, reduced TF-IDF weight
- **Rare/distinctive terms** (appearing in few documents): Higher IDF, boosted TF-IDF weight

This transformation makes the weights more meaningful for clustering by downweighting generic vocabulary and emphasizing domain-specific terminology.

#### 6. **Stopword Removal**
The 150 most frequently occurring terms (by document frequency) are identified and removed as stopwords. These are typically generic words that appear across many documents without adding discriminative value. Examples include common English words that don't contribute to cluster differentiation. Removing them reduces dimensionality and noise in downstream analysis.

#### 7. **Vectorization**
The filtered inverted index is converted into a numerical **document-term matrix**:
- **Rows** = individual documents
- **Columns** = unique terms (after stopword removal)
- **Cell values** = TF-IDF weights

For example, a collection of 1,000 documents with 5,000 unique terms creates a 1000×5000 matrix. Each row represents one document's "profile" across all terms.

The matrix is then **L2-normalized**, scaling each document vector so its Euclidean length equals 1:

**normalized_row = row / √(sum of row²)**

This normalization ensures that clustering distance metrics treat all documents fairly, preventing longer documents from dominating distance calculations.

#### 8. **K-Means Clustering**
K-Means partitions the normalized document-term matrix into **k clusters** (k = 2, 10, or 20). The algorithm works as follows:

1. **Initialization**: k cluster centers are selected using "k-means++" intelligent seeding, which spreads initial centers apart to improve convergence
2. **Assignment**: Each document is assigned to its nearest cluster center (using Euclidean distance)
3. **Update**: Cluster centers are recalculated as the centroid (mean) of all assigned documents
4. **Iteration**: Steps 2-3 repeat until convergence (centers stabilize)

Documents end up in the same cluster when they have similar term profiles, meaning they share similar distributions of important terms.

#### 9. **Dimensionality Reduction (LSA) for Visualization**
The high-dimensional document vectors (potentially thousands of dimensions, one per term) are reduced to 2D using **Truncated Singular Value Decomposition (TruncatedSVD)**, which implements Latent Semantic Analysis (LSA):

- Preserves the most important variance in the data
- Captures semantic relationships between terms and documents
- Enables visual scatter plot representation while maintaining clustering structure

This 2D projection allows human interpretation of how clusters are distributed in semantic space.

#### 10. **Result Output**
For each k value (2, 10, 20), the pipeline generates:

1. **Scatter plot visualization**: Documents plotted in 2D space, colored by cluster assignment, with cluster centroids marked
2. **Text report** (`clustering_results_k{k}.txt`): 
   - Top 50 most representative terms per cluster, ranked by their weight in the cluster centroid
   - Provides interpretability by showing what distinguishes each cluster
   - Document count statistics per cluster

---

## Key Concepts Summary

| Concept | Purpose | Formula/Method |
|---------|---------|-----------------|
| **Tokenization** | Convert raw text into individual analyzable terms | NLTK word_tokenize() + filtering |
| **Term Frequency (TF)** | Weight terms by their frequency within a document | 1 + log₁₀(count) |
| **Inverse Document Frequency (IDF)** | Weight terms by their rarity across the collection | log₁₀(N / df) |
| **TF-IDF** | Combined weight reflecting both local importance and global distinctiveness | TF × IDF |
| **L2 Normalization** | Scale all document vectors to equal magnitude for fair distance comparisons | row / √(sum of row²) |
| **K-Means Clustering** | Partition documents into k groups based on similarity | Iterative centroid-based partitioning |
| **LSA (Latent Semantic Analysis)** | Compress high-dimensional data to 2D for visualization | TruncatedSVD preserving variance |
| **Inverted Index** | Efficient data structure mapping terms to documents containing them | {term: {doc_id: weight}} |

---

## Workflow Summary

1. **Crawl** PDFs from Spectrum repository (Scrapy)
2. **Extract** text and tokenize (PyMuPDF + NLTK)
3. **Weight** terms with TF (logarithmic scaling)
4. **Filter** documents by domain queries (sustainability, waste)
5. **Transform** to TF-IDF weights (raw frequencies → normalized importance)
6. **Clean** by removing stopwords (top 150 terms)
7. **Vectorize** into document-term matrix with L2 normalization
8. **Cluster** using K-Means (k=2, 10, 20)
9. **Visualize** with LSA dimensionality reduction (2D scatter plots)
10. **Report** top 50 terms per cluster for interpretability

The pipeline ultimately transforms unstructured PDF text into mathematically-comparable document vectors, then discovers natural groupings based on shared terminology and semantic relationships.

## Execution Sequence

### 1. Where Code is Ran (`main.py`)

**Option A - Use Existing Collection:**

```python
# Load saved index
with open(chosen_file, 'r') as file:
    MY_COLLECTION_INVERTED_INDEX = json.load(file)
```

**Option B - Crawl New Documents:**

```python
# Step 1: Initialize Scrapy CrawlerProcess
process = CrawlerProcess()

# Step 2: Start web crawling
process.crawl(
    SpectrumSpider, # Name of our Spider class
    upper_bound=UPPER_BOUND  # None = crawl all, or specify number (e.g., 200)
)
process.start()

# Step 3: Retrieve documents matching queries
MY_COLLECTION_IDS = retrieve_documents_on_query(
    query='sustainability',  # Search term
    query_set=MY_COLLECTION_IDS  # Existing document IDs (initially empty set)
)
MY_COLLECTION_IDS = retrieve_documents_on_query(
    query='waste',
    query_set=MY_COLLECTION_IDS
)

# Step 4: Build MY_COLLECTION inverted index with TF-IDF weights
MY_COLLECTION_INVERTED_INDEX = MY_COLLECTION_inverted_index_constructor(
    queried_doc_ids=MY_COLLECTION_IDS,  # Documents matching queries
    N=UPPER_BOUND  # Total documents crawled (for filename)
)
```

**Common Steps For Both Choices:**

```python
# Step 1: Remove stopwords (top 150 most frequent terms by document frequency)
MY_COLLECTION_INVERTED_INDEX = remove_stopwords(
    inverted_index=MY_COLLECTION_INVERTED_INDEX,
    num_stopwords=150  # Default: 150
)

# Step 2: Vectorize to document-term matrix
MY_COLLECTION_WEIGHT_MATRIX = vectorize_terms(
    MY_COLLECTION_inverted_index=MY_COLLECTION_INVERTED_INDEX  # TF-IDF weighted index
)
# Returns: L2-normalized 2D numpy array

# Step 3: Run K-Means clustering for k=2, 10, 20
for num_clusters in [2, 10, 20]:
    cmap = 'coolwarm' if num_clusters == 2 else f'tab{num_clusters}'
    visualize_clusters(
        weight_matrix=MY_COLLECTION_WEIGHT_MATRIX,  # Document-term matrix
        MY_COLLECTION=MY_COLLECTION_INVERTED_INDEX,  # Inverted index (for term names)
        num_clusters=num_clusters,  # k value (2, 10, or 20)
        cmap=cmap  # Matplotlib colormap ('coolwarm' for k=2, 'tab10'/'tab20' for others)
    )
```

### 2. Web Crawling (`spectrum_spider.py`)

**Crawling Parameters:**

- **`upper_bound`**: Maximum number of PDFs to crawl (None = no limit)

**Function Sequence:**

```python
parse(response)
# Extracts document type link calls thesis_type_links()

thesis_type_links(response)
# Gets Master/PhD thesis links calls parse_years()

parse_years(response)
# Retrieves recent 20 years calls parse_thesis_links()

parse_thesis_links(response)
# Extracts individual thesis links calls parse_pdf()

parse_pdf(response)
# Parameters: response
# Returns: None (updates class attributes)
# Process:
#   1. Extract pdf_id and pdf_link
#   2. Call extracted_pdf(pdf_link)  returns {term: tf_weight}
#   3. Call inverted_index_constructor(
#         terms={term: tf_weight},
#         pdf_id=pdf_id,
#         inverted_index=self.inverted_index
#      )
#   4. Store in self.inverted_index and self.pdf_docs
#   5. Increment self.craweled_pdf_count

closed(reason)
# Saves index.json and pdf_links.json
```

### 3. Text Extraction (`text_extractor.py`)

**`extracted_pdf(pdf_url: str) -> dict | bool`**

```python
# Parameters:
#   pdf_url (str): URL of PDF document
# Returns:
#   {term: log_weighted_tf} if successful
#   False if extraction fails

# Process:
response = session.get(pdf_url)                # Fetch PDF via HTTP
doc = pymupdf.open(stream=response.content)    # Open PDF with PyMuPDF
pdf_text = ' '.join(page.get_text() for page in doc)  # Extract text from all pages
tokens = word_tokenize(pdf_text)               # Tokenize with NLTK
compressed_tokens = [token.lower() for token in tokens          # Filter: lowercase, alpha-only, length > 2
                    if token.isalpha() and len(t) > 2]
return tf(compressed_tokens)                            # Calculate TF weights
```

**`tf(terms: list) -> dict`**

```python
# Parameters:
#   terms (list): List of tokenized terms
# Returns:
#   {term: 1 + log10(count)}

term_frequencies = {}
for term in terms:
    term_frequencies[term] = term_frequencies.get(term, 0) + 1

return {term: 1 + math.log10(count)
        for term, count in term_frequencies.items()}
```

### 4. Index Construction (`inverted_index_constructor.py`)

**`inverted_index_constructor(terms: dict, pdf_id: str, inverted_index: dict) -> dict`**

```python
# Parameters:
#   terms (dict): {term: tf_weight} from single document
#   pdf_id (str): Document identifier
#   inverted_index (dict): Existing index to update
# Returns:
#   {'term': {'pdf_id': tf_weight, ...}}

for term, freq in terms.items():
    inverted_index.setdefault(term, {})[pdf_id] = freq
return inverted_index
```

**`remove_stopwords(inverted_index: dict, num_stopwords: int) -> dict`**

```python
# Parameters:
#   inverted_index (dict): Index to filter
#   num_stopwords (int): Number of top terms to remove (default: 150)
# Returns:
#   Filtered inverted index

# Sort terms by document frequency (descending)
term_postings = [(term, len(postings))
                 for term, postings in inverted_index.items()]
term_postings.sort(key=lambda x: x[1], reverse=True)

# Remove top N most frequent terms
for term, _ in term_postings[:num_stopwords]:
    inverted_index.pop(term)
return inverted_index
```

**`MY_COLLECTION_inverted_index_constructor(queried_doc_ids: set, N: int) -> dict`**

```python
# Parameters:
#   queried_doc_ids (set): Documents matching query terms
#   N (int): Total documents crawled (used for filename)
# Returns:
#   {'term': {'pdf_id': tfidf_weight, ...}}

with open('index.json', 'r') as file:
    original_index = json.load(file)

N_collection = len(queried_doc_ids)
MY_COLLECTION = {}

for term, postings in original_index.items():
    collection_docs = postings.keys() & queried_doc_ids

    if collection_docs:
        # IDF = log10(N_collection / document_frequency)
        idf = math.log10(N_collection / len(collection_docs))

        # TF-IDF = TF x IDF
        MY_COLLECTION[term] = {
            doc_id: postings[doc_id] * idf
            for doc_id in collection_docs
        }

# Save to JSON file
with open(f'MY_COLLECTION_OUTPUTS/MY_COLLECTION_index_{N}.json', 'w') as f:
    json.dump(MY_COLLECTION, f, indent=4)

return MY_COLLECTION
```

### 5. Query Processing (`query_processor.py`)

**`retrieve_documents_on_query(query: str, query_set: set) -> set`**

```python
# Parameters:
#   query (str): Search term (e.g., 'sustainability', 'waste')
#   query_set (set): Existing document IDs to update
# Returns:
#   Updated set of document IDs (no duplicates)

with open('index.json', 'r') as file:
    inverted_index = json.load(file)

    if query in inverted_index:
        pdf_ids = list(inverted_index[query].keys())
        query_set.update(pdf_ids)  # Add to existing set

return query_set
```

### 6. Vectorization & Clustering (`vectorization.py`)

**`vectorize_terms(MY_COLLECTION_inverted_index: dict) -> np.ndarray`**

```python
# Parameters:
#   MY_COLLECTION_inverted_index (dict): {'term': {'doc_id': tfidf_weight}}
# Returns:
#   L2-normalized numpy array (num_docs x num_terms)

# Extract unique document IDs and terms
document_ids = set()
for postings in MY_COLLECTION_inverted_index.values():
    document_ids.update(postings.keys())

doc_rows = sorted(list(document_ids))
term_cols = list(MY_COLLECTION_inverted_index.keys())

# Create zero matrix
weight_matrix = np.zeros((len(doc_rows), len(term_cols)))

# Populate matrix with TF-IDF weights
for col, term in enumerate(term_cols):
    for row, doc_id in enumerate(doc_rows):
        weight_matrix[row][col] = MY_COLLECTION_inverted_index[term].get(doc_id, 0)

# Apply L2 normalization (norm='l2')
return normalize(weight_matrix, norm='l2')
```

**`visualize_clusters(weight_matrix: np.ndarray, MY_COLLECTION: dict, num_clusters: int, cmap: str)`**

```python
# Parameters:
#   weight_matrix (np.ndarray): Document-term matrix (num_docs x num_terms)
#   MY_COLLECTION (dict): Inverted index (used to extract term names)
#   num_clusters (int): k value (2, 10, or 20)
#   cmap (str): Matplotlib colormap ('coolwarm', 'tab10', 'tab20')

# Step 1: K-Means clustering
kmeans = KMeans(
    init="k-means++",           # Initialization method
    n_clusters=num_clusters,    # Number of clusters (k)
    n_init=10,                  # Number of initializations
    random_state=42             # Random seed for reproducibility
)
labels = kmeans.fit_predict(weight_matrix)

# Step 2: LSA dimensionality reduction for 2D visualization
lsa = TruncatedSVD(
    n_components=2,      # Reduce to 2 dimensions
    random_state=42      # Random seed for reproducibility
)
weight_matrix_2d = lsa.fit_transform(weight_matrix)

# Step 3: Create scatter plot
plt.scatter(
    weight_matrix_2d[:, 0],  # X-axis (first LSA component)
    weight_matrix_2d[:, 1],  # Y-axis (second LSA component)
    c=labels,                # Color by cluster
    cmap=cmap,               # Colormap
    s=50                     # Marker size
)

# Plot cluster centroids
plt.scatter(
    lsa.transform(kmeans.cluster_centers_)[:, 0],
    lsa.transform(kmeans.cluster_centers_)[:, 1],
    s=200,           # Larger marker size
    c='black',       # Black color
    marker='X',      # X marker
    label='Centroids'
)

# Step 4: Extract top 50 terms per cluster
order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
terms = list(MY_COLLECTION.keys())

# Step 5: Write clustering results to file
with open(f'Cluster_Results/clustering_results_k{num_clusters}.txt', 'w') as f:
    for cluster_id in range(num_clusters):
        for rank, term_idx in enumerate(order_centroids[cluster_id, :50], 1):
            tfidf = kmeans.cluster_centers_[cluster_id, term_idx]
            f.write(f'{rank}. {terms[term_idx]}: {tfidf:.8f}\n')

plt.show()  # Display plot
```
