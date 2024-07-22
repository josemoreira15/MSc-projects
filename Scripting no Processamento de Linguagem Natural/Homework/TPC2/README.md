**Problema**

Complementando o programa desenvolvido até à data, *wfreq*, pretendia-se fazer a comparação e o respetivo estudo entre número de ocorrências de uma palavra num texto, passado como _input_ e uma tabela de frequências da língua portuguesa.

**Solução**

Deste modo, procedeu-se, inicialmente, ao _download_ de uma tabela de frequências da língua portuguesa, recorrendo ao *Linguateca*. Posteriormente, desenvolveu-se uma função, *database_comparison*, responsável pelos seguintes passos:
* carregar o ficheiro de frequências da língua portuguesa, guardando-o num dicionário (palavra -> número de ocorrências da palavra)
* calcular, para cada palavra presente no texto _input_, a frequência de ocorrências nesse mesmo texto, dividida pela frequência de ocorrências na tabela
* guardar esse mesmo resultado num dicionário

Apesar de ter surgido o problema de nem todas as palvras se encontrarem na tabela de frequências, decidiu-se resolver o mesmo, fazendo os cálculos normalmente, atribuindo o valor 1 para o número de ocorrências da mesma na tabela, ou seja, "simulando" que essa palavra se encontra exatamente uma vez na tabela. Deste modo, conseguiu-se perceber e comparar a diferença de ocorrências (em proporção) entre o "nosso" texto e a língua portuguesa. Para efeito de testes, recorreu-se ao ficheiro [Camilo-Amor_de_Perdicao](https://github.com/josemoreira15/SPLN2324/blob/main/TPC1/Camilo-Amor_de_Perdicao.md), disponibilizado pela equipa docente.