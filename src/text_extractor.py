import pymupdf  # https://pymupdf.readthedocs.io/en/1.26.6/
import requests  # https://requests.readthedocs.io/en/v2.32.5/
import nltk
from nltk.tokenize import word_tokenize  # https://www.nltk.org/api/nltk.tokenize.html
import math

nltk.download('punkt_tab')

# Reuse connection for efficiency
session = requests.Session()  # https://requests.readthedocs.io/en/v2.32.5/user/advanced/#session-objects

def extracted_pdf(pdf_url: str) -> dict | bool:
    """
    Extracts text from PDF and calculates log-weighted term frequencies.
    
    Args:
        pdf_url: URL of PDF document
    
    Returns:
        dict: {term: log_weighted_tf} if successful, False otherwise
    """
    try: 
        response = session.get(pdf_url)
        
        with pymupdf.open(stream=response.content) as doc:  # https://pymupdf.readthedocs.io/en/1.26.6/document.html
            pdf_text = ""

        #  KEEP IN MIND OF ' ' --> TRUE
            for page in doc:
                pdf_text += ' ' + page.get_text() 

        # return early if there is no extractable text
            if not pdf_text.strip():
                print(f"PDF at {pdf_url} is not extractable.")
                return False
        
            # KEEP IN MIND TOKENIZING CREATES DUPLICATES
            unfiltered_tokens = word_tokenize(pdf_text)

        # doing some basic compression here by removing non-alpha tokens and lowercasing
        # only adding in tokens that are longer than 2 characters to reduce index size of redundant tokens
            compressed_tokens = [token.lower() for token in unfiltered_tokens if token.isalpha() and len(token) > 2]

            # after compression, check if there are any terms in the list. Return early if none
            if not compressed_tokens:
                print(f"PDF at {pdf_url} has no valid tokens after compression.")
                return False

            print(f"Number of tokens: {len(compressed_tokens)}\n {compressed_tokens[:20]}")


            # we will create a term freq hash map to keep track of {term: frequency} 
            '''NOTE: TF = # of times term appears in the given pdf
            create a dictionary of {term: term_freq}, then create another dictionary of {term: log weighted tf} 
            '''
            log_weighted_term_frequencies = tf(compressed_tokens)

            return log_weighted_term_frequencies
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching PDF from {pdf_url}: {e}")
        return False

def tf(terms: list) -> dict: 
    """
    Calculates log-weighted term frequency: 1 + log10(term_count).
    
    Args:
        terms: List of terms
    
    Returns:
        dict: {term: log_weighted_tf}
    """
    # Count term frequencies
    term_frequencies = {}
    for term in terms:
        term_frequencies[term] = term_frequencies.get(term,0) + 1 
    
    # Apply log weighting: 1 + log10(tf)
    log_weighted_term_frequencies = {}
    for term in term_frequencies:
        log_weighted_term_frequencies[term] = math.log10(term_frequencies.get(term)) + 1

    print(f"Number of unique terms: {len(term_frequencies)}\n {dict(list(term_frequencies.items())[:20])}")
    print(f"Some log-weighted TF:\n {dict(list(log_weighted_term_frequencies.items())[:20])}")
    
    return log_weighted_term_frequencies
