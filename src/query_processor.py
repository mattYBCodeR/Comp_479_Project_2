import json


# Retrieve pdf ids for the queries from index.json (inverted index)
def retrieve_documents_on_query(query: str) -> list:
    with open('index.json', 'r') as file:
        inverted_index = json.load(file)
        if query in inverted_index:
            pdf_ids = list(inverted_index[query].keys())
            print(f"\nQuery '{query}' found in the inverted index. There was a total of {len(inverted_index[query])} documents. "
                  + f"Here they are : {pdf_ids}\n")
            
            return pdf_ids
        else:
            print(f"\nQuery '{query}' not found in the inverted index.")
            return []

def get_query_pdfs(retrieved_documents):
    pass