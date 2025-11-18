import pymupdf
import requests
import nltk
from nltk.tokenize import word_tokenize

nltk.download('punkt_tab')
def extracted_pdf(pdf_url) -> str:
    """Check if a PDF is extractable using PyMuPDF."""

    doc_text_by_pages = []
    
    try: 
        response = requests.get(pdf_url)
        content = response.content
        doc = pymupdf.open(stream=content)

        for i, page in enumerate(doc, start=1):
            text = page.get_text()

            # is this wrong??? For exampple if edxtract text from page 1 but page 2 is not extractable so I just move on. Is this a bad approach?
            # return early if there is no extractable text
            if text == "":
                print(f"Page {i} is not extractable.")
                return False
            
            print(f"Page {i} text length: {len(text)}")
            doc_text_by_pages.append(text)
            
        # Remove whitespaces from the extracted text.
        doc_text_by_pages = [text.strip() for text in doc_text_by_pages]
        full_text = ' '.join(doc_text_by_pages)
        print(len(full_text))

        unfiltered_tokens = word_tokenize(full_text)

        #  Doing some compression here to save time in the future when building the inverted index
        tokens_with_duplicates = [token.lower() for token in unfiltered_tokens if token.isalpha()]
        print(f"Number of tokens: {len(tokens_with_duplicates)}\n {tokens_with_duplicates[:100]}")


        # SHOULD WE SORT AT ALL????
        # tokens = sorted(list(set(tokens_with_duplicates)))

        tokens = list(set(tokens_with_duplicates))
        print(f"Number of tokens: {len(tokens)}\n {tokens[:100]}")


        return tokens
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching PDF from {pdf_url}: {e}")
        return False
    