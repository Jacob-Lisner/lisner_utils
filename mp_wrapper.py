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

#def count_intake(path, iter):
#    i = 0
#    with open(path) as f:
#        yield
#        for line in f:
#            i+=1
#            yield (i-1, line)

def input_builder(q, iter, processes):
    for i in iter:
        q.put(i)
    for i in range(processes):
        q.put('END_OF_QUEUE42')


def processer(qI, qO, temp_func):
    bcount = 0
    batch = ""
    while True:
        if(not qI.empty()):
            val = qI.get()
            if val == 'END_OF_QUEUE42':
                qO.put(val)
                break
            else:
                qO.put(temp_func(val)+"\n")

def output_builder(q, path, processes, t0):
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
                    t0 = timer(float(count), t0)
def main(input):
    input_iter, temp, dump_path, t0, processes = input

    qI = Queue()
    qO = Queue()

    pI = Process(target=input_builder, args=(qI, input_iter, processes))
    pI.start()

    ps = []
    for i in range(0, processes):
        p = Process(target=processer, args=(qI, qO, temp))
        ps.append(p)
        p.start()

    pO = Process(target=output_builder, args=(qO, dump_path, processes, t0))
    pO.start()

    pI.join()
    pI.close()
    for p in ps:
        p.join()
        p.close()
    pO.join()
    pO.close()

def exec_self(input_iter, temp, dump_path, t0, processes=6):
    data_in = (input_iter, temp, dump_path, t0, processes)
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
