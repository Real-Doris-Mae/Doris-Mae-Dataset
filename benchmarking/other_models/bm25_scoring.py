import json
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
import re
from nltk import word_tokenize, sent_tokenize
import numpy as np
from tqdm import tqdm

def preprocessing(text):
    '''
    Note, this preprocessing function should be applied to any text before getting its embedding. 
    Input: text as string
    
    Output: removing newline, latex $$, and common website urls. 
    '''
    pattern = r"(((https?|ftp)://)|(www.))[^\s/$.?#].[^\s]*"
    text = re.sub(pattern, '', text)
    return text.replace("\n", " ").replace("$","")

def all_ranking_bm25(bm25, q, abstract_l, q_candidates, query_mode):
    if query_mode == "paragraph":
        query_l = word_tokenize(q)
        similarities = bm25.get_scores(query_l)
    elif query_mode == 'sentence':
        sent_text = sent_tokenize(q)
        query_sent = [s for s in sent_text if len(preprocessing(s)) >= 5]
        similarity_list = []
        for sentence in query_sent:
            query_l = word_tokenize(sentence)
            similarity = bm25.get_scores(query_l)
            similarity_list.append(similarity)
        similarities = np.mean(similarity_list, axis=0)
    
    sorted_indices = np.argsort(similarities)[::-1]
    ranked_list = [q_candidates[idx] for idx in sorted_indices]
    return ranked_list

def all_ranking_result_bm25(dataset, query_mode):
    query_lists = [q['query_text'] for q in dataset['Query']]
    candidate_list = [q['candidate_pool'] for q in dataset['Query']]
    rank_dict_list = []
    abstracts = dataset['Corpus']
    for i in tqdm(range(len(query_lists))):
        rank_dict = {}
        q = query_lists[i]
        q_candidates = candidate_list[i]
        abs_list = [preprocessing(abstracts[idx]['original_abstract']) for idx in q_candidates]
        tokenized_abstract = [word_tokenize(doc) for doc in abs_list]
        bm25_abs = BM25Okapi(tokenized_abstract)
        ranked_list = all_ranking_bm25(bm25_abs, q, abs_list, q_candidates, query_mode)
        rank_dict['index_rank'] = ranked_list
        rank_dict_list.append(rank_dict)
        
    return rank_dict_list

