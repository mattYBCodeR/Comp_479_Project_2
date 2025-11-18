from pathlib import Path
import scrapy
from scrapy.exceptions import CloseSpider
from text_extractor import extracted_pdf
import json

class SpectrumSpider(scrapy.Spider):
    name = 'spectrum'
    start_urls = [
        ' https://spectrum.library.concordia.ca/'
    ]
    craweled_pdf_count = 0
    inverted_index = {}
    pdf_docs = {}

    def __init__(self, upper_bound = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.upper_bound = int(upper_bound) if upper_bound is not None else None
        self.file = open('pdf_links.txt', 'a') 
        #  ------------- ADDING IN -----------------------
        
#  start by getting the browse link for browsing by years
# then follow the links
    def parse(self, response):
        year_link = response.css('#main_menu_browse li:nth-child(1) a::attr(href)').get()
        # item = response.css('.spectrum-logo-title a::text')[0].extract()
        # yield {'year_link': year_link}
        yield response.follow(year_link, callback = self.year_links) # add callback to follow the link to do an action
        # self.download_pdfs()
        

    '''Getting the most recent year links is essential
        since many of the older year pdf documents are not extractable.
        Also, the code would take foever to run if we tried to get all the years. 
        Thus, we will only get the most recent years'''
    # get the year links from the year page
    def year_links(self, response):

        # get all year links and put them in a list
        # years = response.css('.ep_view_menu a::attr(href)').extract()

        # GETTING THE MOST RECENT YEARS 
        years = response.css('.ep_view_col_1 li a::attr(href)').extract()

        # follow each year link to get the thesis links
        for year in years:
            yield {'year': year}
            yield response.follow(year, callback=self.parse_year)
        
    '''For each year page get all thesis links and follow them to get the pdf link'''
    def parse_year(self, response):

        thesis_docs = response.css('p')
        
        # go through each individual thesis link for that year
        for doc in thesis_docs:
            link = doc.css('a::attr(href)').get()
            if 'thesis' in str(doc).lower() and 'non-thesis' not in str(doc).lower():
                if 'orcid' not in str(link):
                    # if self.upper_bound is None or self.craweled_pdf_count < self.upper_bound:
                    yield response.follow(link, callback = self.parse_pdf)
                    # else:
                        # raise CloseSpider('Reached upper bound of PDFs to crawl')
                    # yield {
                    
                    #     'response_year' : response.url.split('/')[-1].strip('.html'),
                    #     'count' : count,
                    #     'thesis_link': link
                    # }
                    # count += 1
                    

                    #  write the good urls to a text file 
                    # with open('pdf_links.txt', 'a') as f:
                    #     f.write(str(link) + '\n')
        
        # with open('index.json', 'w') as index_file:
        #     index_file.dump(str(self.inverted_index))

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
        restricted_link = response.css('.table .ep_form_action_button')

        if pdf_link and not restricted_link:
            if self.upper_bound is None or self.craweled_pdf_count < self.upper_bound:
                tokens = extracted_pdf(pdf_link)
                if tokens:

                    for token in tokens:
                        if token in self.inverted_index:
                            if pdf_id not in self.inverted_index[token]:
                                self.inverted_index[token].append(pdf_id)
                        else:
                            self.inverted_index[token] = [pdf_id]
                         
                            

                    self.pdf_docs[pdf_id] = pdf_link
                    self.file.write(str(pdf_link) + '\n')
                    self.file.flush()

                    # yield {'crawled_pdf_count': self.craweled_pdf_count}
                    self.craweled_pdf_count += 1
            else: 
                raise CloseSpider('Reached upper bound of PDFs to crawl') 
             #ADDED IN RN
                # f.write(str(pdf_link) + '\n')
            #     If there iss no upper bound, return all lines --> paper links    
        #  need to crawl each link in the list and convert the pdfs
             
    '''When the spider is closed, write the inverted index to a JSON file'''
    def closed(self, reason):
       
        with open('pdf_links.json', 'w') as f:
           json.dump(self.pdf_docs, f, indent=4)
        # json_inverted_index = json.dumps(self.inverted_index, indent=4)
       
        with open('index.json', 'w') as file:
            json.dump(self.inverted_index, file, indent=4)


