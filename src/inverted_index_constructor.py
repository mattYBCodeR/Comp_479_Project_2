import json
import math 


def inverted_index_constructor(terms: dict, pdf_id: str, inverted_index: dict) -> dict:
    """
    Adds terms from a document to the inverted index with TF weights.
    
    Args:
        terms: {term: tf_weight} from a single document
        pdf_id: Document identifier
        inverted_index: Existing index to update
    
    Returns:
        Updated inverted index: {'term': {'pdf_id': tf_freq, ...}, ...}
    """
    for term, freq in terms.items():
        inverted_index.setdefault(term,{}) [pdf_id] = freq  # Store tf weight of term as value to pdf_id key

    return inverted_index


def remove_stopwords(inverted_index: dict, num_stopwords: int) -> dict:
    """
    Removes top N most frequent terms by document frequency.
    
    Filters out common terms (e.g., "research", "study") that appear in
    many documents but provide little discriminative value for clustering.
    
    Args:
        inverted_index: {'term': {'pdf_id': weight, ...}, ...}
        num_stopwords: Number of top terms to remove
    
    Returns:
        Filtered inverted index with high-frequency terms removed
    """
    # get the doc frequency of each term and then sort the list from greates to least   
    term_postings_counts = [(term, len(postings)) for term, postings in inverted_index.items()]
    term_postings_counts.sort(key = lambda posting: posting[1], reverse=True)

    # Remove top N terms
    for term, posting_counts in term_postings_counts[:num_stopwords]:
        inverted_index.pop(term)

    return inverted_index


def MY_COLLECTION_inverted_index_constructor(queried_doc_ids: set, N: int | None) -> dict:
    """
    Builds MY_COLLECTION inverted index with TF-IDF weights.
    
    Filters original index to only documents matching queries, then
    calculates IDF weights based on collection size.
    
    Args:
        queried_doc_ids: Document IDs matching query terms
        N: Total documents crawled (used for filename)
    
    Returns:
        MY_COLLECTION index: {'term': {'pdf_id': tfidf_weight, ...}
    
    Process:
        1. Load original index (TF weights only)
        2. Filter with documents in queried_doc_ids
        3. Calculate IDF: log10(N_collection / document_frequency)
        4. Calculate TF-IDF: TF x IDF
        5. Save to MY_COLLECTION_OUTPUTS/MY_COLLECTION_index_{N}.json
    """
    MY_COLLECTION_inverted_index = {}
    N_MY_COLLECTION = len(queried_doc_ids)

    with open('index.json', 'r') as file:
        original_inverted_index = json.load(file)

    for term, postings in original_inverted_index.items():
        # Find documents in both posting list and query results
        collection_postings = postings.keys() & queried_doc_ids 

        if collection_postings:
            # Calculate IDF weight
            document_frequency = len(collection_postings)
            idf_weight = math.log10(N_MY_COLLECTION / document_frequency)
            
            # Calculate TF-IDF for each document
            MY_COLLECTION_inverted_index[term] = {
                pdf_id: postings[pdf_id] * idf_weight 
                for pdf_id in collection_postings
            } 
    
    # Save to JSON
    with open(f'MY_COLLECTION_OUTPUTS/MY_COLLECTION_index_{N}.json', 'w') as file:
        json.dump(MY_COLLECTION_inverted_index, file, indent=4)

    return MY_COLLECTION_inverted_index