import json

with open('../data/clubes.json') as ficheiro_clubes:
    clubes = json.load(ficheiro_clubes)

with open('../data/gr.json') as ficheiro_gr:
    gr = json.load(ficheiro_gr)

with open('../data/fbref_clubs.json') as ficheiro_stats_clubes:
    stats_clubes = json.load(ficheiro_stats_clubes)

with open('../data/fbref_results.json') as ficheiro_resultados:
    resultados = json.load(ficheiro_resultados)

with open('../data/transfermarkt.json') as ficheiro_transfermarkt:
    transfermarkt = json.load(ficheiro_transfermarkt)

with open('../data/treinadores.json') as ficheiro_treinadores:
    treinadores = json.load(ficheiro_treinadores)

with open('../data/arbitros.json') as ficheiro_arbitros:
    arbitros = json.load(ficheiro_arbitros)

CLUBES = {}

ID = 1
ttl = ''

## ESTADIO E CLUBE

for clube, values in clubes.items():
    ttl += f'''###  http://rpcw.di.uminho.pt/2024/gfootdz#E{ID}
:E{ID} rdf:type owl:NamedIndividual ,
                       :Estádio ;
              :capacidadeEstadio "{values["capacidade"]}"^^xsd:int ;
              :nomeEstadio "{values["estadio"]}" .

'''
    CLUBES[clube] = ID
    ttl += f'''###  http://rpcw.di.uminho.pt/2024/gfootdz#C{ID}
:C{ID} rdf:type owl:NamedIndividual ,
                       :Clube ;
              :temEstadio :E{ID} ;
              :lotacaoMediaEquipa "{stats_clubes[clube]["attendance_per_g"].replace('.','')}"^^xsd:int  ;
              :fundacaoClube "{values["fundacao"]}" ;
              :amarelosEquipa "{stats_clubes[clube]["stats_standard_32"]["cards_yellow"]}"^^xsd:int ;
              :golosEquipa "{stats_clubes[clube]["stats_standard_32"]["goals"]}"^^xsd:int ;
              :golosSofridosEquipa "{stats_clubes[clube]["against"]["stats_standard_32"]["goals"]}"^^xsd:int ;
              :empatesEquipa "{values["empates"]}"^^xsd:int ;
              :vitoriasEquipa "{values["vitorias"]}"^^xsd:int ; 
              :derrotasEquipa "{values["derrotas"]}"^^xsd:int ;
              :nomeClube "{clube}" ;
              :nomeCompletoClube "{values["nome"]}" ;
              :penaltisContraEquipa "{stats_clubes[clube]["against"]["stats_standard_32"]["pens_att"]}"^^xsd:int ;
              :penaltisFavorEquipa "{stats_clubes[clube]["stats_standard_32"]["pens_att"]}"^^xsd:int ;
              :vermelhosEquipa "{stats_clubes[clube]["stats_standard_32"]["cards_red"]}"^^xsd:int ;
              :xgEquipa "{stats_clubes[clube]["stats_standard_32"]["xg"]}"^^xsd:float .\n\n
''' 
    
    ID += 1


## JOGADORES

ID = 1

JOGADORES = {}

