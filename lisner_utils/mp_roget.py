import re
import os
import time
import pandas as pd
import numpy as np
import pickle
import json
from bs4 import BeautifulSoup
from lxml import etree
import time
import datetime
import warnings
import sys, importlib
import multiprocessing as mp
from multiprocessing import Process, Queue
import ast
from lisner_utils import text_parser as txp
from functools import partial
from multiprocessing import get_context
import sys
import pathlib
import subprocess
from subprocess import Popen, PIPE
import random
import time

def p_pow(x):
    return x*x

def timer(current:float, t0):
    end, thresh, thresh_start, time_start = t0
    if(current/end > thresh_start):
        sys.stdout.write("Complete: "
                         + "%.1f%%" % (100*current/end)
                         + " -- Elapsed:"
                         + " %.1f" % (time.time()-time_start)
                         + " seconds -- Estimated Remaining:"
                         + " %.1f" % ((end-current)*(time.time()-time_start)/current)
                         + " seconds\\r\r")

        sys.stdout.flush()
        #time_start = time.time()
        thresh_start = current/end+thresh
    return thresh_start

def get_roget(dat, types, roget, type_check=True, rog_only = True):
    count, inf = dat[0], dat[1]
    data = ast.literal_eval(inf)
    labels = set(data[-1])
    failed = type_check
    for type in types:
        if type in labels:
            failed = False
            break
    if failed:
        return None
    sid = re.search('(?<=\\\\)[^\\\\]*?(?=\.xml)', data[0]).group()
    paper = data[4]
    date = data[2]
    words = data[1]

    word_to_min = roget[0]
    min_to_dims = roget[1]
    heir = []
    for maxes in np.amax(np.array(list(min_to_dims.values())), axis=0):
        heir.append(np.zeros(maxes+1).astype('int'))

    word_count = 0
    for word in words:
        if not rog_only:
            word_count += 1
        word_sets = []
        for h in range(0, len(heir)):
            word_sets.append(set())
        if word in word_to_min:
            if rog_only:
                word_count += 1
            wmins = word_to_min[word]
            for m in wmins:
                for h in range(0, len(heir)):
                    word_sets[h].add(min_to_dims[m][h])
            for h in range(0, len(heir)):
                for g in word_sets[h]:
                    heir[h][g]+=1


    lex_grid = []
    for h in heir:
        lex_grid.append(list(h))
    return (sid, paper, date, word_count, lex_grid)


def count_intake(path):
    i = 0
    with open(path) as f:
        for line in f:
            i+=1
            yield (i-1, line)

def input_builder(q, path, processes):
    iter = count_intake(path)
    for i in iter:
        q.put(i)
    for i in range(processes):
        q.put('END_OF_QUEUE42')

def processer(qI, qO, temp, batch_size = 50):
    bcount = 0
    batch = ""
    while True:
        if(not qI.empty()):
            val = qI.get()
            if val == 'END_OF_QUEUE42':
                if(len(batch) != 0):
                    qO.put(batch)
                qO.put(val)
                break
            else:
                batch = batch + str(temp(val)) + "\n"
                bcount += 1
                if(bcount == batch_size):
                    qO.put(batch)
                    batch = ""
                    bcount = 0

def output_builder(q, path, processes, t0, batch_size = 50):
    pr_done = 0
    count = 0
    with open(path, 'w') as f:
        while True:
            if(not q.empty()):
                val = q.get()
                if val == 'END_OF_QUEUE42':
                    pr_done += 1
                    if pr_done == processes:
                        break
                    else:
                        continue

                elif val == None:
                    continue
                else:
                    f.write(val)
                    count+=batch_size
                    t0[2] = timer(float(count), t0)


def main(args):
    timer, roget, paper_name, count_path, dump_path, processes, type_check, types = args

    tot, thresh, thresh_start = timer
    time_start = time.time()

    t0 = [tot, thresh, thresh_start, time_start]


    temp = partial(get_roget,
        types = types,
        roget = roget,
        type_check=type_check)

    #pool = get_context("spawn").Pool(processes=processes)
    #with open(dump_path, 'w') as f:
    #    for paper in pool.imap_unordered(temp, count_intake(count_path), chunksize=100):
#            if paper is not None:
    #            f.write(str(paper) + "\n")
    #pool.close()
    #pool.join()
    #pool = get_context("spawn").Pool(processes=4)
    sys.stdout.flush()
    qI = Queue()
    qO = Queue()
    sys.stdout.flush()

    pI = Process(target=input_builder, args=(qI, count_path, processes))
    pI.start()
    sys.stdout.flush()
    ps = []
    for i in range(0, processes):
        p = Process(target=processer, args=(qI, qO, temp))
        ps.append(p)
        p.start()

    sys.stdout.flush()
    pO = Process(target=output_builder, args=(qO, dump_path, processes, t0))
    pO.start()

    pI.join()
    pI.close()
    for p in ps:
        p.join()
        p.close()
    pO.join()
    pO.close()

def exec_self(timer=0, roget=0, paper_name=0, count_path=0, dump_path=0, processes=6, type_check = False, types = []):
    data_in = (timer, roget, paper_name, count_path, dump_path, processes, type_check, types)
    pickle_path =  os.path.join(str(pathlib.Path(__file__).parent.resolve()),"execself_"+str(time.time())+"_temp.pickle")
    with open(pickle_path, "wb") as f:
        pickle.dump(data_in, f)

    p = Popen(['python.exe', os.path.join(str(pathlib.Path(__file__).parent.resolve()),'mp_roget.py'), pickle_path],
        stdin=PIPE,
        stdout=PIPE,
        stderr=subprocess.STDOUT,
        bufsize = 1,
        universal_newlines=True,
        shell=True)


    while True:
        output = p.stdout.readline()
        if len(output) == 0 and p.poll() is not None:
            break
        elif len(output) > 0:
            #sys.stdout.write(output)
            #sys.stdout.flush()
            if(output[-3:] == '\\r\n'):
                sys.stdout.write(output[:-3]+'\r')#
                sys.stdout.flush()
            else:
                sys.stdout.write(output)#
                sys.stdout.flush()
    rc = p.poll()
    p.kill()

if __name__ == '__main__':
    args_path = sys.argv[1]
    with open(args_path, "rb") as f:
        args = pickle.load(f)
    os.remove(args_path)
    main(args)
    #timer, roget, paper_name, count_path, dump_path, processes=6, type_check = False, types = []
    #main()
