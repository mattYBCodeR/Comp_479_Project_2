from SpectrumScraper.SpectrumScraper.spiders.spectrum_spider import SpectrumSpider
from scrapy.crawler import CrawlerProcess
from src.query_processor import retrieve_documents_on_query
from src.inverted_index_constructor import MY_COLLECTION_inverted_index_constructor, remove_stopwords
from src.vectorization import *
import json
import os
import time

def main():
    
    '''Will start by asking the user if they want to crawl/download new documents
    or use an existing MY_COLLECTION inverted index to avoid crawling/downloading.
    Then, it will design queries to collect spectrum documents on sustainability and waste.
    Next, it will create the MY_COLLECTION inverted index with the proper tf-idf weights.
    Finally, it will run k-means clustering on the MY_COLLECTION weight matrix for k = 2, 10, 20
    and we will plot the results with matplotlib.'''


    start_time = time.time()
    
    use_existing_collections = input('\nDo you want to use an existing MY_COLLECTION inverted index to avoid crawling/downloading? Choosing n may overwrite one of the existing collections if it exists (y/n): ')

    if use_existing_collections == 'y':
        existing_MY_COLLECTION_indexes = [file for file in os.listdir('MY_COLLECTION_OUTPUTS')]

        print('Here are the existing MY_COLLECTION inverted index files:')
        for i, file in enumerate(existing_MY_COLLECTION_indexes, 0):
            print(f"{i}. {file}")
        
        choice = int(input("\nEnter the number of which collection you want to use. The size at the end of the filename indicates the number of documents crawled/downloaded." \
        " Please note choosing a smaller collection may raise errors for larger clusters since k = 2 , 10, 20 is ran altogether. : "))
        chosen_file = os.path.join('MY_COLLECTION_OUTPUTS',existing_MY_COLLECTION_indexes[choice])

        with open(chosen_file, 'r') as file:
            MY_COLLECTION_INVERTED_INDEX = json.load(file)
        
        # remove stopwords
        MY_COLLECTION_INVERTED_INDEX = remove_stopwords(MY_COLLECTION_INVERTED_INDEX, num_stopwords=150)
        
        print(f"Loaded MY_COLLECTION inverted index from {chosen_file}\n")
        
        # Extract and print document IDs for the waste and sustainability queries
        #  SHow docs that are part of the MY COLLECTION INDEX
        MY_COLLECTION_IDS = set()
        sustainability_docs = set()
        waste_docs = set()
        
        for term, term_data in MY_COLLECTION_INVERTED_INDEX.items():
            for doc_id in term_data.keys():
                MY_COLLECTION_IDS.add(doc_id)
                if 'sustainability' in term.lower():
                    sustainability_docs.add(doc_id)
                if 'waste' in term.lower():
                    waste_docs.add(doc_id)
        
        print(f"Documents containing 'sustainability': {len(sustainability_docs)}")
        print(f'Here they are: {sustainability_docs}\n')
        print(f"Documents containing 'waste': {len(waste_docs)}")
        print(f'Here they are: {waste_docs}\n')
        print(f"\nThere were a total of {len(MY_COLLECTION_IDS)} documents in this collection.")
        print(f"Here they are: {MY_COLLECTION_IDS}\n")

    elif use_existing_collections == 'n':

        UPPER_BOUND = input('Enter the upper bound for number of PDFs to crawl or "" for no limit: ')
        if UPPER_BOUND == '':
            UPPER_BOUND = None
        else:
            UPPER_BOUND = int(UPPER_BOUND)

        process = CrawlerProcess() 
        process.crawl(SpectrumSpider, upper_bound=UPPER_BOUND)  # Set upper_bound as needed
        process.start()
    
    #  Designing queries to collect spectrum documents on sustainablity and waste
    # COLLECTING MY COLLECTION IDS
        MY_COLLECTION_IDS = set()
        MY_COLLECTION_IDS = retrieve_documents_on_query('sustainability', MY_COLLECTION_IDS)
        MY_COLLECTION_IDS = retrieve_documents_on_query('waste', MY_COLLECTION_IDS)
        print(f"\nThere were a total of {len(MY_COLLECTION_IDS)} UNIQUE documents retrieved for the queries.\n\n" 
            + f"Here they are: {MY_COLLECTION_IDS   }\n")
        
        #  Creating MY_COLLECTION inverted index with the proper tf-idf weights
        MY_COLLECTION_INVERTED_INDEX = MY_COLLECTION_inverted_index_constructor(MY_COLLECTION_IDS, UPPER_BOUND)
        
        # remove stopwords
        MY_COLLECTION_INVERTED_INDEX = remove_stopwords(MY_COLLECTION_INVERTED_INDEX, num_stopwords=150)

    else:
        print("Invalid input. Rerun the program and enter 'y' or 'n'.")
        return

    # vectorizing the MY_COLLECTION inverted index
    MY_COLLECTION_WEIGHT_MATRIX = vectorize_terms(MY_COLLECTION_INVERTED_INDEX)
        
    #  run clusters on k = 2, 10, 20
    # Test different cluster numbers
    for num_clusters in [2, 10, 20]:
        try:
            cmap = 'coolwarm' if num_clusters == 2 else f'tab{num_clusters}'
            visualize_clusters(MY_COLLECTION_WEIGHT_MATRIX, MY_COLLECTION_INVERTED_INDEX,num_clusters=num_clusters, cmap=cmap)
        except Exception as e:
            print(f"Error during clustering with k={num_clusters}: {e}. This may be due to having fewer documents than clusters.")

    
# ------------------------------------------------------------------------------------

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time/60:.2f} minutes")

if __name__ == "__main__":
    main()
