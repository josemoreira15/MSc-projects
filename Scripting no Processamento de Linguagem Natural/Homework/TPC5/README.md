**Problema**

Apresentação dos diferentes *tokens* de um texto, juntamente com a sua POS (*part of speech*) e o seu *lemma*.

**Solução**

A solução abordada passa pelas seguintes etapas:
* criação da variável **nlp = spacy.load('pt_core_news_lg')**
* utilização da variável no texto de *input*, criando a variável *doc*
* utilização da função *retokenizer*, para dar *merge* das entidades
* *print* do conteúdo
