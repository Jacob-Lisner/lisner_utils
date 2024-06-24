import pandas as pd
import pathlib
import os
import gdown
import pickle
from lisner_utils import loc_refs, cache
import re
import copy

def load(ocr = False, add_base = False, roget_path=str(pathlib.Path(__file__).parent.resolve())+"\\"+loc_refs.main('roget_mapper')):
    #file_name = loc_refs.main('roget_mapper')
    with open(roget_path, 'rb') as f:
        mapper = pickle.load(f)
    if(not ocr):
        return mapper

    ocr_map = {}
    for word in mapper[0]:
        if(re.search('^[a-zA-Z\'-]+$', word) is not None):
            if word.lower() not in ocr_map:
                ocr_map[word.lower()] = []
            for form in mapper[0][word]:
                ocr_map[word.lower()].extend(mapper[0][word][form])
    if(add_base):
        i = 0
        for key in mapper[1]:
            mapper[1][key].append(i)
            i+=1
    return (ocr_map, mapper[1])


def load_2(ocr = False, add_base = False, roget_path=str(pathlib.Path(__file__).parent.resolve())+"\\"+loc_refs.main('roget_mapper_2')):
    #file_name = loc_refs.main('roget_mapper')
    with open(roget_path, 'rb') as f:
        mapper = pickle.load(f)
    if(not ocr):
        return mapper

    ocr_map = {}
    for word in mapper[0]:
        if(re.search('^[a-zA-Z\'-]+$', word) is not None):
            if word.lower() not in ocr_map:
                ocr_map[word.lower()] = []
            for form in mapper[0][word]:
                ocr_map[word.lower()].extend(mapper[0][word][form])
    if(add_base):
        i = 0
        for key in mapper[1]:
            mapper[1][key].append(i)
            i+=1
    return (ocr_map, mapper[1], mapper[2])

def get_subs(lref, level, slevel, base = None, return_a = False):
    if level >= slevel:
        return None
    if base is None:
        base = load_2(ocr = True)

    word_map, category_map, term_map = base

    subs = []
    for sub in category_map[len(category_map)-slevel]:
        if(category_map[len(category_map)-slevel][sub][level] == lref):
            subs.append(sub)
    return subs

def get_ans(lrefs, level, base = None):
    if base is None:
        base = load_2(ocr = True)
    word_map, category_map, term_map = base

    ans = []
    if(level == 0):
        ind = {k:i for i,k in enumerate(range(0, len(term_map[0])))}
    else:
        ind = {k:i for i,k in enumerate(category_map[len(category_map)-level].keys())}
    #print(ind)
    for ref in lrefs:
        #print(ind[ref])
        ans.append(term_map[level][ind[ref]])
        #else:

    return ans

def get_roget_mod(base = None):
    if base is None:
        base = load_2(ocr = True)
    word_map, category_map, term_map = base

    cat_map = copy.deepcopy(category_map[0])
    i = 0
    for key in cat_map:
        cat_map[key].append(i)
        i+=1
    return (copy.deepcopy(word_map.copy()), cat_map)
