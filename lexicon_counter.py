import pickle
import os
import re
import multiprocessing as mp
from multiprocessing import get_context

import sys
from os.path import dirname
sys.path.append(dirname(__file__))

from lisner_utils2 import multi_process_dump as mpd
from lisner_utils2 import lexicon as lx
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
        inds = False,
        processes=mp.cpu_count(),
        big_path = "10000_word_dictionary.pickle",
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
        if __name__ == '__main__':
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
                        fold = re.search("\\\\([^\\\\_]*)[^\\\\]*\\\\[^\\\\]*$", count_path).groups()[0]+"\\"+lex_name
                    else:
                        fold = re.search("\\\\([^\\\\_]*)[^\\\\]*\\\\[^\\\\]*$", count_path).groups()[0]+"\\"+lex_name
                    folder = '..\\!Lexicon_Counts\\'+fold
                    if not os.path.exists(folder):
                        os.mkdir(folder)
                    lexicon = lx.load_master(lex_name)
                    temp = partial(mpd.get_lex, types = types, lexicon=lexicon, tot=0, thresh=0, thresh_start=0, time_start = 0, lex_norm=lex_norm, type_check=False, ind_c=inds)
                    #temp = partial(mpd.get_lex2, path = os.path.abspath(folder+'\\'+paper_name+'_'+lex_name+'_norm-big0'), types = types, lexicon=lexicon, tot=0, thresh=0, thresh_start=0, time_start = 0, lex_norm=lex_norm, type_check=False, ind_c=inds)

                    with open(folder+'\\'+paper_name+'_'+lex_name+'_norm-big0.txt', 'w') as f:
                        for paper in pool.imap_unordered(temp, 
                                                        count_intake(os.path.abspath(count_path)), 
                                                        chunksize=1000):
                            if paper is not None:
                                f.write(str(paper) + "\n")
                                
            pool.close()
            pool.join()

if __name__ == "__main__":
    main()