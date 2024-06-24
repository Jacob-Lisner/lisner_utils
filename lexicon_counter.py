import sys
import os
import pathlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pickle
import os
import re
import multiprocessing as mp
from multiprocessing import get_context

from lisner_utils import multi_process_dump as mpd
from lisner_utils import lexicon as lx
from lisner_utils import loc_refs
from functools import partial

def count_intake(path):
    i = 0
    with open(path) as f:
        for line in f:
            i+=1
            yield (i-1, line)

def main(
        lex_names, 
        paper_folders,
        output_folder,
        inds = False,
        processes=mp.cpu_count(),
        big_path = os.path.abspath(os.path.join(str(pathlib.Path(__file__).parent.resolve()), loc_refs.main("big_word_10000"))),
        types = [
            'Front Page/Cover Story', 
            'Front Matter',
            'Feature', 
            'Article', 
            'General Information', 
            'News', 
            'Review', 
            'Letter to the Editor', 
            'Correspondence', 
            'Editorial',
            'Commentary',
            'Military/War News',
            ]
        ):
    
    with open(big_path, "rb") as f:
        big_word = pickle.load(f)
    lex_norm = big_word
    for cp in paper_folders:
        #if __name__ == '__main__':
        pool = get_context("spawn").Pool(processes=processes)
        for file in os.listdir(cp):
            paper_name = file[:-4]
            print("==============================")
            print(paper_name)
            count_path = cp+paper_name+'.txt'
            for lex_name in lex_names:
                print("------------------------------")
                print(lex_name)
                if inds:
                    fold = os.path.join(os.path.split(os.path.dirname(count_path))[1]+"_Inds", lex_name)
                else:
                    fold = os.path.join(os.path.split(os.path.dirname(count_path))[1], lex_name)
                folder = os.path.join(output_folder, fold)
                if not os.path.exists(folder):
                    os.makedirs(folder)
                lexicon = lx.load_master(lex_name)
                temp = partial(mpd.get_lex, types = types, lexicon=lexicon, tot=0, thresh=0, thresh_start=0, time_start = 0, lex_norm=lex_norm, type_check=False, ind_c=inds)
                #temp = partial(mpd.get_lex2, path = os.path.abspath(folder+'\\'+paper_name+'_'+lex_name+'_norm-big0'), types = types, lexicon=lexicon, tot=0, thresh=0, thresh_start=0, time_start = 0, lex_norm=lex_norm, type_check=False, ind_c=inds)

                with open(os.path.join(folder,paper_name+'_'+lex_name+'.txt'), 'w') as f:
                    for paper in pool.imap_unordered(temp, 
                                                    count_intake(os.path.abspath(count_path)), 
                                                    chunksize=1000):
                        if paper is not None:
                            f.write(str(paper) + "\n")
                            
        pool.close()
        pool.join()

if __name__ == "__main__":
    main()