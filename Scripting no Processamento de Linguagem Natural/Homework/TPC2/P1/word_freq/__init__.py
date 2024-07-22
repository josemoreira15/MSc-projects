#!/usr/bin/python3
'''
NAME
   word_freq - calculates word frequency in a text

SYNOPSIS
   word_freq [options] input_file
    options:
        -b S : shows the words whose initial is in the string S (in descending order by value)
        -c   : compares the frequencies with the database file (in descending order by ratio)
        -i   : case insensitive (shows the result in upper case and in descending order by value)
        -l N : shows the words which length equals to N (in descending order by value)
        -m N : shows the N most common words (in descending order by value)
        -n   : orders alfabetically
        -p   : case insensitive (prints the most frequent between words that share the same upper word and sums all their occurrences)
        -s S : shows the words that have S as a substring (in descending order by value)
        no option : sorts descending by value

DESCRIPTION

FILES
    database.txt : https://www.linguateca.pt/acesso/tokens/formas.totalpt.txt
'''

from jjcli import *
from collections import Counter
import re

__version__ = "0.0.1"


def tokenizer(content):
    tokens = re.findall(r'\w+(?:\-\w+)?|[,.;:?—!_]+', content)
    return tokens

def beaut_print(content):
    count = 0
    for key, value in content:
        space = (20 - len(key)) * ' '
        print(f'{key}{space}{value}')
        count += value  

def smart_case_insensitive(content):
    sci = dict()
    md = dict()

    for key, value in content:
        up = key.upper()
        if up not in md:
            sci[key] = value
            md[up] = key
        else:
            if value > sci[md[up]]:
                sum = value + sci[md[up]]
                sci[key] = sum
                sci.pop(md[up])
            else:
                sci[md[up]] += value

    return sci
            
def case_insensitive(content):
    ci = dict()
    for key, value in content:
        up = key.upper()
        if up not in ci:
            ci[up] = 0
        ci[up] += value
    
    return ci

def equal_len_keys(content, size):
    sd = dict()
    for key, value in content:
        if len(key) == size:
            sd[key] = value
    
    return sd

def starter_char(content, string):
    scd = dict()
    for key, value in content:
        if key[0] in string:
            scd[key] = value
    
    return scd

def sub(content, ss):
    ssd = dict()
    for key, value in content:
        if ss in key:
            ssd[key] = value
    
    return ssd

def database_comparison(content):
    db_dict = dict()
    counter = 0
    cd = dict()

    with open('tests/database.txt', 'r', encoding='iso-8859-1') as database_file:
        for line in database_file:
            split = re.split(r'[\s\t]+', line, maxsplit=1)
            db_dict[split[1][:-1]] = int(split[0])
            counter += int(split[0])
    
    occ_sum = sum(occ for _, occ in content)
    
    for key, value in content:
        if key in db_dict:
            ratio = (value/occ_sum) / (db_dict[key]/counter)
        else:
            ratio = (value/occ_sum) / (1/counter)
        cd[key] = round(ratio, 4)

    return cd

def main():
    cl = clfilter("b:cil:m:nps:", doc=__doc__)

    for txt in cl.text():
        tokens = tokenizer(txt)
        count = Counter(tokens)

        if '-b' in cl.opt:
            scd = starter_char(count.items(), cl.opt.get('-b'))
            beaut_print(sorted(scd.items(), key=lambda x: x[1], reverse=True))
        if '-c' in cl.opt:
            cd = database_comparison(count.items())
            beaut_print(sorted(cd.items(), key=lambda x: x[1], reverse=True))
        elif '-i' in cl.opt:
            ci = case_insensitive(count.items())
            beaut_print(sorted(ci.items(), key=lambda x: x[1], reverse=True))
        elif '-l' in cl.opt:
            ed = equal_len_keys(count.items(), int(cl.opt.get('-l')))
            beaut_print(sorted(ed.items(), key=lambda x: x[1], reverse=True))
        elif '-m' in cl.opt:
            beaut_print(count.most_common(int(cl.opt.get('-m'))))
        elif '-n' in cl.opt:
            beaut_print(sorted(count.items()))
        elif '-p' in cl.opt:
            sci = smart_case_insensitive(count.items())
            beaut_print(sorted(sci.items(), key=lambda x: x[1], reverse=True))
        elif '-s' in cl.opt:
            ssd = sub(count.items(), cl.opt.get('-s'))
            beaut_print(sorted(ssd.items(), key=lambda x: x[1], reverse=True))
        else:
            beaut_print(sorted(count.items(), key=lambda x: x[1], reverse=True))