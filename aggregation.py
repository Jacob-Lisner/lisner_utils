import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lisner_utils import lexicon as lex
import ast
import json
import os
import time
import datetime
import numpy as np
import pandas as pd
import sys
from dateutil.relativedelta import relativedelta
from IPython.core.display import display, HTML
display(HTML("<style>.container { width:85% !important; }</style>"))

#modern:
def convert_to_json(roget_line):
    line = "["+roget_line[1:-2]+"]"
    line = re.sub("\'", "\"", line)
    return line

def delta_date(x, start, interval=1):
    delta = x-start
    return delta.days//interval

def date_aggregate(files):
    aggregate = {}
    time_start = time.time()
    i = 0
    for path in files:
        with open(path) as f:
            for line in f:
                entry = json.loads(convert_to_json(line))
                #entry = ast.literal_eval(line)
                #print(entry)
                if entry[2] not in aggregate:
                    aggregate[entry[2]] = [0, 0]

                #total
                aggregate[entry[2]][0] += entry[1]

                #lexicon
                aggregate[entry[2]][1] += entry[0]
                if(i%1000) == 0:
                    sys.stdout.write(f"{time.time()-time_start:.2f}"+" seconds\r")
                    sys.stdout.flush()
                i+=1
    print()
    return aggregate


def parse_aggregate(entry, aggregate, subs, ind):
    if(subs):
        if entry[1] not in aggregate:
            aggregate[entry[1]] = {}
        if entry[2] not in aggregate[entry[1]]:
            aggregate[entry[1]][entry[2]] = [0, 0, 0]
        
        #total
        aggregate[entry[1]][entry[2]][0] += entry[3]
        #document
        aggregate[entry[1]][entry[2]][2] += 1
        #lexicon
        if(ind is None):
            aggregate[entry[1]][entry[2]][1] += entry[4]
        else:
            if(ind in entry[5]):
                aggregate[entry[1]][entry[2]][1] += entry[5][ind]

    else:
        if entry[2] not in aggregate:
            aggregate[entry[2]] = [0, 0, 0]

        #total
        aggregate[entry[2]][0] += entry[3]
        #document
        aggregate[entry[2]][2] += 1

        #lexicon
        if(ind is None):
            aggregate[entry[2]][1] += entry[4]
        else:
            if(ind in entry[5]):
                aggregate[entry[2]][1] += entry[5][ind]

def date_aggregate(files, subs = False, inds = None):
    if(inds is None):
        aggregate = {}
    else:
        aggregates = {}
        for word in inds:
            aggregates[word] = {}
    time_start = time.time()
    fileschecked = set()
    repeats = 0
    i = 0
    for path in files:
        with open(path) as f:
            for line in f:
                #print(line)
                try:
                    entry = json.loads(convert_to_json(line))
                except:
                    entry = ast.literal_eval(line)
                    #print(entry)
                #entry = ast.literal_eval(line)
                if entry[0] in fileschecked:
                    repeats+=1
                    continue
                else:
                    fileschecked.add(entry[0])

                if(inds is None):
                    parse_aggregate(entry, aggregate, subs, None)
                else:
                    for word in inds:
                        aggregate = aggregates[word]
                        parse_aggregate(entry, aggregate, subs, word)           

                # if(subs):
                #     if entry[1] not in aggregate:
                #         aggregate[entry[1]] = {}
                #     if entry[2] not in aggregate[entry[1]]:
                #         aggregate[entry[1]][entry[2]] = [0, 0]
                    
                #     #total
                #     aggregate[entry[1]][entry[2]][0] += entry[3]
                #     #lexicon
                #     if(inds is None):
                #         aggregate[entry[1]][entry[2]][1] += entry[4]

                # else:
                #     if entry[2] not in aggregate:
                #         aggregate[entry[2]] = [0, 0]

                #     #total
                #     aggregate[entry[2]][0] += entry[3]

                #     #lexicon
                #     aggregate[entry[2]][1] += entry[4]

                
                if(i%1000) == 0:
                    sys.stdout.write(f"{time.time()-time_start:.2f}"+" seconds\r")
                    sys.stdout.flush()
                i+=1
    print(repeats)
    if(inds is None):
        return aggregate
    else:
        return aggregates