for clube in transfermarkt:
    nome_clube = list(clube.keys())[0]

    for jogador in clube[nome_clube]:
        nome_jogador = list(jogador.keys())[0]

        JOGADORES[nome_jogador] = ID

        jogador_fbref = stats_clubes[nome_clube]["players"][nome_jogador]

        
        ttl += f'''###  http://rpcw.di.uminho.pt/2024/gfootdz/PL{ID}
:PL{ID} rdf:type owl:NamedIndividual ,
                          :Jogador ;
             :joga :C{CLUBES[nome_clube]} ;\n'''
        
        if "stats_misc_32" not in stats_clubes[nome_clube]["players"][nome_jogador]:
            ttl += '             :aereosGanhos "0.0"^^xsd:float ;\n'
            ttl += '             :autoGolos "0"^^xsd:int ;\n'
            ttl += '             :bolasRecuperadas "0"^^xsd:int ;\n'
            ttl += '             :cruzamentos "0"^^xsd:int ;\n'
            ttl += '             :faltasCometidas "0"^^xsd:int ;\n'
            ttl += '             :faltasSofridas "0"^^xsd:int ;\n'
            ttl += '             :forasDeJogo "0"^^xsd:int ;\n'
        else:
            ttl += f'             :aereosGanhos "{jogador_fbref["stats_misc_32"]["aerials_won_pct"].replace(",", ".")}"^^xsd:float ;\n'
            ttl += f'             :autoGolos "{jogador_fbref["stats_misc_32"]["own_goals"]}"^^xsd:int ;\n'
            ttl += f'             :bolasRecuperadas "{jogador_fbref["stats_misc_32"]["ball_recoveries"]}"^^xsd:int ;\n'
            ttl += f'             :cruzamentos "{jogador_fbref["stats_misc_32"]["crosses"]}"^^xsd:int ;\n'
            ttl += f'             :faltasCometidas "{jogador_fbref["stats_misc_32"]["fouls"]}"^^xsd:int ;\n'
            ttl += f'             :faltasSofridas  "{jogador_fbref["stats_misc_32"]["fouled"]}"^^xsd:int ;\n'
            ttl += f'             :forasDeJogo "{jogador_fbref["stats_misc_32"]["offsides"]}"^^xsd:int ;\n'


        if "stats_defense_32" not in stats_clubes[nome_clube]["players"][nome_jogador]:
            ttl += '             :cortes "0"^^xsd:int ;\n'
            ttl += '             :cortesGanhos "0"^^xsd:int ;\n'
            ttl += '             :duelos "0"^^xsd:int ;\n'
            ttl += '             :duelosGanhos "0"^^xsd:int ;\n'
            ttl += '             :intercecoes "0"^^xsd:int ;\n'
        else:
            ttl += f'             :cortes "{jogador_fbref["stats_defense_32"]["tackles"]}"^^xsd:int ;\n'
            ttl += f'             :cortesGanhos "{jogador_fbref["stats_defense_32"]["tackles_won"]}"^^xsd:int ;\n'
            ttl += f'             :duelos "{jogador_fbref["stats_defense_32"]["challenges"]}"^^xsd:int ;\n'
            ttl += f'             :duelosGanhos "{int(jogador_fbref["stats_defense_32"]["challenges"]) - int(jogador_fbref["stats_defense_32"]["challenges_lost"])}"^^xsd:int ;\n'
            ttl += f'             :intercecoes "{jogador_fbref["stats_defense_32"]["interceptions"]}"^^xsd:int ;\n'


        if "stats_gca_32" not in stats_clubes[nome_clube]["players"][nome_jogador]:
            ttl += '             :gca "0"^^xsd:int ;\n'
        else:
            ttl += f'             :gca "{jogador_fbref["stats_gca_32"]["gca"]}"^^xsd:int ;\n'


        if "stats_possession_32" not in stats_clubes[nome_clube]["players"][nome_jogador]:
            ttl += '             :toques "0"^^xsd:int ;\n'
        else:
            ttl += f'             :toques "{jogador_fbref["stats_possession_32"]["touches"]}"^^xsd:int ;\n'


        if "stats_shooting_32" not in stats_clubes[nome_clube]["players"][nome_jogador]:
            ttl += '             :rematesBalizaJogador "0"^^xsd:int ;\n'
            ttl += '             :rematesJogador "0"^^xsd:int ;\n'
        else:
            ttl += f'             :rematesBalizaJogador "{jogador_fbref["stats_shooting_32"]["shots_on_target"]}"^^xsd:int ;\n'
            ttl += f'             :rematesJogador "{jogador_fbref["stats_shooting_32"]["shots"]}"^^xsd:int ;\n'
        

        if "stats_passing_32" not in stats_clubes[nome_clube]["players"][nome_jogador]:
            ttl += '             :keyPasses "0"^^xsd:int ;\n'
            ttl += '             :passesCompletos "0"^^xsd:int ;\n'
            ttl += '             :percentagemPasses "0"^^xsd:float ;\n'
        else:
            total_passes_completos = int(jogador_fbref["stats_passing_32"]["passes_completed_short"]) + int(jogador_fbref["stats_passing_32"]["passes_completed_medium"]) + int(jogador_fbref["stats_passing_32"]["passes_completed_long"])
            total_passes = 0
            if jogador_fbref["stats_passing_32"]["passes_pct_short"] != '':
                total_passes += float(int(jogador_fbref["stats_passing_32"]["passes_completed_short"]) / float(jogador_fbref["stats_passing_32"]["passes_pct_short"].replace(",",".")))
            if jogador_fbref["stats_passing_32"]["passes_pct_medium"] != '':
                total_passes += float(int(jogador_fbref["stats_passing_32"]["passes_completed_medium"]) / float(jogador_fbref["stats_passing_32"]["passes_pct_medium"].replace(",",".")))
            if jogador_fbref["stats_passing_32"]["passes_pct_long"] != '':
                total_passes += float(int(jogador_fbref["stats_passing_32"]["passes_completed_long"]) / float(jogador_fbref["stats_passing_32"]["passes_pct_long"].replace(",",".")))

            ttl += f'             :keyPasses "{jogador_fbref["stats_passing_32"]["assisted_shots"]}"^^xsd:int ;\n'
            ttl += f'             :passesCompletos "{total_passes_completos}"^^xsd:int ;\n'

            if total_passes != 0:
                ttl += f'             :percentagemPasses "{round((total_passes_completos/total_passes),1)}"^^xsd:float ;\n'
            else:
                ttl += f'             :percentagemPasses "0"^^xsd:float ;\n'
        

        ttl += f'''             :alturaJogador "{jogador[nome_jogador]['Altura']}" ;
             :assistenciasJogador "{jogador_fbref["stats_standard_32"]["assists"]}"^^xsd:int ;
             :caJogador "{jogador_fbref["stats_standard_32"]["cards_yellow"]}"^^xsd:int ;
             :conducoesProgressivas "{jogador_fbref["stats_standard_32"]["progressive_carries"]}"^^xsd:int ;
             :cvJogador "{jogador_fbref["stats_standard_32"]["cards_red"]}"^^xsd:int ;
             :dataNascimento "{jogador[nome_jogador]['dataNasc']}" ;
             :golosJogador "{jogador_fbref["stats_standard_32"]["goals"]}"^^xsd:int ;
             :jogosJogador "{jogador_fbref["stats_standard_32"]["games"]}"^^xsd:int ;
             :minutosJogador "{jogador_fbref["stats_standard_32"]["minutes"].replace('.', '')}"^^xsd:int ;
             :nomePessoa "{nome_jogador}" ;
             :numeroJogador "{jogador[nome_jogador]['NumeroCamisola']}"^^xsd:int ;
             :nacionalidade "{jogador[nome_jogador]['Nacionalidade']}" ;\n'''
            
        if 'Nome completo' not in jogador[nome_jogador]:
            ttl += f'             :nomeCompleto "{nome_jogador}" ;\n'
        else:
            ttl += f'             :nomeCompleto "{jogador[nome_jogador]["Nome completo"]}" ;\n'

        
        if jogador[nome_jogador]['Posição'] == 'Guarda-redes':
            ttl += f'''             :golosSofridosGR "{gr[nome_jogador]["gk_goals_against"]}"^^xsd:int ;
             :rematesSofridosGR "{gr[nome_jogador]["gk_shots_on_target_against"]}"^^xsd:int ;
             :cleanSheets "{gr[nome_jogador]["gk_clean_sheets"]}"^^xsd:int ;
             :penaltisContraGR "{gr[nome_jogador]["gk_pens_att"]}"^^xsd:int ;
             :penaltisDefendidosGR "{gr[nome_jogador]["gk_pens_saved"]}"^^xsd:int ;
             :xgSofridosGR "{gr[nome_jogador]["gk_psxg"].replace(",",".")}"^^xsd:float ;\n'''

        
        ttl += f'''             :passesProgressivos "{jogador_fbref["stats_standard_32"]["progressive_passes"]}"^^xsd:int ;
             :peJogador "{jogador[nome_jogador]['Pé']}" ;
             :penaltisMarcadosJogador "{jogador_fbref["stats_standard_32"]["pens_made"]}"^^xsd:int ;
             :penaltisTentadosJogador "{jogador_fbref["stats_standard_32"]["pens_att"]}"^^xsd:int ;
             :posicaoJogador "{jogador[nome_jogador]['Posição']}" ;
             :valorJogador "{jogador[nome_jogador]['Valor de Mercado']}" ;
             :xaJogador "{jogador_fbref["stats_standard_32"]["xg_assist"]}"^^xsd:float ;
             :xgJogador "{jogador_fbref["stats_standard_32"]["xg"]}"^^xsd:float .\n\n'''
        
        
        ID += 1


