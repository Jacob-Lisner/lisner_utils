#this utility helps for generating and synthesisizing data standards
#for a base text entry

#conventional standard is a directory with a ref.pickle (for a dictionary)
#and a text file

# valid fields in the dictionary are:
# Ref ID
# Text_File
# Date
# Labels (sub dict)

import os
import pickle

def parse_standard(path):
    for file in os.listdir(path):
        if file.endswith(".pickle"):
            with open(os.path.join(path,file), 'rb') as f:
                std_d = pickle.load(os.path.join)
                break

    with open(os.path.join(path,std_d['Text_File']), 'r') as f:
        text = f.read()

    return (std_d['Ref ID'], std_d['Date'], std['Labels'], text)

def generate_standard(path, ref_id, date, labels, text, text_name=None):
    
