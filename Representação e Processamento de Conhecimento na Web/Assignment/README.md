# Relatório de Projeto - gfootdz, Representação e Processamento de Conhecimento na Web (2023/2024)
## Mestrado em Engenharia Informática
## Projeto desenvolvido por:
* Duarte Parente (PG53791)
* Gonçalo Pereira (PG53834)
* José de Matos Moreira (PG53963)

## Resumo
O presente relatório visa descrever detalhadamente a **gfootdz**, uma aplicação web responsável por agregar e apresentar diversa informação e as mais variadas estatísticas sobre a **Liga Portugal Betclic 2023/2024**. Para além disso, a aplicação desenvolvida aufere uma capacidade restrita de manipulação sobre os diversos dados existentes.

## Introdução
O futebol é, sem sombra de dúvida, o desporto mais visto e praticado em Portugal (assim como no resto do mundo), o que leva a que haja uma constante procura pela mais diversa informação acerca do mesmo. Com isto, cresceu a motivação de desenvolver uma aplicação, de utilização simples, capaz de fornecer as mais variadas e precisas estatísticas sobre a **Liga Portugal Betclic**, a principal liga portuguesa de futebol. Deste modo e, restringindo-se ainda mais o espetro da aplicação, decidiu-se, por fim, abordar apenas a informação acerca da edição 2023/2024 da liga anteriormente mencionada. Com isto, projetou-se a **gfootdz**, um *site* intuitivo que se distingue dos outros na medida em que, focando-se apenas numa liga e numa edição específicas, consegue apresentar a sua informação de uma forma muito mais rápida e de acesso muito mais simplificado e direto.