## TREINADORES

ID = 1

for treinador, values in treinadores.items(): 

    ttl += f'''###  http://rpcw.di.uminho.pt/2024/gfootdz/T{ID}
:T{ID} rdf:type owl:NamedIndividual ,
                          :Treinador ;\n'''
    for clube in values['clubes']:
        ttl += f'    :treina :C{CLUBES[clube]} ;\n'
    
    ttl += f'''    :dataNascimento "{values["dataNasc"]}" ;
    :derrotasTreinador "{values["d"]}"^^xsd:int ;
    :empatesTreinador "{values["e"]}"^^xsd:int ;
    :formacaoTreinador "{values["formacao"]}" ;\n'''
    
    if type(values["pais"]) == list:
        nacionalidades = '  '.join(values["pais"])
        ttl += f'    :nacionalidade "{nacionalidades}" ;\n'
    else:
        ttl += f'    :nacionalidade "{values["pais"]}" ;\n'

    ttl += f'''    :nomePessoa "{treinador}" ;
    :nomeCompleto "{values["nome"]}" ;
    :vitoriasTreinador "{values["v"]}"^^xsd:int .\n\n'''

    ID += 1


## ÁRBITROS

ID = 1

ARBITROS = {}

for arbitro, values in arbitros.items(): 


    ARBITROS[arbitro] = ID

    ttl += f'''###  http://rpcw.di.uminho.pt/2024/gfootdz/A{ID}
:A{ID} rdf:type owl:NamedIndividual ,
                          :Árbitro ;
    :amarelosArbitro "{values["cartoesAmarelos"]}"^^xsd:int ;
    :associacaoArbitro "{values["associacao"]}" ;
    :dataNascimento "{values["dataNascimento"]}" ;
    :duplosAmarelosArbitro "{values["duploAmarelo"]}"^^xsd:int ;
    :jogosArbitro "{values["jogos"]}"^^xsd:int ;
    :nacionalidade "{values["pais"]}" ;
    :nomePessoa "{arbitro}" ;
    :nomeCompleto "{values["nome"]}" ;
    :penaltisArbitro "{values["penaltis"]}"^^xsd:int ;
    :vermelhosArbitro "{values["cartoesVermelhos"]}"^^xsd:int .\n\n'''

    ID += 1


