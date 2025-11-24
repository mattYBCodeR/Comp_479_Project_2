import pymupdf
import requests

import nltk
from nltk.tokenize import word_tokenize

from itertools import islice
import math

import json

nltk.download('punkt_tab')

# reuse this connection
# Speeds up process of fetching PDFs substantially
session = requests.Session()

def extracted_pdf(pdf_url: str) -> dict | bool:
    """Check if a PDF is extractable using PyMuPDF.
    
    Returns a dictionary of the term and its log weighted frequence for the given doc"""
    # using session instead of request for efficeincy
    try: 
        response = session.get(pdf_url)
        # content = response.content
        with pymupdf.open(stream=response.content) as doc:
            pdf_text = ""

        #  KEEP IN MIND OF ' ' --> TRUE
            for page in doc:
                pdf_text = pdf_text + ' ' + page.get_text()

        # return early if there is no extractable text
            if not pdf_text.strip():
                print(f"PDF at {pdf_url} is not extractable.")
                return False
        
            # KEEP IN MIND TOKENIZING CREATES DUPLICATES
            unfiltered_tokens = word_tokenize(pdf_text)

        # doing some basic compression here by removing non-alpha tokens and lowercasing
        # only adding in tokens that are longer than 2 characters to reduce index size of redundant tokens
            compressed_tokens = [token.lower() for token in unfiltered_tokens if token.isalpha() and len(token) > 2]

            # after compression, check if there are any tokens left. Return early if none
            # is this necessary if i dont increment pdf count in spectrum_spider
            if not compressed_tokens:
                print(f"PDF at {pdf_url} has no valid tokens after compression.")
                return False

        #  Doing some compression here to save time in the future when building the inverted index
            print(f"Number of tokens: {len(compressed_tokens)}\n {compressed_tokens[:20]}")


        # SHOULD WE SORT AT ALL????
        # tokens = sorted(list(set(tokens_with_duplicates)))

            # terms = list(set(compressed_tokens))

            # we will create a term freq hash map to keep track of {term: frequency} 
            '''NOTE: TF = # of times term appears in the given doc / total # of terms in the given doc
            To calculate this, we would take the frequence of the given term and divide it by len(compressed_tokens) 
            create a dictionary of term --> term freq, then create another dictionary of term --> log weighted tf 
            '''
            log_weighted_term_frequencies = tf(compressed_tokens)

            
            return log_weighted_term_frequencies
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching PDF from {pdf_url}: {e}")
        return False

def tf(terms: list) -> dict: 
    ''' Function takes a list of terms 
    1) Get the frequency of each term in the list
    2) Calculate the log weighted term frequency for each term'''

    term_frequencies = {}

    for term in terms:
        term_frequencies[term] = term_frequencies.get(term,0) + 1 
    
    log_weighted_term_frequencies = {}

    for term in term_frequencies:
        log_weighted_term_frequencies[term] =  math.log10(term_frequencies.get(term)) + 1

    print(f"Number of tokens: {len(term_frequencies)}\n {dict(list(term_frequencies.items())[:20])}")
    print(f"Number of tokens: {len(log_weighted_term_frequencies)}\n {dict(list(log_weighted_term_frequencies.items())[:20])}")
            
    
    return log_weighted_term_frequencies

def idf(N:int, term: str) -> int:
    ''' Load in json file and get the length of the posting list for term'''
    with open('index.json', 'r') as file:
        inverted_index = json.load(file)

        # retrieve posting list for the term
        posting_list = inverted_index.get(term)
        document_frequency = len(posting_list)

        idf = math.log10(N/document_frequency)
        pass