## Dataset
Em relação à recolha dos dados, recorreu-se a **Web Scraping**, uma estratégia simples que permite efetuar uma extração automática de dados de diferentes fontes web. Deste modo, desenvolveram-se *scripts* capazes de recolher informação de duas páginas distintas: [Tranfermarkt](https://www.transfermarkt.pt) e [FBref](https://fbref.com). De modo a complementar a informação recolhida, consultou-se e extraiu-se, manualmente, informação presente em [Liga Portugal](https://ligaportugal.pt).

## Ontologia
Posteriormente, mostrou-se necessário agregar e relacionar toda a informação até ao momento recolhida, de modo a facilitar o seu posterior acesso (por parte da aplicação). Com isto, escreveu-se um novo *script* com a capacidade de consultar os ficheiros anteriormente produzidos e elaborar um novo ficheiro, em formato **.ttl**, possuindo a ontologia que representa as relações entre os diversos dados. Esta mesma ontologia foi posteriormente carregada no **GraphDB**.

### Classes
Aqui, apresentam-se as classes que constituem a ontologia anteriormente referida:
* **Clube** - agrega as informações dos 18 clubes que participam na liga
* **Estádio** - reúne as informações dos estádios de futebol
* **Jogo** - possui as informações detalhadas de cada um dos 306 jogos
* **Liga** - inclui as informações da **Liga Portugal Betclic 2023/2024**
* **Pessoa** - guarda informações gerais sobre as pessoas presentes na ontologia
    * **Jogador** - possui as informações específicas sobre um jogador
        * **GuardaRedes** - guarda as informações detalhadas apenas relativas aos guarda-redes
    * **Treinador** - agrega as informações dos treinadores
    * **Árbitro** - possui as informações relativas aos árbitros

### *Object Properites*
Nesta secção, detalham-se as relações existentes entre as diversas classes anteriormente explicadas:
* **equipaCasa** (**Jogo** -> **Clube**) - associa um jogo à equipa visitada
* **equipaFora** (**Jogo** -> **Clube**) - associa um jogo à equipa visitante
* **joga** (**Jogador** -> **Clube**) - associa um jogador ao clube no qual o mesmo joga
* **temArbitro** (**Jogo** -> **Árbitro**) - associa um jogo ao árbitro que ajuizou o mesmo
* **temEstadio** (**Clube** -> **Estádio**) - associa um clube ao estádio no qual o mesmo disputa os seus jogos
* **treina** (**Treinador** -> **Clube**) - associa um treinador ao clube que o mesmo treina

### *Data Properties*
As *data properties* mostram-se importantes na medida em que agregam a informação, associando uma classe a um valor literal. Apresentam-se, assim, as *data properties* presentes na ontologia:
* **aereosGanhos** - percentagem de lances aéreos ganhos por um **Jogador**
* **alturaJogador** - altura de um **Jogador**
* **amarelosArbitro** - número de cartões amarelos mostrados por um **Árbitro**
* **amarelosEquipa** - número de cartões amarelos mostrados aos jogadores de um **Clube**
* **assistenciasJogador** - número de assistências de um **Jogador**
* **associacaoArbitro** - associação à qual pertence um **Árbitro**
* **autoGolos** - número de autogolos marcados por um **Jogador**
* **bolasRecuperadas** - número de bolas recuperadas por um **Jogador**
* **caJogador** - número de cartões amarelos mostrados a um **Jogador**
* **capacidadeEstadio** - número total de lugares de um **Estádio**
* **cleanSheets** - número de jogos de um **GuardaRedes** sem sofrer golos
* **conducoesProgressivas** - número de conduções progressivas efetuadas por um **Jogador**
* **cortes** - número de cortes de um **Jogador**
* **cortesGanhos** - número de cortes ganhos por um **Jogador**
* **cruzamentos** - número de cruzamentos efetuados por um **Jogador**
* **cvJogador** - número de cartões vermelhos mostrados a um **Jogador**
* **dataJogo** - data na qual foi realizado um **Jogo**
* **dataNascimento** - data de nascimento de uma **Pessoa**
* **derrotasEquipa** - número de derrotas de um **Clube**
* **derrotasTreinador** - número de derrotas de um **Treinador**
* **duelos** - número de duelos de um **Jogador**
* **duelosGanhos** - número de duelos ganhos por um **Jogador**
* **duplosAmarelosArbitro** - número de duplos cartões amarelos mostrados por um **Árbitro**
* **edicao** - edição de uma **Liga**
* **empatesEquipa** - número de empates de um **Clube**
* **empatesTreinador** - número de empates de um **Treinador**
* **espectadores** - número de espectadores de um **Jogo**
* **faltasCometidas** - número de faltas cometidas por um **Jogador**
* **faltasSofridas** - número de faltas sofridas por um **Jogador**
* **forasDeJogo** - número de foras de jogo assinalados a um **Jogador**
* **formacaoCasa** - formação apresentada pela equipa visitada num **Jogo**
* **formacaoFora** - formação apresentada pela equipa visitante num **Jogo**
* **formacaoTreinador** - formação preferida por um **Treinador**
* **fundacaoClube** - data de fundação de um **Clube**
* **gca** - número de ações de criação de golo de um **Jogador**
* **golosEquipa** - número de golos marcados por um **Clube**
* **golosJogador** - número de golos marcados por um **Jogador**
* **golosSofridosEquipa** - número de golos sofridos por um **Clube**
* **golosSofridosGR** - número de golos sofridos por um **GuardaRedes**
* **horaJogo** - hora do pontapé de saída de um **Jogo**
* **intercecoes** - número de interceções efetuadas por um **Jogador**
* **jogosArbitro** - número de jogos ajuizados por um **Árbitro**
* **jogosJogador** - número de jogos jogados por um **Jogador**
* **jornada** - jornada na qual foi disputado um **Jogo**
* **keyPasses** - número de passes chave efetuados por um **Jogador**
* **minutosJogador** - número de minutos jogados por um **Jogador**
* **nacionalidae** - nacionalidade de uma **Pessoa**
* **nomeClube** - nome de um **Clube**
* **nomeCompleto** - nome completo de uma **Pessoa**
* **nomeCompletoClube** - nome completo de um **Clube**
* **nomeEstadio** - nome de um **Estádio**
* **nomeLiga** - nome de uma **Liga**
* **nomePessoa** - nome de uma **Pessoa**
* **numeroEquipas** - número de equipas que disputam uma **Liga**
* **numeroJogador** - número da camisola de um **Jogador**
* **paisLiga** - país organizador de uma **Liga**
* **passesCompletos** - número de passes acertados por um **Jogador**
* **passesProgressivos** - número de passes progressivos de um **Jogador**
* **peJogador** - pé mais utilizado por um **Jogador**
* **penaltisArbitro** - número de penáltis assinalados por um **Árbitro**
* **penaltisContraEquipa** - número de penáltis assinalados contra um **Clube**
* **penaltisContraGR** - número de penáltis tentados contra um **GuardaRedes**
* **penaltisDefendidosGR** - número de penáltis defendidos por um **GuardaRedes**
* **penaltisFavorEquipa** - número de penáltis assinalados a favor de um **Clube**
* **penaltisMarcadosJogador** - número de penáltis marcados por um **Jogador**
* **penaltisTentadosJogador** - número de penáltis executados por um **Jogador**
* **percentagemPasses** - percentagem de passes acertados por um **Jogador**
* **posicaoJogador** - posição em campo de um **Jogador**
* **posseJogo** - posse de bola observada em relação à disputa de um **Jogo**
* **rankingUEFA** - ranking **UEFA** de uma **Liga**
* **rematesBalizaJogador** - número de remates à baliza de um **Jogador**
* **rematesJogaodr** - número de remates de um **Jogador**
* **rematesSofridosGR** - número de remates efetuados contra um **GuardaRedes**
* **resultado** - resultado final de um **Jogo**
* **toques** - número de toques na bola de um **Jogador**
* **valorJogador** - valor de mercado de um **Jogador**
* **vermelhosArbitro** - número de cartões vermelhos mostrados por um **Árbitro**
* **vermelhosEquipa** - número de cartões vermelhos mostrados aos jogadores de um **Clube**
* **vitoriasEquipa** - número de vitórias de um **Clube**
* **vitoriasTreinador** - número de vitórias de um **Treinador**
* **xaJogador** - número de assistências esperadas de um **Jogador**
* **xgCasa** - número de golos esperados da equipa visitada num **Jogo**
* **xgEquipa** - número de golos esperados de um **Clube**
* **xgFora** - número de golos esperados da equipa visitante num **Jogo**
* **xgJogador** - número de golos esperados de um **Jogador**
* **xgSofridosGR** - número de golos sofridos esperados por um **GuardaRedes**

Sendo assim, ontolgia final apresenta um total de **27,265** triplos.

## Aplicação
Relativamente à aplicação, esta foi construída com recurso à framework *Flask*, conhecida pela sua simplicidade e flexibilidade, tornando a implementação mais rápida e fácil. A aplicação é composta por três componentes principais: autenticação (auth), API e interface do utilizador.

### Autenticação
No que toca ao módulo da autenticação, não é permitida e criação de contas de utilizador, apenas existem já as 3 contas de administrador pré-definidas, representando cada elemento do grupo. As informações das contas são guardadas num ficheiro *json*, na diretoria *users*. As rotas definidas neste módulo são as seguintes:

* **POST /entrar** - esta rota está associada a uma função que tem como objetivo a realização do *login*, por parte de um administrador, no qual o utilizador introduz o nome de utilizador e a *password*

* **POST /sair** - a função associada a esta rota serve para efetuar o *logout* de um utilizador

### API
De forma a estabelecer uma comunicação entre os dados e a *frontend*, foi codificada a API. Esta implementa a funcionalidade de operações CRUD (criar, ler, atualizar e apagar). As rotas definidas na API são as seguintes:


* **GET /clubes/\<id>** - retorna as informações relativas a um determinado clube
* **GET /arbitros** - retorna a lista de árbitros
* **GET /arbitros/\<idArbitro>** - retorna as informações relativas a um determinado árbitro
* **GET /jogadores** - retorna a lista de jogadores
* **GET /jogadores/\<idJogador>** - retorna as informações relativas a um determinado jogador
* **GET /treinadores** - retorna a lista de treinadores
* **GET /treinadores/\<idTreinador>** - retorna as informações relativas a um determinado treinador
* **GET /lideres** - retorna todos os top 10 relativos a todos os parâmetros estatísticos de comparação defenidos 


* **POST /adicionar_jogador** - encarregue de tratar de toda a lógica associada ao registo de um novo jogador
* **POST /adicionar_treinador** - encarregue de tratar de toda a lógica associada ao registo de um novo treinador
* **POST /adicionar_arbitro** - encarregue de tratar de toda a lógica associada ao registo de um novo árbitro


* **DELETE /apagar_registo/\<id>** - encarregue de tratar de toda a lógica associada à eliminação de um determinado registo


* **PUT /editar_treinador/\<idTreinador>** - encarregue de tratar de toda a lógica associada à edição de um determinado registo de um treinador
* **PUT /editar_arbitro/\<idArbitro>** - encarregue de tratar de toda a lógica associada à edição de um determinado registo de um árbitro
* **PUT /editar_jogador/\<idJogador>** - encarregue de tratar de toda a lógica associada à edição de um determinado registo de um jogador


### Interface
Relativamente ao módulo que sustenta a interface da aplicação web, procurou-se estabelecer um design simples mas que salientasse todas as funcionalidades desenvolvidas, assim como fornecer um ambiente de consulta e interpretação dos dados com certo grau de comodidade para o utilizador. Logo no página principal, é possível consultar a classificação geral da liga acompanhada de algumas estatísticas complementares, assim como interagir com duas tabelas de modo a consultar os jogadores ou clubes líderes nos parâmetros fornecidos, sendo que esta informação poderá ser consultada com maior detalhe na página relativa aos líderes do campeonato. São também disponibilizadas páginas de consulta relativas aos treinadoes, árbitros e clubes. Para terminar, os administradores da aplicação poderão ainda interagir com a mesma através da adição, edição e eliminação de registos.


* **GET /** - rota relativa à página principal
* **GET /entrar** - rota relativa à página de login
* **GET /clubes/\<id>** - rota relativa à página individual de um clube
* **GET /arbitros** - rota relativa à página dos árbitros
* **GET /treinadores** - rota relativa à página dos treinadores
* **GET /lideres** - rota relativa à página dos líderes do campeonato
* **GET /gerir** - rota relativa à página de gestão registo por parte do administrador com sessão ativa


* **POST /entrar** - rota relativa ao pedido de login por parte de um utilizador
* **POST /sair** - rota relativa ao pedido de logout por parte de um utilizador
* **POST /adicionar_jogador** - rota relativa ao pedido de adição de um registo de um jogador por parte do administrador com sessão ativa
* **POST /adicionar_treinador** - rota relativa ao pedido de adição de um registo de um treinador por parte do administrador com sessão ativa
* **POST /adicionar_árbitro** - rota relativa ao pedido de adição de um registo de um árbitro por parte do administrador com sessão ativa
* **POST /editar_registo** - rota relativa ao pedido de edição de um registo por parte do administrador com sessão ativa
* **POST /editar_treinador/\<idTreinador>** - rota relativa ao pedido de edição de um registo de um treinador por parte do administrador com sessão ativa
* **POST /editar_arbitro/\<idArbitro>** - rota relativa ao pedido de edição de um registo de um árbitro por parte do administrador com sessão ativa
* **POST /editar_jogador/\<idJogador>** - rota relativa ao pedido de edição de um registo de um jogador por parte do administrador com sessão ativa
* **POST /remover** - rota relativa ao pedido de remoção de um registo por parte do administrador com sessão ativa


## Conclusão


De um modo geral, o desenvolvimento deste trabalho prático permitiu aprofundar o estudo e a compreensão de ferramentas e conceitos abordados ao longo do semestre de forma aplicada. Através deste projeto, foi possível aplicar o conhecimento adquirido e explorar o processo de desenvolvimento e funcionamento de uma aplicação web voltada para estatísticas de futebol.

De acordo com a proposta apresentada, os objetivos foram plenamente atingidos. A **gfootdz** revelou-se uma ferramenta valiosa para os entusiastas da **Liga Portugal Betclic 2023/2024**, oferecendo acesso simplificado e direto a diversas estatísticas e informações relevantes sobre a mesma. A aplicação destaca-se pela sua interface intuitiva, permitindo uma consulta e análise eficientes dos dados pretendidos.

Como trabalho futuro, propõe-se a expansão do âmbito da aplicação, através da adição de mais competições de futebol, permitindo alargar o seu alcance. 

Concluindo, encerra-se o presente relatório relativo à plataforma web desenvolvida em resposta ao projeto prático proposto pela Unidade Curricular de **Representação e Processamento de Conhecimento na Web**, no ano letivo de 2023/2024. A **gfootdz** não só cumpre os requisitos estabelecidos pelo projeto como também se posiciona como um software útil e relevante para os utilizadores que procurem informações detalhadas sobre a principal liga de futebol em Portugal.