## JOGOS

ID = 1

for ronda in resultados:
    for jogo in resultados[ronda]:
        equipas = jogo.split('_')

        ttl += f'''###  http://rpcw.di.uminho.pt/2024/gfootdz/J{ID}
:J{ID} rdf:type owl:NamedIndividual ,
                          :Jogo ;
        :equipaCasa :C{CLUBES[equipas[0]]} ;
        :equipaFora :C{CLUBES[equipas[1]]} ;
        :temArbitro :A{ARBITROS[resultados[ronda][jogo]["referee"]]} ;
        :jornada "{ronda}" ;
        :dataJogo "{resultados[ronda][jogo]["date"]}" ;
        :espectadores "{resultados[ronda][jogo]["attendance"].replace('.', '')}"^^xsd:int ;
        :formacaoCasa "{resultados[ronda][jogo][equipas[0]]["formation"]}" ;
        :formacaoFora "{resultados[ronda][jogo][equipas[1]]["formation"]}" ;
        :horaJogo "{resultados[ronda][jogo]["start_time"]}" ;
        :posseJogo "{resultados[ronda][jogo][equipas[0]]["possession"]}-{resultados[ronda][jogo][equipas[1]]["possession"]}" ;
        :resultado "{resultados[ronda][jogo][equipas[0]]["goals_for"]}-{resultados[ronda][jogo][equipas[1]]["goals_for"]}" ;
        :xgCasa "{resultados[ronda][jogo][equipas[0]]["xg_for"]}"^^xsd:float ;
        :xgFora "{resultados[ronda][jogo][equipas[1]]["xg_for"]}"^^xsd:float .\n\n
'''
        ID += 1


print(ttl)