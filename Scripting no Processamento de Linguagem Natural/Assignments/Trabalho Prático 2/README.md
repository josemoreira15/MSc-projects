# Relatório de Projeto - gchatdz, Scripting no Processamento de Linguagem Natural (2023/2024)
## Mestrado em Engenharia Informática
## Projeto desenvolvido por:
* Duarte Parente (PG53791)
* Gonçalo Pereira (PG53834)
* José de Matos Moreira (PG53963)

## Introdução
O presente relatório visa apresentar, de forma resumida, a ferramenta **gchatdz**, um *chatbot* que tem como base de conhecimento o **Diário da República**.
Deste modo, apresentam-se os diversos testes efetuados relativos à utilização de diferentes modelos e de diferentes algoritmos (*word embedding* e *tf-idf*).



## Resultados dos testes
Neste capítulo, apresentam-se os resultados com diferente número de textos mais relevantes e para três diferentes modelos. Os modelos são os seguintes:
    
+ mrm8488/bert-base-portuguese-cased-finetuned-squad-v1-pt
+ lfcc/bert-portuguese-squad
+ eraldoluis/faquad-bert-base-portuguese-cased

Acrescenta-se que o "Caso 1" refere-se à execução do programa recorrendo a *word embedding*, enquanto que o "Caso 2" se relaciona com o mecanismo *tf-idf*.

### Teste 1

**Parágrafo**

> Manda o Governo da República Portuguesa, pelo Ministro da Educação e  Investigação Científica, sob parecer da 4.ª Subsecção da 2.ª Secção da Junta  Nacional da Educação, que, de harmonia com a alínea f) do n.º 2 do § 1.º do  artigo 19.º do regimento da mesma Junta, aprovado pelo Decreto n.º 46349, de  22 de Maio de 1965, seja fixado, conforme planta anexa a esta portaria, o  perímetro de protecção e zona vedada à construção da **ponte sobre o rio Lima,  em Ponte de Lima, classificada como monumento nacional pelo Decreto de 16 de  Junho de 1910.**

**Pergunta**

> Como é que o decreto de 16 de junho de 1910 classifica a ponte sobre o rio Lima?

**Resultados com os 100 textos mais relevantes**

+ Caso 1

| Modelo   | Resposta            | 
|----------|---------------------|
|  <div align="center">0</div> | Cabo Ruivo          | 
| <div align="center">1</div> | monumento nacional  |
| <div align="center">2</div> | monumento nacional  |


+ Caso 2

| Modelo   | Resposta            | 
|----------|---------------------|
| <div align="center">0</div> | monumento nacional          |
| <div align="center">1</div> | monumento de interesse público  | 
| <div align="center">2</div> | monumento nacional  |

**Resultados com os 10 textos mais relevantes**

+ Caso 1

| Modelo   | Resposta            |
|----------|---------------------|
|  <div align="center">0</div> | monumento nacional         |
| <div align="center">1</div> | monumento nacional  |
| <div align="center">2</div> | monumento nacional  | 

+ Caso 2

| Modelo   | Resposta            |
|----------|---------------------|
| <div align="center">0</div> | monumento nacional          |
| <div align="center">1</div> | monumento de interesse público  | 
| <div align="center">2</div> | monumento nacional  |


### Teste 2

**Parágrafo**

> Por ordem superior se torna público que **em 2 de Outubro de 1981 o Governo da  Itália depositou, junto do Ministério dos Negócios Estrangeiros dos Países  Baixos, o instrumento de ratificação da Convenção sobre o Reconhecimento e a  Execução de Decisões Relativas às Obrigações Alimentares,** concluída na Haia em  2 de Outubro de 1973, com a reserva seguinte:

**Pergunta**

>A 2 de Outubro de 1981, o Governo da  Itália, junto do Ministério dos Negócios Estrangeiros dos Países  Baixos, depositou o quê?

**Resultados com os 100 textos mais relevantes**

+ Caso 1

| Modelo   | Resposta            | 
|----------|---------------------|
| <div align="center">0</div> | instrumento de  ratificação |
| <div align="center">1</div> | o seu instrumento de adesão à referida Convenção  | 
| <div align="center">2</div> | instrumento de ratificação  |

+ Caso 2

| Modelo   | Resposta            | 
|----------|---------------------|
| <div align="center">0</div> | instrumento  de adesão |
| <div align="center">1</div> | o seu instrumento de adesão à mesma  Convenção  | 
| <div align="center">2</div> | Convenção sobre o Reconhecimento de Divórcios e Separações  |

**Resultados com os 10 textos mais relevantes**

+ Caso 1

| Modelo   | Resposta            | 
|----------|---------------------|
| <div align="center">0</div> | seu instrumento de adesão à referida Convenção. |
| <div align="center">1</div> | o seu instrumento de adesão à referida Convenção  | 
| <div align="center">2</div> | instrumento de adesão à referida Convenção  |

+ Caso 2

| Modelo   | Resposta            |
|----------|---------------------|
| <div align="center">0</div> | instrumento de  ratificação | 
| <div align="center">1</div> | o seu instrumento de ratificação  daquela Convenção  | 
| <div align="center">2</div> | instrumento de  ratificação  |

### Teste 3

**Parágrafo**

> Em cumprimento do disposto no n.º 4 do artigo 23.º da Lei n.º 28/82, de 15 de  Novembro, declara-se que o conselheiro Joaquim Jorge de Pinho Campinos  apresentou, em 12 de Agosto de 1985, declaração escrita de renúncia das suas  funções de juiz do Tribunal Constitucional, a qual não depende de aceitação e  **implica a cessação imediata de funções.**

**Pergunta**

> O que implica a declaração que o conselheiro Joaquim Jorge de Pinho Campinos  apresentou, em 12 de Agosto de 1985?

**Resultados com os 100 textos mais relevantes**

+ Caso 1

| Modelo   | Resposta            |
|----------|---------------------|
| <div align="center">0</div> | declaração de renúncia | 
| <div align="center">1</div> | cessação imediata de funções  | 
| <div align="center">2</div> | declaração escrita de renúncia das suas  funções de juiz do Tribunal Constitucional  |

+ Caso 2

| Modelo   | Resposta            |
|----------|---------------------|
| <div align="center">0</div> | declaração de renúncia | 
| <div align="center">1</div> | renúncia às funções de juiz  do Tribunal Constitucional  | 
| <div align="center">2</div> | renúncia das suas  funções de juiz do Tribunal Constitucional  |

**Resultados com os 10 textos mais relevantes**

+ Caso 1

| Modelo   | Resposta            |
|----------|---------------------|
| <div align="center">0</div> | Decreto do Presidente da República | 
| <div align="center">1</div> | situação de disponibilidade  | 
| <div align="center">2</div> | inexactidão  |

+ Caso 2

| Modelo   | Resposta            |
|----------|---------------------|
| <div align="center">0</div> | cessação imediata de funções | 
| <div align="center">1</div> | renúncia às suas funções de juiz do Tribunal Constitucional  | 
| <div align="center">2</div> | renúncia das suas  funções de juiz do Tribunal Constitucional  |
