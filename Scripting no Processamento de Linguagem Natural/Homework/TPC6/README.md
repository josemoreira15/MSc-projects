**Problema**

Calcular as "amizades", a partir de um texto. Com "amizades", quer-se dizer o número de ocorrências que dois nomes próprios ocorrem na mesma frase.

**Solução**

Para se conseguir resolver o problema proposto, começou-se por criar uma variável, do tipo *dict*, responsável por armazenar todos os pares de "amizades". Posteriormente, dentro do ciclo da função que percorre as *sentences* do *doc*, dentro da condição que verifica se o *token* é um nome próprio (**PROPN**), fez-se o seguinte:
* criação de uma variável, lista, com a capacidade de guardar todos os nomes próprios já encontrados na *sentence* (sem repetições);
* aquando a iteração sob outro nome próprio, verificar, para cada par (elemento da lista, nome próprio) já existe no dicionário (ou com a ordem trocada (nome próprio, elemento da lista));
* em caso negativo, criar essa nova chave, (elemento da lista, nome próprio), com o valor a 0;
* incrementar o valor em uma unidade.

Para efeito de testes, recorreu-se ao ficheiro [HP.txt](https://github.com/josemoreira15/SPLN2324/blob/main/TPC6/HP.txt), disponibilizado pela equipa docente.