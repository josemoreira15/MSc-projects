#!/usr/bin/python3
'''
NAME
   word_freq - calculates word frequency in a text

SYNOPSIS
   word_freq [options] input_file
   
Description

    options:
        -b S : shows the words whose initial is in the string S (in descending order by value)
        -i   : case insensitive (shows the result in upper case and in descending order by value)
        -l N : shows the words which length equals to N (in descending order by value)
        -m N : shows the N most common words (in descending order by value)
        -n   : orders alfabetically
        -s S : shows the words that have S as a substring (in descending order by value)
        
        no option : sorts descending by value
'''

from jjcli import *
from collections import Counter
import re

cl = clfilter("b:il:m:ns:", doc=__doc__)

def tokenizer(content):
    tokens = re.findall(r'\w+(?:\-\w+)?|[,.;:?—!_]+', content)
    return tokens

def beaut_print(content):
    count = 0
    for key, value in content:
        space = (20 - len(key)) * ' '
        print(f'{key}{space}{value}')
        count += value
    
    print(f'««« There are {len(content)} different words, totalizing {count} occurences »»»')

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


for txt in cl.text():
    tokens = tokenizer(txt)
    count = Counter(tokens)

    if '-b' in cl.opt:
        scd = starter_char(count.items(), cl.opt.get('-b'))
        beaut_print(sorted(scd.items(), key=lambda x: x[1], reverse=True))
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
    elif '-s' in cl.opt:
        ssd = sub(count.items(), cl.opt.get('-s'))
        beaut_print(sorted(ssd.items(), key=lambda x: x[1], reverse=True))
    else:
        beaut_print(sorted(count.items(), key=lambda x: x[1], reverse=True))
