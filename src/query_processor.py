import json

# Retrieve pdf ids (postings list) for the queries "waste" and "sustainability" from index.json (inverted index)
# update the query_set with the retrieved pdf ids and return it --> avoids duplicates
def retrieve_documents_on_query(query: str, query_set: set) -> set:
    with open('index.json', 'r') as file:
        inverted_index = json.load(file)
        if query in inverted_index:
            pdf_ids = list(inverted_index[query].keys())
            query_set.update(pdf_ids)
            print(f"\nQuery '{query}' found in the inverted index. There was a total of {len(inverted_index[query])} documents. "
                  + f"Here they are : {pdf_ids}\n")
            
        else:
            print(f"\nQuery '{query}' not found in the inverted index.")
            
    return query_set

# def get_query_pdfs(retrieved_documents):
#     pass