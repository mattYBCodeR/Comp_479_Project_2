
from SpectrumScraper.SpectrumScraper.spiders.spectrum_spider import SpectrumSpider
from scrapy.crawler import CrawlerProcess
from query_processor import retrieve_documents_on_query
import json
import time

def main():
  
    start_time = time.time()
    
    process = CrawlerProcess() 
    process.crawl(SpectrumSpider)  
    process.start()
    
    query_pdf_ids = []
    query_pdf_ids.extend(retrieve_documents_on_query('sustainability'))
    query_pdf_ids.extend(retrieve_documents_on_query('waste'))
    print(f"There were a total of {len(query_pdf_ids)} documents retrieved for the queries.\n\n" 
        + f"Here they are: {query_pdf_ids}\n")
    
    with open('pdf_links.json', 'r') as file:
        pdf_links_dict = json.load(file)
        for pdf_id in query_pdf_ids:
            if pdf_id in pdf_links_dict:
                print(f"PDF ID: {pdf_id}, PDF Link: {pdf_links_dict[pdf_id]}\n")
            else:
                print(f"PDF ID: {pdf_id} not found in pdf_links.json\n")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time/60:.2f} minutes")

if __name__ == "__main__":
    main()
