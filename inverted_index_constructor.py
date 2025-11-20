import json 

def inverted_index_constructor(tokens: list, pdf_id: str, inverted_index: dict) -> dict:
    """Constructs an inverted index from the given tokens and pdf_id."""
    for token in tokens:
        if token in inverted_index:
            if pdf_id not in inverted_index[token]:
                inverted_index[token].append(pdf_id)
        else:
            inverted_index[token] = [pdf_id]
    return inverted_index

def MY_COLLECTION_inverted_index_constructor(queried_doc_ids: set) -> dict:
    """Constructs an inverted index from the pdf_ids for MY_COLLECTION. Will look up tokens for each pdf_id.
        Will be called in Main
    """
    MY_COLLECTION_inverted_index = {}
    with open('index.json', 'r') as file:
        original_inverted_index = json.load(file)

    for term, postings in original_inverted_index.items():
        # print(term, token)
        collection_postings = [pdf_id for pdf_id in postings if pdf_id in queried_doc_ids]   

        if collection_postings:
            MY_COLLECTION_inverted_index[term] = collection_postings 
        
    with open('MY_COLLECTION_index.json', 'w') as file:
        json.dump(MY_COLLECTION_inverted_index, file, indent=4)

    return MY_COLLECTION_inverted_index