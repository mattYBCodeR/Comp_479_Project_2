import json
import math 


def inverted_index_constructor(terms: dict, pdf_id: str, inverted_index: dict) -> dict:
    """Adds to an inverted index from the given terms and pdf_id.
        will look like {'term': {'pdf_id': 5},  ...}
    """
    for term, freq in terms.items():
        inverted_index.setdefault(term,{}) [pdf_id] = freq  # Store tf weight of term as value to pdf_id key

    return inverted_index

def MY_COLLECTION_inverted_index_constructor(queried_doc_ids: set, N: int | None) -> dict:
    """Constructs an inverted index from the pdf_ids for MY_COLLECTION. Will look up terms for each pdf_id.
        Will be called in Main
        args:
            queried_doc_ids: set of pdf ids retrieved from the queries
            N: total number of documents in the corpus

        Returns:
            MY_COLLECTION_inverted_index: dict of the inverted index for MY_COLLECTION with the TF-IDF weights
    """

    MY_COLLECTION_inverted_index = {}
    N_MY_COLLECTION = len(queried_doc_ids)

    with open('index.json', 'r') as file:
        original_inverted_index = json.load(file)

    for term, postings in original_inverted_index.items():

        # collect the doc ids that are in both the original posting list and the queried doc ids for each term
        # check if they have the same ones. If so the term is in the MY_COLLECTION
        # then compute the idf weight for that term based on the number of documents in MY_COLLECTION
        collection_postings = postings.keys() & queried_doc_ids 

        if collection_postings:
            document_frequency = len(collection_postings)
            idf_weight = math.log10(N_MY_COLLECTION/document_frequency)
            MY_COLLECTION_inverted_index[term] = {pdf_id: postings[pdf_id] * idf_weight for pdf_id in collection_postings} 
    
    # write the collection index to a json file with the total docs crawled N
    with open(f'MY_COLLECTION_OUTPUTS/MY_COLLECTION_index_{N}.json', 'w') as file:
        json.dump(MY_COLLECTION_inverted_index, file, indent=4)

    return MY_COLLECTION_inverted_index