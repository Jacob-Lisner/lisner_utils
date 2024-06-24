import os
import re
import pysbd
import string
import nltk
import traceback


#text preprocessing to work well with pysbd
def prep_text(text_orig, poem_mode = False):
    text = text_orig
    #add newline for poetic breaks to ensure they're captured:
    if poem_mode:
        punct = re.escape(string.punctuation)
        text = re.sub("([" + punct + "]\s*\n)", "\\1\n", text)
    #trim 1 newline (helps with speech)
    text = re.sub("(\s*)\n", "\\1 ", text)
    #trim excessive newline whitespace
    text = re.sub("(?<=[ \t\r\f\v])[ \t\r\f\v]+", " ", text)
    #convert paragraph into extra newline
    text = re.sub("\\\\P+", "\n", text)
    return text


#gets a list of sentences
def ex_sentence(text, seg = None, poem_mode = False, pre = False):
    if seg is None:
        seg = pysbd.Segmenter(language="en", clean = True)
    txt = prep_text(text, poem_mode=poem_mode)
    sents = seg.segment(txt)
    return sents



#re for custom tokenizer
start = "[^\s\'\"\(\{\[“‘]"
con_segs = ["[a-zA-Z](?:[a-zA-Z]*(?:[\-\'’][a-zA-Z]+)+|[a-zA-Z]+)",  #all lower case (2 letter min, hyphens and apost)
            #"[A-Z](?:[A-Z]*(?:[\-\'][A-Z]+)+|[A-Z]+)",  #all upper case ('')
            #"[A-Z](?:[a-z]*(?:[\-\'][a-z]+)+|[a-z]+)",  #upper start then rest lowercase ('')
            "A", "a", "I"]                             #single letter words        "smith" + " george" = "smith george"
content = con_segs[0]
for i in range(1, len(con_segs)):
    content += "|" + con_segs[i]
end = "[^\s\'\"\)\]\}\!\?\-\:\;\,\.’”]"
reg_token = re.compile("(?<!"+start+")("+content+")(?!"+end+")", re.DOTALL)

#re for custom tokenizer
start = "[^\s\'\"\(\{\[“‘]"
con_segs = ["[a-zA-Z0-9](?:[a-zA-Z0-9]*(?:[\-\'’][a-zA-Z0-9]+)+|[a-zA-Z0-9]+)",  #all lower case (2 letter min, hyphens and apost)
            #"[A-Z](?:[A-Z]*(?:[\-\'][A-Z]+)+|[A-Z]+)",  #all upper case ('')
            #"[A-Z](?:[a-z]*(?:[\-\'][a-z]+)+|[a-z]+)",  #upper start then rest lowercase ('')
            "A", "a", "I"]                             #single letter words
content = con_segs[0]

for i in range(1, len(con_segs)):
    content += "|" + con_segs[i]
end = "[^\s\'\"\)\]\}\!\?\-\:\;\,\.’”]"
reg_token_num = re.compile("(?<!"+start+")("+content+")(?!"+end+")", re.DOTALL)

start = "[^\s\'\"\(\{\[“‘]"
con_segs = ["[a-zA-Z0-9](?:[a-zA-Z0-9]*(?:[\-\'’][a-zA-Z0-9]+)+|[a-zA-Z0-9]+)",  #all lower case (2 letter min, hyphens and apost)
            #"[A-Z](?:[A-Z]*(?:[\-\'][A-Z]+)+|[A-Z]+)",  #all upper case ('')
            #"[A-Z](?:[a-z]*(?:[\-\'][a-z]+)+|[a-z]+)",  #upper start then rest lowercase ('')
            "A", "a", "I"]                             #single letter words
content = con_segs[0]
for i in range(1, len(con_segs)):
    content += "|" + con_segs[i]
end = "[^\s\'\"\)\]\}\!\?\-\:\;\,\.’”]"
reg_token_emoji = re.compile(u'[\U00010000-\U000FFFFF]+'+"|(?<!"+start+")"+content+"(?!"+end+")", re.DOTALL)

#gets a list of tokens
def ex_tokens(text, num = False, emoji = False):
    if num:
        return reg_token_num.findall(text)
    if emoji:
        return reg_token_emoji.findall(text)
    return reg_token.findall(text)

#gets a count of tokens
def ex_words(toks, low = True):
    words = {}
    for word in toks:
        if(low):
            wrd = word.lower()
        else:
            wrd = word
        if wrd not in words:
            words[wrd] = 0
        words[wrd] += 1
    return words

def text_to_words(text, num = False):
    return ex_words(ex_tokens(text, num=num))

#return a dictionary, where the keys are the names of all the files in a path,
#and the values are an array of entities from that file
#handles txt files
#valid entities include:
#  "raw" - return the raw text
#  "words" - return the raw tokens of text
#  "word_dict" - grabs word counts with a generic re
#  "word_total" - grabs the total number of words
#  "sents" - uses modified psybd parser to get sentences
#  "sents_words" - grabs the tokens of sentence
#  "sents_dict" - above, but gets BOW for sentence instead of raw sentence
#  "sents_total"
#  "lexicon" - creates a lexicon re and applies it to the text
def extract_from_text(path, entities = {"words", "word_total"}, poem_mode = False, encoding = 'utf8'):
    entries = {}
    seg = pysbd.Segmenter(language="en", clean = True)
    items = [] #os.listdir(path)
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            if((re.search("\.txt$",name) is None)):
                continue
            else:
                items.append(os.path.join(root, name))
    for item in items:
        #print(item)
        #print(re.sub("\\\\", "\\\\", path))
        with open(item, 'r', encoding=encoding) as f:
            text = f.read()
        file = re.search("(?<=^"+re.sub("\\\\", "\\\\\\\\", path)+").*(?=\.)", item).group()
        file = re.sub("\\\\", "/", file)
        entries[file] = {}
        entry = entries[file]

        val_sent = ["sents", "sents_words","sents_dict", "sents_total"]
        if len([k for k in val_sent if k in entities]) > 0:
            sents = ex_sentence(text, seg=seg, poem_mode=poem_mode)
            if("sents" in entities):
                entry["sents"] = sents
            if("sents_dict" in entities or "sents_words" in entities):
                if("sents_dict" in entities):
                    entry["sents_dict"] = []
                if("sents_words" in entities):
                    entry["sents_words"] = []
                for sent in sents:
                    toks = ex_tokens(sent)
                    if("sents_dict" in entities):
                        entry["sents_dict"].append(ex_words(toks))
                    if("sents_words" in entities):
                        entry["sents_words"].append(toks)
            if("sents_total" in entities):
                entry["sents_total"] = len(sents)

        val_word = ["tokens", "words", "word_total"]
        if len([k for k in val_word if k in entities]) > 0:
            toks = ex_tokens(text)
            if("tokens" in entities):
                entry["tokens"] = toks
            if("words" in entities):
                entry["words"] = ex_words(toks)
            if("word_total" in entities):
                entry["word_total"] = len(toks)
        if "raw" in entities:
            entry["raw"] = text

    return entries
