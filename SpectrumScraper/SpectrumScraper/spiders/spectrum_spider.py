from pathlib import Path
import scrapy
from scrapy.exceptions import CloseSpider
from inverted_index_constructor import inverted_index_constructor
from text_extractor import extracted_pdf
import json

class SpectrumSpider(scrapy.Spider):
    name = 'spectrum'
    start_urls = [
        ' https://spectrum.library.concordia.ca/'
    ]
    craweled_pdf_count = 0
    upper_bound = None
    inverted_index = {}
    pdf_docs = {}


    # def __init__(self, upper_bound = None, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.upper_bound = int(upper_bound) if upper_bound is not None else None
        # self.file = open('pdf_links.txt', 'a') 
        #  ------------- ADDING IN -----------------------
        
#  start by getting the browse link for browsing by documnt type
# then follow the links
    def parse(self, response):
        # get the document type link for theses
        document_type_link = response.css('#main_menu_browse li:nth-child(4) a::attr(href)').get()
        yield response.follow(document_type_link, callback = self.thesis_type_links) # add callback to follow the link to do an action
        
        

    '''Getting Master and PhD thesis links'''
    # get the thesis link from the document type page
    # bcs of bound, only getting master papers
    def thesis_type_links(self, response):

        # GETTING THE THESIS LINKS FOR MASTER AND PHD THESES --> GIVES A LIST OF THE LINKS
        thesis_links = response.css('ul:nth-child(9) ul a::attr(href)').extract()

        # follow each year link to get the thesis links
        for thesis_type in thesis_links:
            yield response.follow(thesis_type, callback=self.parse_years)
        
    '''For the master and phd thesis year page, get all the year links
        and follow each link to get the individual thesis pdf links
        We will trim our year links to only reteive the most recent years 
        since many older pdfs are not extractable since they are scanned'''
    def parse_years(self, response):

        #  collect a list of all the year links. We will then follow each link to get the thesis links
        # NOTE: we trimmed the list to take more recent years since many older pdfs are not extractable since they are scanned
        years = response.css('.ep_view_intro+ ul a::attr(href)').extract()
        recent_years = years[:20]

        for year in recent_years:
            yield response.follow(year, callback=self.parse_thesis_links)

        
    def parse_thesis_links(self, response):
        theses_docs = response.css('p')
        # pop out the last item in the list since it returns an empty doc value
        theses_docs.pop()
        #  to avoid getting orchid links do list[-1]
        for doc in theses_docs:
            doc_link = doc.css('a::attr(href)')[-1].extract()
            yield response.follow(doc_link, callback=self.parse_pdf)



    '''Parse individial thesis pdfs 
    1) this function will respect the upper bound if provided
    2) Once the upper bound is reached, an exception will be raised to stop the spider
    3) Will call the pdf_to_download function to check if the pdf is extractable. If so, write the link to the file
    4) While writing the pdfs into the file, need to flush the file buffer to ensure data is written immediately
    NOTE: Only writing into the file to make sure we are retreiving the correcet pdfs
    '''
    def parse_pdf(self, response):

        # if self.upper_bound is None or self.craweled_pdf_count < self.upper_bound:
        #  get the doc id for when we need to write index into JSON file

        pdf_id = response.url.split('/')[-2]

        pdf_link = response.css('.ep_document_link ::attr(href)').get()
        # restricted_link = response.css('.table .ep_form_action_button')

        if pdf_link:
            if self.upper_bound is None or self.craweled_pdf_count < self.upper_bound:
                tokens = extracted_pdf(pdf_link)
                if tokens:

                        #  BCS WE NEED TO DO TF-IDF LATER, SHOULD I ADD IN FREQUENCY COUNT HERE?
                        # OR SHOULD I JUST DO IT WHEN BUILDING THE INVERTED INDEX LATER?
                        # SHOULD I JUST ADD in duplicates tokens HERE FOR TF-IDF???

                    self.inverted_index = inverted_index_constructor(tokens, pdf_id, self.inverted_index)  
                    # for token in tokens:
                    #     if token in self.inverted_index:
                    #         if pdf_id not in self.inverted_index[token]:
                    #             self.inverted_index[token].append(pdf_id)
                    #     else:
                    #         self.inverted_index[token] = [pdf_id]
                         
                    self.pdf_docs[pdf_id] = pdf_link
                    self.craweled_pdf_count += 1
                    print(f"Crawled PDF count: {self.craweled_pdf_count}\n")
            else: 
                raise CloseSpider('Reached upper bound of PDFs to crawl') 
             
    '''When the spider is closed, write the inverted index to a JSON file'''
    def closed(self, reason):
       
        with open('pdf_links.json', 'w') as f:
           json.dump(self.pdf_docs, f, indent=4)
        # json_inverted_index = json.dumps(self.inverted_index, indent=4)
       
        with open('index.json', 'w') as file:
            json.dump(self.inverted_index, file, indent=4)


