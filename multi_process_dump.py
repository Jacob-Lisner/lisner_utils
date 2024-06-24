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
import ast
from lisner_utils import text_parser as txp


def getxmlcontent(root):
    if root.find('.//HiddenText') is not None:
        return root.find('.//HiddentText').text
    elif root.find('.//Text') is not None:
        return root.find('.//Text').text
    elif root.find('.//FullText') is not None:
        return root.find('.//FullText').text
    else:
        return None

def get_x(data, tot, thresh, thresh_start, time_start):
    try:
        count, path = data[0], data[1]
        warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
        tree = etree.parse(path)
        root = tree.getroot()
        if getxmlcontent(root):
            soup = BeautifulSoup(getxmlcontent(root),features="lxml")
            text = soup.get_text()
        else:
            text = 'Error in processing document'

        #print(text)
        date = root.find('.//AlphaPubDate').text
        publisher = root.find('.//Publisher').text
        paper = root.find('.//Publication/Title').text
        location = root.find('.//Publication/Qualifier').text
        labels = [i.text for i in root.findall('.//ObjectType')]
        word_dict = txp.text_to_words(text)
        warnings.filterwarnings("default", category=UserWarning, module='bs4')
        return [path, word_dict, date, publisher, paper, location, labels]
    except:
        print("Processing Error")
        return None

def get_x_sent(data):
    try:
        count, path = data[0], data[1]
        warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
        tree = etree.parse(path)
        root = tree.getroot()
        if getxmlcontent(root):
            soup = BeautifulSoup(getxmlcontent(root),features="lxml")
            text = soup.get_text()
        else:
            text = 'Error in processing document'

        date = root.find('.//AlphaPubDate').text
        publisher = root.find('.//Publisher').text
        paper = root.find('.//Publication/Title').text
        location = root.find('.//Publication/Qualifier').text
        labels = [i.text for i in root.findall('.//ObjectType')]
        sent_list = txp.ex_sentence(text)
        warnings.filterwarnings("default", category=UserWarning, module='bs4')
        return [path, sent_list, date, publisher, paper, location, labels]
    except:
        print("Processing Error")
        return None

def get_words_mini(dat, global_dict):
    count, inf = dat[0], dat[1]
    try:
        data = json.loads(inf)
    except:
        data = ast.literal_eval(inf)
    paper = data[0]
    if paper is not None:
        for word in paper:
            if word not in global_dict:
                global_dict[word] = 0
            global_dict[word] += paper[word]
    return
#
def get_lex(dat, types, lexicon, tot, thresh, thresh_start, time_start, lex_norm = None, type_check=True, ind_c=False):
    count, inf = dat[0], dat[1]
    try:
        data = json.loads(inf)
    except:
        data = ast.literal_eval(inf)
    labels = set(data[-1])
    failed = type_check
    for type in types:
        if type in labels:
            failed = False
            break
    if failed:
        return None
    try:
        sid = re.search('(?<=[\\\\/])[^\\\\/]*?(?=\.xml)', data[-2]).group()
    except:
        sid = re.search('(?<=[\\\\/])[^\\\\/]*?(?=\.xml)', data[-3]).group()
    paper = data[3]
    date = data[1]
    words = data[0]
    word_count = 0
    lex_count = 0
    ind_counts = {}
    for word in words:
        if word in lexicon:
            lex_count += words[word]
            #return individual decomposition from lexicons
            if(ind_c):
                if word not in ind_counts:
                    ind_counts[word] = 0
                ind_counts[word] += words[word]

        if lex_norm is None:
            word_count += words[word]
        else:
            if word in lex_norm:
                word_count += words[word]
    
    if(ind_c):
        return json.dumps([sid, paper, date, word_count, lex_count, ind_counts])
    return json.dumps([sid, paper, date, word_count, lex_count])

def get_lex2(dat, lexicon, lex_norm = None, ind_c=False):
    write_path, read_path = dat[0], dat[1]
    with open(write_path, 'a') as f:
        with open(read_path, 'r') as f2:
            for inf in f2:
                try:
                    data = json.loads(inf)
                except:
                    data = ast.literal_eval(inf)
                try:
                    sid = re.search('(?<=[\\\\/])[^\\\\/]*?(?=\.xml)', data[-2]).group()
                except:
                    sid = re.search('(?<=[\\\\/])[^\\\\/]*?(?=\.xml)', data[-3]).group()
                paper = data[3]
                date = data[1]
                words = data[0]
                word_count = 0
                lex_count = 0
                ind_counts = {}
                for word in words:
                    if word in lexicon:
                        lex_count += words[word]
                        #return individual decomposition from lexicons
                        if(ind_c):
                            if word not in ind_counts:
                                ind_counts[word] = 0
                            ind_counts[word] += words[word]

                    if lex_norm is None:
                        word_count += words[word]
                    else:
                        if word in lex_norm:
                            word_count += words[word]
                
                if(ind_c):
                    f.write(str(json.dumps([sid, paper, date, word_count, lex_count, ind_counts])) + "\n")
                else:
                    f.write(str(json.dumps([sid, paper, date, word_count, lex_count])) + "\n")