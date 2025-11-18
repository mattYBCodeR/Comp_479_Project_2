from os import remove
from SpectrumScraper.SpectrumScraper.spiders.spectrum_spider import SpectrumSpider
from scrapy.crawler import CrawlerProcess
from query_processor import retrieve_documents_on_query
import json
import time

def main():
  
    start_time = time.time()
    
    process = CrawlerProcess()
    # process.crawl(SpectrumSpider)  
    process.crawl(SpectrumSpider, upper_bound=100)  
    process.start()

    # pdfs_to_download = get_theses_pages_links()

    # spider = SpectrumSpider(1000)
    # print(f"PDFs to download: {pdfs_to_download}")
    
    list_of_query_pdfs = []
    list_of_query_pdfs.extend(retrieve_documents_on_query('sustainability'))
    list_of_query_pdfs.extend(retrieve_documents_on_query('waste'))
    print(f"There were a total of {len(list_of_query_pdfs)} documents retrieved for the queries.\n" 
        + f"Here they are: {list_of_query_pdfs}")

    with open('pdf_links.json', 'r') as file:
        pdf_links_dict = json.load(file)
        for pdf_id in list_of_query_pdfs:
            if pdf_id in pdf_links_dict:
                print(f"PDF ID: {pdf_id}, PDF Link: {pdf_links_dict[pdf_id]}\n")
            else:
                print(f"PDF ID: {pdf_id} not found in pdf_links.json\n")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time/60:.2f} minutes")

    # remove('pdf_links.txt')
# def get_theses_pages_links():
        
#     file = 'pdf_links.txt'
#     with open(file, 'r') as f:
#         lines = [line.strip() for line in f if line]
            
#         return lines

# if __name__ == "__main__":
#     main()
