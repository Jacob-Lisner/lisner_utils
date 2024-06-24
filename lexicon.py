import pandas as pd
import pathlib
import gdown

from lisner_utils import loc_refs, cache

import os

#load from singular lexicon csv
def load_csv(path):
    df_lexicon = pd.read_csv(path)
    lexicon = set()
    for word in df_lexicon[df_lexicon.columns[0]]:
        lexicon.add(word)
    return lexicon
#updates master lexicon from the internet
def update_master(master_path = str(pathlib.Path(__file__).parent.resolve()),
                  master_file = loc_refs.main('lexicon_master'),
                  url = loc_refs.main('lexicon_master_url'),
                  gid1 = loc_refs.main('lexicon_master_id_0')):

    cache.replace(master_path+master_file)
    gdown.download(url+str(gid1), os.path.abspath(os.path.join(master_path, master_file)), quiet=False, fuzzy=True)
#restore master lexicon from last backup
def restore_master(master_path = str(pathlib.Path(__file__).parent.resolve()),
                  master_file = loc_refs.main('lexicon_master')):
    cache.restore(os.path.abspath(os.path.join(master_path, master_file)))

#load from master lexicon csv
def load_master(column_name, master_path=os.path.abspath(os.path.join(str(pathlib.Path(__file__).parent.resolve()), loc_refs.main('lexicon_master'))), update=False, lower=True):
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