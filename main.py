
from SpectrumScraper.SpectrumScraper.spiders.spectrum_spider import SpectrumSpider
from scrapy.crawler import CrawlerProcess
from query_processor import retrieve_documents_on_query
from inverted_index_constructor import MY_COLLECTION_inverted_index_constructor
import json
import time

def main():
  
    start_time = time.time()
    
    process = CrawlerProcess() 
    process.crawl(SpectrumSpider, upper_bound=10)  # Set upper_bound as needed
    process.start()
    
    #  Designing queries to collect spectrum documents on sustainablity and waste
    # COLLECTING MY COLLECTION IDS
    MY_COLLECTION_IDS = set()
    MY_COLLECTION_IDS.update(retrieve_documents_on_query('sustainability'))
    MY_COLLECTION_IDS.update(retrieve_documents_on_query('waste'))
    print(f"\nThere were a total of {len(MY_COLLECTION_IDS)} UNIQUE documents retrieved for the queries.\n\n" 
        + f"Here they are: {MY_COLLECTION_IDS   }\n")
    

#  Creating MY_COLLECTION inverted index
    MY_COLLECTION_INVERTED_INDEX = MY_COLLECTION_inverted_index_constructor(MY_COLLECTION_IDS)
    # print(f'Here is the constructed MY_COLLECTION inverted index:\n {MY_COLLECTION_INVERTED_INDEX}')
   
# ------------------------------------------------------------------------------------

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time/60:.2f} minutes")

if __name__ == "__main__":
    main()
