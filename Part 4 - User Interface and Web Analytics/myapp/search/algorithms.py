from collections import defaultdict
import pandas as pd
import math
import numpy as np
from array import array
import collections
from numpy import linalg as la
from myapp.search.objects import Document
from myapp.search.load_corpus import build_terms

def search_in_corpus(query, index, tf, idf):
    # 1. create create_tfidf_index
    #index, tf, idf = create_index_tfidf(corpus, len(corpus))

    # 2. apply ranking
    return search_tf_idf(query, index, idf, tf)


def create_index_tfidf(corpus, num_documents):
    
    index = defaultdict(list)
    tf = defaultdict(list)
    df = defaultdict(int)  
    idf = defaultdict(float)
    title_index = defaultdict(str)
    
    ll = list(corpus.values())
    for i in range(num_documents):
        line: Document = ll[i]  
        page_id = line.id
        terms = line.cleaned_description
        title = line.title
        title_index[page_id] = title 
        current_page_index = {}
        
        for position, term in enumerate(terms):  ## terms contains page_title + page_text
            try:
                current_page_index[term][1].append(position) 
            except:
                current_page_index[term] = [page_id,  [position]] 

        # Normalize term frequencies
        norm = 0
        for term, posting in current_page_index.items():
            norm += len(posting[1]) ** 2
        norm = math.sqrt(norm)

        # Calculate the tf
        for term, posting in current_page_index.items():
            tf[term].append(np.round(len(posting[1]) / norm, 4)) 
            df[term] += 1 
        
        for term_page, posting_page in current_page_index.items():
            index[term_page].append(posting_page)
        
        # Compute IDF
        for term in df:
            idf[term] = np.round(np.log(float(num_documents / df[term])), 4)

    return index, tf, idf



def rank_documents(terms, docs, index, idf, tf):
    
    doc_vectors = defaultdict(lambda: [0] * len(terms)) 
    query_vector = [0] * len(terms)

    # compute the norm for the query tf
    query_terms_count = collections.Counter(terms)  # get the frequency of each term in the query
    query_norm = la.norm(list(query_terms_count.values()))

    for termIndex, term in enumerate(terms):  # termIndex is the index of the term in the query
        if term not in index:
            continue

        query_vector[termIndex] = query_terms_count[term] / query_norm * idf[term]

        # Generate doc_vectors for matching docs
        for doc_index, (doc, postings) in enumerate(index[term]):
            if doc in docs:
                doc_vectors[doc][termIndex] = tf[term][doc_index] * idf[term]

    # Calculate the score of each doc computing the cosine similarity between queyVector and each docVector
    doc_scores = [[np.dot(curDocVec, query_vector), doc] for doc, curDocVec in doc_vectors.items()]
    doc_scores.sort(reverse=True)
    result_docs = [x[1] for x in doc_scores]
    result_scores = [x[0] for x in doc_scores]
    
    return result_docs, result_scores


def search_tf_idf(query, index, idf, tf):
    """
    output is the list of documents that contain any of the query terms. 
    So, we will get the list of documents for each query term, and take the intersaction of them.
    """
    query = build_terms(query)
    docs = set()
    for term in query:
        try:
            # store in term_docs the ids of the docs that contain "term"
            term_docs = [posting[0] for posting in index[term]]
            # docs = docs Union term_docs
            docs |= set(term_docs)
        except:
            #term is not in index
            pass
    docs = list(docs)
    ranked_docs, result_scores = rank_documents(query, docs, index, idf, tf)
    return ranked_docs, result_scores