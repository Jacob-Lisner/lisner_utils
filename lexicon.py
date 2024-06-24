import pandas as pd
import pathlib
import os
import gdown
import pickle
from lisner_utils import loc_refs, cache
import re

#load from singular lexicon csv
def load_csv(path):
    df_lexicon = pd.read_csv(path)
    lexicon = set()
    for word in df_lexicon[df_lexicon.columns[0]]:
        lexicon.add(word)
    return lexicon

#updates master lexicon from the internet
def update_master(master_path = str(pathlib.Path(__file__).parent.resolve()) + "\\",
                  master_file = loc_refs.main('lexicon_master'),
                  reference_file = loc_refs.main('lexicon_reference'),
                  url = loc_refs.main('lexicon_master_url'),
                  gid1 = loc_refs.main('lexicon_master_id_0'),
                  gid2 = loc_refs.main('lexicon_master_id_1')):

    cache.replace(master_path+master_file)
    gdown.download(url+str(gid1), master_path+master_file, quiet=False, fuzzy=True)

    cache.replace(master_path+reference_file)
    gdown.download(url+str(gid2), master_path+reference_file, quiet=False, fuzzy=True)


#restore master lexicon from last backup
def restore_master(master_path = str(pathlib.Path(__file__).parent.resolve()) + "\\",
                  master_file = loc_refs.main('lexicon_master'),
                  reference_file = loc_refs.main('lexicon_reference')):

    cache.restore(master_path+master_file)
    cache.restore(master_path+reference_file)

#load from master lexicon csv
def load_master(column_name, master_path=str(pathlib.Path(__file__).parent.resolve())+"\\"+loc_refs.main('lexicon_master'), update=False, lower=True):
    if(update):
        update_master()
    df_master = pd.read_csv(master_path, dtype='str')
    lexicon = set()
    for word in df_master[column_name]:
        if(isinstance(word, str)):
            if(lower):
                lexicon.add(word.lower())
            else:
                lexicon.add(word)
    return lexicon

def load_roget(ocr = False, add_base = False, roget_path=str(pathlib.Path(__file__).parent.resolve())+"\\"+loc_refs.main('roget_mapper')):
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


def load_roget_2(ocr = False, add_base = False, roget_path=str(pathlib.Path(__file__).parent.resolve())+"\\"+loc_refs.main('roget_mapper_2')):
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
