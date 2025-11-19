import json


# Retrieve pdf ids for the queries from index.json (inverted index)
def retrieve_documents_on_query(query) -> list:
    with open('index.json', 'r') as file:
        inverted_index = json.load(file)
        if query in inverted_index:
            print(f"\nQuery '{query}' found in the inverted index. There was a total of {len(inverted_index[query])} documents.")
            return inverted_index[query]
        else:
            print(f"\nQuery '{query}' not found in the inverted index.")
            return []

def get_query_pdfs(retrieved_documents):
    pass