#!/usr/bin/python3
'''
NAME
    gsadz - Portuguese Sentiment Analysis module

SYNOPSIS
    gsadz [OPTION]...

DESCRIPTION
    Module of Portuguese Sentiment Analysis that calculates the sentiment polarity and the frequency of words, puncts, boosters, deniers, positive tokens, negative tokens
    and neutral tokens of a given input.

    With no OPTION, reads from standard input.

    -f file     Analyzes the file's content
'''

from .parse_data import SentilexData
from jjcli import *
import spacy, os

__version__ = "0.0.1"

PACKAGE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
POS = {
    'NOUN': 'N',
    'VERB': 'V',
    'ADJ': 'Adj'
}
BOOSTERS = {
    'incr': 1.25,
    'decr': 0.75
}
SUBJECT_DEP = ["nsubj", "nsubjpass","csubj", "csubjpass", "nmod", "appos", "acl", "acl:relcl"]
OBJECT_DEP = ["ROOT", "obj", "pobj", "dobj", "oprd", "ccomp", "xcomp", "obl"]




class SentimentAnalysis:
    
    def __init__(self, p_weight=1, n_weight=1):
        self.sentilexdata = SentilexData(PACKAGE_DIRECTORY)
        self.sentilexdata.read_sentilex()
        self.nlp = spacy.load("pt_core_news_lg")
        self.nlp.add_pipe("merge_entities")
        self.booster = 1
        self.negate = 1
        self.p_weight = p_weight
        self.n_weight = n_weight

    
    def reset_scores(self):
        self.booster = 1
        self.negate = 1

    
    def split_by_groups(self, sentence, n):
        sets = []

        for i in range(n, 1, -1):
            for j in range(len(sentence) - i + 1):
                subset = sentence[j : j + i]
                sets.append((subset, j, len(subset)))

        return sets, [(token, index) for index, token in enumerate(sentence)]


    def closer_value(self, values, avg):
        result = (0, 5)
        for value in values:
            temp = abs(avg - value)
            if temp < result[1]:
                result = (value, temp)

        return result[0]
    

    def pre_analysis(self, sentence):
        sets, ones = self.split_by_groups(sentence, 8)

        result = []
        types = []

        for set in sets:
            set_flag = False
            magic = None
            text = set[0].text.lower()

            if text in self.sentilexdata.flex:
                magic = list(self.sentilexdata.flex[text][0]["POL"].values())[0]
                set_flag = True
            
            elif text in self.sentilexdata.lemma:
                magic = list(self.sentilexdata.lemma[text][0]["POL"].values())[0]
                set_flag = True

            elif text in self.sentilexdata.boosters:
                magic = self.sentilexdata.boosters[text].lower()
                set_flag = True

            elif text in self.sentilexdata.negate:
                magic = 'neg'
                set_flag = True

            if set_flag:
                indexes = [index for index in range(set[1], set[1] + set[2])]

                if not any(any(index in subresult for index in indexes) for subresult in result):
                    result.append(indexes)
                    types.append(magic)

        for one in ones:
            one_flag = False
            magic = None
            text = one[0].text.lower()

            if text in self.sentilexdata.boosters:
                one_flag = True
                magic = self.sentilexdata.boosters[text].lower()

            elif text in self.sentilexdata.negate:
                one_flag = True
                magic = 'neg'

            if one_flag:
                if not any(one[1] in subresult for subresult in result):
                    result.append([one[1]])
                    types.append(magic)

        return list(zip(result, types))
    

    def find_special(self, ind_types, index):
        for i in range (0, len(ind_types)):
            if index in ind_types[i][0]:
                return ind_types[i][1], ind_types[i][0].index(index)

        return None 
            
 
    def polarity_result(self, input):
        doc = self.nlp(input)

        counters = {
            'n_tokens': 0,
            'n_boosters': 0,
            'n_negates': 0,
            'n_positives': 0,
            'n_negatives': 0,
            'n_neutrals': 0,
            'n_puncts': 0
        }

        scores = []

        for sentence in doc.sents:
            counters['n_tokens'] += len(sentence)
            ind_types = self.pre_analysis(sentence)
            sentence_score = 0
            sentence_scores = []
            pending_scores = []
            token_counter = -1

            for token in sentence:
                token_counter += 1

                score = 0
                entry = None

                if token.is_punct:
                    counters['n_puncts'] += 1
                    continue

                special = self.find_special(ind_types, token_counter)
                
                if special != None:
                    if special[1] > 0:
                        continue

                    else:
                        if special[0] in ['incr', 'decr']:
                            self.booster *= BOOSTERS[special[0]]
                            counters['n_boosters'] += 1
                            continue
                            

                        elif special[0] == 'neg':
                            self.negate = -1
                            counters['n_negates'] += 1
                            continue

                        else:
                            polarity = int(special[0])
                            counters['n_positives'], counters['n_negatives'], counters['n_neutrals'], polarity = (counters['n_positives'] + 1, counters['n_negatives'], counters['n_neutrals'], polarity * self.p_weight) if polarity > 0 \
                                                                                                      else (counters['n_positives'], counters['n_negatives'] + 1, counters['n_neutrals'], polarity * self.n_weight) if polarity < 0 \
                                                                                                      else (counters['n_positives'], counters['n_negatives'], counters['n_neutrals'] + 1, polarity)
                            sentence_scores.append(polarity * self.booster * self.negate) 
                            self.reset_scores()
                            continue


                if str(token).lower() in self.sentilexdata.flex:
                    entry = self.sentilexdata.flex[str(token).lower()]

                elif token.lemma_.lower() in self.sentilexdata.lemma:
                    entry = self.sentilexdata.lemma[token.lemma_.lower()]

                if entry != None:

                    for elem in entry:
                        if elem['PoS'] == POS.get(token.pos_, ""):  

                            if len(list(elem['POL'].values())) == 1:
                                polarity = int(list(elem['POL'].values())[0])
                                counters['n_positives'], counters['n_negatives'], counters['n_neutrals'], polarity = (counters['n_positives'] + 1, counters['n_negatives'], counters['n_neutrals'], polarity * self.p_weight) if polarity > 0 \
                                                                                                      else (counters['n_positives'], counters['n_negatives'] + 1, counters['n_neutrals'], polarity * self.n_weight) if polarity < 0 \
                                                                                                      else (counters['n_positives'], counters['n_negatives'], counters['n_neutrals'] + 1, polarity)
                                sentence_scores.append(polarity * self.booster * self.negate)

                            else:
                                if token.dep_ in OBJECT_DEP or token.head.dep_ in OBJECT_DEP:
                                    polarity = int(elem['POL']["N1"])
                                    counters['n_positives'], counters['n_negatives'], counters['n_neutrals'], polarity = (counters['n_positives'] + 1, counters['n_negatives'], counters['n_neutrals'], polarity * self.p_weight) if polarity > 0 \
                                                                                                      else (counters['n_positives'], counters['n_negatives'] + 1, counters['n_neutrals'], polarity * self.n_weight) if polarity < 0 \
                                                                                                      else (counters['n_positives'], counters['n_negatives'], counters['n_neutrals'] + 1, polarity)
                                    sentence_scores.append(polarity * self.booster * self.negate)
                                elif token.dep_ in SUBJECT_DEP or token.head.dep_ in SUBJECT_DEP:
                                    polarity = int(elem['POL']["N1"])
                                    counters['n_positives'], counters['n_negatives'], counters['n_neutrals'], polarity = (counters['n_positives'] + 1, counters['n_negatives'], counters['n_neutrals'], polarity * self.p_weight) if polarity > 0 \
                                                                                                      else (counters['n_positives'], counters['n_negatives'] + 1, counters['n_neutrals'], polarity * self.n_weight) if polarity < 0 \
                                                                                                      else (counters['n_positives'], counters['n_negatives'], counters['n_neutrals'] + 1, polarity)
                                    sentence_scores.append(polarity * self.booster * self.negate)           
                                else:
                                    token_scores = [int(value) * self.booster * self.negate for value in list(elem['POL'].values())]
                                    token_scores += [sum(token_scores) / len(token_scores)]
                                    pending_scores.append((token_scores, self.negate))

                            break

                self.reset_scores()
                    

            if len(sentence_scores) > 0:
                sentence_score = sum(sentence_scores) / len(sentence_scores)
                
            for pending in pending_scores:
                closer = self.closer_value(pending[0], score)
                counters['n_positives'], counters['n_negatives'], counters['n_neutrals'], closer = (counters['n_positives'] + 1, counters['n_negatives'], counters['n_neutrals'], closer * self.p_weight) if (closer > 0 and pending[1] == 1) or (closer < 0 and pending[1] == -1)\
                                                                                                                          else (counters['n_positives'], counters['n_negatives'] + 1, counters['n_neutrals'], closer * self.n_weight) if (closer > 0 and pending[1] == -1) or (score < 0 and pending[1] == 1)\
                                                                                                                          else (counters['n_positives'], counters['n_negatives'], counters['n_neutrals'] + 1, closer)
                sentence_scores.append(closer)

            if len(sentence_scores) > 0:
                sentence_score = sum(sentence_scores) / len(sentence_scores)
            
            scores.append(sentence_score)
        

        result = {
            'Polarity': sum(scores) / len(scores),
            'Words': counters['n_tokens'] - counters['n_puncts'],
            'Puncts': counters['n_puncts'],
            'Boosters': counters['n_boosters'],
            'Deniers': counters['n_negates'],
            'Positives': counters['n_positives'],
            'Negatives': counters['n_negatives'],
            'Neutrals': counters['n_neutrals']
        }   

        return result



def main():
    sa = SentimentAnalysis()

    cl = clfilter("f:", doc=__doc__)
    if '-f' in cl.opt:
        with open(cl.opt.get('-f')) as file:
            content = file.read()
    else:
        content = input()
    
    analysis = sa.polarity_result(content)
    print(analysis)


if __name__ == "__main__":
    main()