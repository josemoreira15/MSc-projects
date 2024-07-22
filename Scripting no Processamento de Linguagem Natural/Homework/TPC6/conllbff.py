#!/usr/bin/env python3

import spacy, sys
# from spacy import displacy

with open(sys.argv[1]) as file:
    content = file.read()

nlp = spacy.load("pt_core_news_lg")

doc = nlp(content)
# displacy.serve(doc, style='dep')

with doc.retokenize() as retokenizer:
    for entity in doc.ents:
        retokenizer.merge(entity)

bffs = dict()
    
print("TOKEN   POS   LEMMA   DEP")
print('-' * 25)
for sentence in doc.sents:
    person_list = []
    for token in sentence:
        if token.is_space:
            continue
        if token.pos_ == 'PROPN':
            this_person = str(token)

            print(f"{this_person}   {token.pos_}   {token.ent_type_}   {token.dep_}")

            for person in person_list:
                if person != this_person:
                    flag_added = False
                    if (person, this_person) not in bffs:
                        if (this_person, person) in bffs:
                            bffs[(this_person, person)] += 1
                            flag_added = True
                        else:
                            bffs[(person, this_person)] = 0

                    if not flag_added:
                        bffs[(person, this_person)] += 1

            if this_person not in person_list:
                person_list.append(this_person)

        else:
            print(f"{str(token)}   {token.pos_}   {token.lemma_}   {token.dep_}")

    print()

# dicionário com o número de ocorrências das "amizades"
sorted_dict = dict(sorted(bffs.items(), key=lambda item: item[1], reverse=True))
# for key in sorted_dict:
#     print(f'{key}: {sorted_dict[key]}')