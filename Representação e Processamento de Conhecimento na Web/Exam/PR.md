# RPCW2024-Recurso

## Exercício 1
Para conseguir representar a história presente no exercício 1, desenvolvi o seguinte:

### Classes
* Universidade
* Escola
* Curso
* Pessoa
    * Aluno
    * Professor
* Lingua


### Object Properties
* aprendeCurso
* estudaEm
* falaLingua
* temAmigo
* temDocente
* temEscola
* temProfessor


### Data Properties
* horario
* idade
* local
* nasceu


Com isto, foi possível reunir a máxima informação recolhida e responder às queries presentes no ficheiro **queries.txt**, na pasta **ex1**.



## Exercício 2
A execução deste exercício foi dividida em três fases distintas (para além da criação da ontologia):

### Limpeza do dataset
A limpeza do ficheiro de entrada foi feita recorrendo a um script, **clean_script**, onde as diversas estruturas que deveriam estar representadas em formato de lista, estavam em formato string.


### Produção da ontologia
Recorrendo ao **ttl_script**, consegui povoar a ontologia. Para isso, recorri a uma função de criação de ids responsável por substituir os caracteres não alfanuméricos por alfanuméricos, de modo a criar URIs legíveis e aceites. Enquanto percorria os livros, adicionava as suas *data properties* e criava entidades de autores, personagens, editoras (que publicam), locais (setting), géneros e prémios. Tudo isto foi feito recorrendo à estrutura *set()* de modo a evitar as repetições e a futura criação errada. Com isto, foram respondidas as primeiras *queries*.


### Produção do ficheiro com coautores
Após colocar a query *construct* no **GraphDB**, fiz *download* dos triplos e adicionei os mesmos ao ficheiro **books_coauthors.ttl*, adicionando a propriedade de coautor. Com isto, consegui responder à última query.