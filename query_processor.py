import json

def retrieve_documents_on_query(query):
    with open('index.json', 'r') as file:
        inverted_index = json.load(file)
        if query in inverted_index:
            print(f"Query '{query}' found in the inverted index. There was a total of {len(inverted_index[query])} documents.")
            return inverted_index[query]
        else:
            print(f"Query '{query}' not found in the inverted index.")
            return []

def get_query_pdfs(retrieved_documents):
    pass