def get_date_sum(path, 
                 week_range, 
                 day_offset = 0, 
                 gap = 7, 
                 gap_type = 'days',
                 is_dir = True,
                 mod_type = None,
                 roll=7, 
                 diff = False,
                 ind_i = None,
                 ret_tot = False):
    
    inds = None
    sub = False
    rolling = False
    if mod_type == 'Inds':
        inds = ind_i
    elif mod_type == 'Subs':
        sub = True
    elif(mod_type == 'Rolling'):
        rolling = True

    subs = sub    
    if is_dir:
        files = []
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path,f)):
                files.append(os.path.join(path,f))
    else:
        files = [path]
    
    data = date_aggregate(files, subs=subs, inds = inds)

    if((not sub) and (inds is not None)):
        subs = True
    
    weeks = []

    if(gap_type == 'days'):
        st = datetime.datetime(week_range[0], 1, 1) + datetime.timedelta(days=day_offset)
        nt = st+datetime.timedelta(days=gap)
        end = datetime.datetime(week_range[1], 12, 31) + datetime.timedelta(days=day_offset)
        while(nt < end):
            weeks.append([st, nt])
            st = nt
            nt = st+datetime.timedelta(days=gap)
        
        weeks.append([st, nt])
        st = nt
        nt = st+datetime.timedelta(days=gap)

    elif(gap_type == 'months'):
        #print("HIT IT")
        gapm = relativedelta(months=gap)
        st = datetime.datetime(week_range[0], 1, 1) + gapm#datetime.timedelta(months=day_offset)
        nt = st+gapm#datetime.timedelta(months=gap)
        end = datetime.datetime(week_range[1], 12, 31) + gapm#datetime.timedelta(months=day_offset)
        while(nt < end):
            weeks.append([st, nt])
            st = nt
            nt = st+gapm
        
        weeks.append([st, nt])
        st = nt
        nt = st+gapm#datetime.timedelta(months=gap)

    elif(gap_type == 'years'):
        st = datetime.datetime(week_range[0], 1, 1)
        nt = datetime.datetime(week_range[0]+1*gap, 1, 1)
        end = datetime.datetime(week_range[1]+1*gap, 12, 31)
        i = 2
        while(nt < end):
            weeks.append([st, nt])
            st = nt
            nt = datetime.datetime(week_range[0]+i*gap, 1, 1)
            i+=1
        
        #weeks.append([st, nt])
        #st = nt
        #nt = st+datetime.timedelta(years=gap)


    if(subs):
        dates = np.zeros(len(weeks)*len(data), dtype=object)
        for i in range(0, len(weeks)*len(data)):
            dates[i] = weeks[i%len(weeks)][0]
        word_sums = np.zeros(len(dates)*len(data))
        doc_sums = np.zeros(len(dates))
        lex_sums = np.zeros(len(dates)*len(data))

        rolls = []
        j = 0
        for key in data:
            rolls.append(key)
            for dat in data[key]:
                try:
                    date = datetime.datetime.strptime(dat, '%b %d, %Y')
                except:
                    date = datetime.datetime.strptime(dat, '%Y-%m-%d')
                for i in range(0, len(weeks)):
                    if date >= weeks[i][0] and date < weeks[i][1]:
                        word_sums[j*len(weeks)+i] += float(data[key][dat][0])
                        doc_sums[j*len(weeks)+i] += float(data[key][dat][2])
                        lex_sums[j*len(weeks)+i] += float(data[key][dat][1])
                        break
            j+=1


    else:
        dates = np.zeros(len(weeks), dtype=object)
        for i in range(0, len(weeks)):
            dates[i] = weeks[i][0]
        word_sums = np.zeros(len(dates))
        doc_sums = np.zeros(len(dates))
        lex_sums = np.zeros(len(dates))
    
        for dat in data:
            try:
                date = datetime.datetime.strptime(dat, '%b %d, %Y')
            except:
                date = datetime.datetime.strptime(dat, '%Y-%m-%d')
            for i in range(0, len(weeks)):
                if date >= weeks[i][0] and date < weeks[i][1]:
                    word_sums[i] += float(data[dat][0])
                    doc_sums[i] += float(data[dat][2])
                    lex_sums[i] += float(data[dat][1])
                    break
                
        
    if(rolling == False):
        perc_safe = lex_sums/np.where(word_sums > 1, word_sums, 1)
        percentages = np.where(word_sums == 0, None, perc_safe)

        all_perc = list(percentages)
        #years = years[np.argsort(years)]
    else:
        if not diff:
            rlex_sums = np.zeros(len(dates)-(roll-1))
            rword_sums = np.zeros(len(dates)-(roll-1))
            for k in range(0, roll):
                rlex_sums += lex_sums[k:(len(lex_sums)-roll+k+1)]
                rword_sums += word_sums[k:(len(lex_sums)-roll+k+1)]
            dates = dates[roll:]

            perc_safe = rlex_sums/np.where(rword_sums > 1, rword_sums, 1)
            percentages = np.where(rword_sums == 0, None, perc_safe)
            all_perc = list(percentages)
            
        else:
            roll1 = roll[0]
            roll2 = roll[1]
            
            rlex_sums1 = np.zeros(len(dates)-(roll2-1))
            rword_sums1 = np.zeros(len(dates)-(roll2-1))
            
            rlex_sums2 = np.zeros(len(dates)-(roll2-1))
            rword_sums2 = np.zeros(len(dates)-(roll2-1))
            
            for k in range(0, roll1):
                rlex_sums1 += lex_sums[k+roll2-roll1:(len(lex_sums)-roll1+k+1)]
                rword_sums1 += word_sums[k+roll2-roll1:(len(lex_sums)-roll1+k+1)]
            
            for k in range(0, roll2):
                rlex_sums2 += lex_sums[k:(len(lex_sums)-roll2+k+1)]
                rword_sums2 += word_sums[k:(len(lex_sums)-roll2+k+1)]
            
            perc_safe1 = rlex_sums1/np.where(rword_sums1 > 1, rword_sums1, 1)
            perc_safe2 = rlex_sums2/np.where(rword_sums2 > 1, rword_sums2, 1)
            
            percentages = np.where((rword_sums1 == 0) | (rword_sums2 == 0) | (rlex_sums2 == 0), None, perc_safe1/perc_safe2)
            
            all_perc = list(percentages)
            
            dates = dates[roll2:]
            
            
    if ret_tot:
        data_alex = np.zeros((len(dates),7)).astype('object')
    else:
        data_alex = np.zeros((len(dates),4)).astype('object')

    for i in range(0, data_alex.shape[0]):
        data_alex[i][1] = dates[i]
        data_alex[i][2] = delta_date(st, dates[i])
        data_alex[i][0] = all_perc[i]
        if(subs):
            data_alex[i][3] = rolls[i//len(weeks)]
        else:
            data_alex[i][3] = "NA"
        
        if ret_tot:
            data_alex[i][4] = lex_sums[i]
            data_alex[i][5] = word_sums[i]
            data_alex[i][6] = doc_sums[i]

    return data_alex

def aggregate(  
        input_path,
        output_folder,
        output_name,
        week_range, 
        day_offset = 0, 
        gap = 7, 
        gap_type = 'days',
        is_dir = True,
        mod_type = None,
        roll=7, 
        diff = False,
        ind_i = None,
        ret_tot = False
    ):
    data = get_date_sum(input_path, week_range, day_offset, gap, gap_type, is_dir, mod_type, roll, diff, ind_i, ret_tot)
    cols = []
    if(ret_tot):
        df = pd.DataFrame(data, columns = ['Date', 'Raw Day', 'Percent', 'Label', 'Lexicon Count', 'Word Count', 'Document Count'])
    else:
        df = pd.DataFrame(data, columns = ['Date', 'Raw Day', 'Percent', 'Label'])
    
    df_c2 = df.drop_duplicates(subset=['Raw Day', 'Label'], keep='last')
    df_complete_sort = df_c2.sort_values(by=['Date'], kind='mergesort')
    df = df_complete_sort.sort_values(by=['Label'], kind='mergesort')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    df.to_csv(output_folder+'/'+output_name, index=False)
    return