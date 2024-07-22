**Problema**

Recorrendo às bibliotecas *jjcli*, *collections* e *re*, o objetivo prendia-se em elaborar um programa que conseguisse apresentar o número de ocorrências das palavras num texto, podendo, também, obter essas mesmas palavras a partir de queries: ordenadas decrescentemente, obtidas através de case insensitive, etc.

**Solução**

Em primeiro lugar, de modo a conseguir-se capturar as várias palavras de um texto, elaborou-se a função *tokenizer* que, recorrendo ao *re*, consegue identificar as várias palavras de um texto. Posteriormente, desenvolveu-se a função *beaut_print*, responsável por imprimir, com uma identação correta, o resultado final.
Como referido, o programa aceita, pela linha de comandos, diferentes opções, sendo as mesmas:
* -b S  : mostra as palavras cuja inicial pertence à string S (exemplo: se S for igual a "abc", serão mostradas todas as palavras que comecem por a, b ou c), ordenadas decrescentemente pelo número de occorências
* -i    : case insensitive, ou seja, agrupa as palavras que são escritas com as mesmas letras, mesmo que estejam em maiúscula e minúscula (exemplo: sim e Sim são contabilizadas como a mesma palavra), mostrando o resultado em letra maiúscula, ordenadas decrescentemente pelo número de ocorrências
* -l N  : mostra as palavras cujo comprimento seja igual a N (exemplo: para N igual a 3, são apresentadas todas as palavras que tenham exatamente 3 caracteres), ordenadas decrescentemente por valor
* -m N  : mostra as N palavras com mais ocorrências (exemplo: para N igual a 10, são apresentadas as 10 palavras com maior número de ocorrências), ordenadas decrescentemente pelo número de ocorrências
* -n    : apresenta todas as palavras do texto ordenadas alfabeticamente
* -s S  : imprime todas as palavras que possuem a substring S (exemplo: para S igual a "si", seriam impressas (caso existissem no texto) as palavras: assim, sim, sinal, etc.), ordenadas decrescentemente pelo número de ocorrências
* no option : mostra todas as palavras do texto ordenadas de forma decrescente pelo respetivo número de ocorrências

De modo a oferecer alguma vantagem a nível informativo, no fim do resultado é mostrada uma mensagem a contabilizar o número total de palavras contabilizadas pela opção selecionada (quando selecionada) e o número de ocorrências somado das mesmas.

Deste modo, foram escritas as funções auxiliares *case_insensitive*, *equal_len_keys*, *starter_char* e *sub* de forma a ajudarem na resolução do problema. Para efeito de testes, recorreu-se ao ficheiro [Camilo-Amor_de_Perdicao](https://github.com/josemoreira15/SPLN2324/blob/main/TPC1/Camilo-Amor_de_Perdicao.md), disponibilizado pela equipa docente.