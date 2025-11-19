import pymupdf
import requests
import nltk
from nltk.tokenize import word_tokenize

nltk.download('punkt_tab')

# reuse this connection
# Speeds up process of fetching PDFs substantially
session = requests.Session()

def extracted_pdf(pdf_url: str) -> list:
    """Check if a PDF is extractable using PyMuPDF."""
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
            print(f"Number of tokens: {len(compressed_tokens)}\n {compressed_tokens[:30]}")


        # SHOULD WE SORT AT ALL????
        # tokens = sorted(list(set(tokens_with_duplicates)))

            terms = list(set(compressed_tokens))
            print(f"Number of tokens: {len(terms)}\n {terms[:10]}")
            return terms
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching PDF from {pdf_url}: {e}")
        return False
    