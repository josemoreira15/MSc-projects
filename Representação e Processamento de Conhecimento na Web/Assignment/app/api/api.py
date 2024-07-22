from flask import Flask, jsonify, request
from SPARQLWrapper import JSON, SPARQLWrapper
import datetime, jwt

app = Flask(__name__)
SECRET_KEY = 'gfootdz_secret'
GRAPHDB_ENDPOINT = "http://localhost:7200/repositories/gfootdz"


player_stat_selector = [
    ('jogosJogador', 'Jogos', 'Mais Jogos'), ('minutosJogador', 'Minutos', 'Mais Utilizados'), ('conducoesProgressivas', 'Conduções progressivas', 'Mais Conduções Progressivas'),
    ('passesProgressivos', 'Passes progressivos', 'Mais Passes Progressivos'), ('golosJogador', 'Golos', 'Melhores Marcadores'), ('assistenciasJogador', 'Assistências', 'Melhores Assistentes'),
    ('autoGolos', 'Autogolos','Mais Autogolos'), ('bolasRecuperadas', 'Recuperações', 'Mais Recuperações'), ('caJogador', 'Cartões', 'Mais Cartões Amarelos'),
    ('cvJogador', 'Cartões', 'Mais Cartões Vermelhos'), ('cruzamentos', 'Cruzamentos', 'Mais Cruzamentos'), ('faltasCometidas', 'Faltas', 'Mais Faltas Cometidas'),
    ('faltasSofridas', 'Faltas', 'Mais Faltas Sofridas'), ('gca', 'GCA', 'Mais Ações de Criação de Golo'), ('intercecoes', 'Interceções', 'Mais Interceções'),
    ('keyPasses', 'Passes', 'Mais Passes Chave'), ('percentagemPasses', '% Passes', 'Maior % de Acerto de Passes'),
    ('toques', 'Toques', 'Mais Toques na Bola')
]


league_stat_selector = [
    ('xgEquipa', 'xG', 'Mais Golos Esperados'), ('vermelhosEquipa','Cartões vermelhos', 'Mais Cartões Vermelhos'), ('amarelosEquipa','Cartões amarelos', 'Mais Cartões Amarelos'),
    ('penaltisFavorEquipa', 'Penáltis', 'Mais Penáltis a Favor'), ('penaltisContraEquipa', 'Penáltis', 'Mais Penáltis Contra'),
    ('lotacaoMediaEquipa', 'Lotação', 'Maior Lotação Média'), ('lotacaoMediaEquipa', '% Ocupação', 'Maior Taxa de Ocupação'),
    ('','', 'Plantel Mais Valioso'), ('','', 'Maior Eficácia'), ('', '', 'Plantel mais Jovem')
]


player_all_properties = [
    'alturaJogador', 'dataNascimento', 'jogosJogador', 'minutosJogador', 'nacionalidade',
    'nomeCompleto', 'nomePessoa', 'numeroJogador', 'peJogador', 'posicaoJogador', 'valorJogador',
    'assistenciasJogador', 'conducoesProgressivas', 'cruzamentos', 'faltasSofridas', 'forasDeJogo',
    'gca', 'golosJogador', 'keyPasses', 'passesCompletos', 'passesProgressivos', 'penaltisMarcadosJogador',
    'penaltisTentadosJogador', 'percentagemPasses', 'rematesBalizaJogador', 'rematesJogador', 'toques',
    'xaJogador', 'xgJogador', 'aereosGanhos', 'autoGolos', 'bolasRecuperadas', 'caJogador', 'cortes',
    'cortesGanhos', 'cvJogador', 'duelos', 'duelosGanhos', 'faltasCometidas', 'intercecoes', 'joga',
    'cleanSheets', 'golosSofridosGR', 'penaltisContraGR', 'penaltisDefendidosGR', 'rematesSofridosGR', 'xgSofridosGR'
]


def sparql_get_query(query):
    sparql = SPARQLWrapper("http://localhost:7200/repositories/gfootdz")
    sparql.setMethod('GET')
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    return sparql.query().convert()


def sparql_post_query(query):
    sparql = SPARQLWrapper("http://localhost:7200/repositories/gfootdz/statements")
    sparql.setMethod('POST')
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    return sparql.query().convert()


def verify_token(token):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return True
    
    except jwt.ExpiredSignatureError:
        return False
    
    except jwt.InvalidTokenError:
        return False


def check_token():
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Access denied'}), 403
    
    token = auth_header.split(' ')[1]
    if not verify_token(token):
        return jsonify({'message': 'Invalid or expired token'}), 403
    
    return jsonify({'message': 'Valid'}), 200


@app.get('/')
def index():
    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?c ?g ?gs ?v ?e ?d ?n WHERE {
    ?c a :Clube ;
           :golosEquipa ?g ;
           :golosSofridosEquipa ?gs ;
           :vitoriasEquipa ?v ;
           :empatesEquipa ?e ;
           :derrotasEquipa ?d ;
           :nomeClube ?n .
}
'''
    resultado = sparql_get_query(query)
    tabela = []

    for linha in resultado['results']['bindings']:
        vs = linha['v']['value']
        es = linha['e']['value']
        ds = linha['d']['value']
        id = linha['c']['value'].split("/")[-1]

        tabela.append({
            'id': id,
            'classificacao': id.split('C')[-1],
            'clube': linha['n']['value'],
            'vitorias': vs,
            'empates': es,
            'derrotas': ds,
            'gms': linha['g']['value'],
            'gs': linha['gs']['value'],
            'pontos': int(vs) * 3 + int(es)
        })

    league_selector = {}
    
    for selector in league_stat_selector:

        if selector[2] == 'Maior Taxa de Ocupação':
            query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?c ?nome ?valor ?ce ((?valor / ?ce) AS ?taxaOcupacao) WHERE {{
        ?c a :Clube ;
           :temEstadio ?e ;
           :nomeClube ?nome ;
           :lotacaoMediaEquipa ?valor .
        ?e :capacidadeEstadio ?ce .
}} ORDER BY DESC(?taxaOcupacao) LIMIT 10
    '''
            clubs = []
            resultado = sparql_get_query(query)
            for linha in resultado['results']['bindings']:
                clubs.append({
                       'id': linha['c']['value'].split("/")[-1],
                       'nome': linha['nome']['value'],
                       'stat': round(float(linha['taxaOcupacao']['value'])*100,1)
                   })
            league_selector[selector[2]] = [selector[1], clubs]
            
        
        elif selector[2] != 'Plantel Mais Valioso' or selector[2] != 'Maior Eficácia' or selector[2] != 'Plantel mais Jovem':

            query = f'''
        PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
        SELECT * WHERE {{
            ?c a :Clube ;
               :temEstadio ?e ;
               :nomeClube ?nome ;
               :{selector[0]} ?valor .
            ?e :capacidadeEstadio ?ce .
        }} ORDER BY DESC (?valor) ASC(?nome) LIMIT 10
        '''
            resultado = sparql_get_query(query)

            clubs = []
            for linha in resultado['results']['bindings']:
                clubs.append({
                    'id': linha['c']['value'].split("/")[-1],
                    'nome': linha['nome']['value'],
                    'stat': linha['valor']['value']
                })
            league_selector[selector[2]] = [selector[1], clubs]
    
    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?clube ?nomeClube (SUM(?valorJogador) AS ?valorTotalPlantel) WHERE {
    ?jogador a :Jogador ;
             :joga ?clube ;
             :valorJogador ?valor .
    ?clube :nomeClube ?nomeClube .
    BIND(
        IF(CONTAINS(?valor, "M"), xsd:float(STRBEFORE(?valor, " M")),
        IF(CONTAINS(?valor, "k"), xsd:float(STRBEFORE(?valor, " k")) / 1000, 0.0))
        AS ?valorJogador
    )
}
GROUP BY ?clube ?nomeClube
ORDER BY DESC(?valorTotalPlantel)
LIMIT 10
'''
    resultado = sparql_get_query(query)
    clubs = []
    for linha in resultado['results']['bindings']:
        clubs.append({
            'id': linha['clube']['value'].split("/")[-1],
            'nome': linha['nomeClube']['value'],
            'stat': round(float(linha['valorTotalPlantel']['value']),1)
        })
    league_selector['Plantel Mais Valioso'] = ['Valor (M €)', clubs]

    query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?c ?nome ((?valor - ?valorF) AS ?value) WHERE {{
        ?c a :Clube ;
           :nomeClube ?nome ;
           :xgEquipa ?valorF ;
           :golosEquipa ?valor .
}} ORDER BY DESC (?value) ASC(?nome) LIMIT 10
    '''
    resultado = sparql_get_query(query)
    clubs = []
    for linha in resultado['results']['bindings']:
        clubs.append({
            'id': linha['c']['value'].split("/")[-1],
            'nome': linha['nome']['value'],
            'stat': f'+{round(float(linha["value"]["value"]),1)}'
        })
    league_selector['Maior Eficácia'] = ['xG +/-', clubs]

    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?clube ?nomeClube ?nomeJogador ?dataNascimento WHERE {
    ?jogador a :Jogador ;
             :joga ?clube ;
             :dataNascimento ?dataNascimento ;
             :nomePessoa ?nomeJogador .
    ?clube :nomeClube ?nomeClube .
}
'''
    resultado = sparql_get_query(query)
    
    clubes = {}

    for linha in resultado['results']['bindings']:
        id = linha['clube']['value'].split("/")[-1],
        nome_clube = linha['nomeClube']['value']
        data_nascimento = linha['dataNascimento']['value']
        nascimento = datetime.datetime.strptime(data_nascimento, "%d/%m/%Y")
        hoje = datetime.datetime.today()
        idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
    
        if nome_clube not in clubes:
            clubes[nome_clube] = {'id': id, 'idades': []}
    
        clubes[nome_clube]['idades'].append(idade)
        

    idade_media_plantel = {clube: sum(data['idades']) / len(data['idades']) for clube, data in clubes.items()}
    clubes_ordenados = sorted(idade_media_plantel.items(), key=lambda x: x[1])[:10]

    clubs = []
    for clube, idade_media in clubes_ordenados:
        clubs.append({'id': clubes[clube]['id'][0], 'nome': clube, 'stat': round(idade_media, 1)})

    league_selector['Plantel mais Jovem'] = ['Média de Idades', clubs]


    player_selector = {}

    for selector in player_stat_selector:
        
        query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>

SELECT ?nome ?valor ?clube ?nclube WHERE {{
	   ?j a :Jogador ;
          :jogosJogador ?jogos ;
       	  :nomePessoa ?nome ;
          :{selector[0]} ?valor ;
          :joga ?clube .
       ?clube :nomeClube ?nclube .
       FILTER (?jogos > 10)
}} ORDER BY DESC(?valor) ASC(?jogos) ASC(?nome) LIMIT 10
'''
        resultado = sparql_get_query(query)
        players = []
        for linha in resultado['results']['bindings']:
            players.append({
                'nome': linha['nome']['value'],
                'stat': linha['valor']['value'],
                'clube': linha['clube']['value'].split("/")[-1],
                'ne': linha['nclube']['value']
            })
        
        player_selector[selector[2]] = [selector[1], players]   

    return jsonify({'tabela': tabela, 'player_selector': player_selector, 'league_selector': league_selector, 'player_stat_selector': player_stat_selector, 'league_stat_selector': league_stat_selector}), 200


@app.get('/clubes/<id>')
def clube(id):
    query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?ne ?ce ?f ?n ?nc ?gs ?gss ?pf ?pc ?as ?vs ?xg ?v ?es ?ds ?lm WHERE {{
    ?c a :Clube ;
       :temEstadio ?e ;
       :fundacaoClube ?f ;
       :nomeClube ?n ;
       :nomeCompletoClube ?nc ;
       :golosEquipa ?gs ;
       :golosSofridosEquipa ?gss ;
       :penaltisFavorEquipa ?pf ;
       :penaltisContraEquipa ?pc ;
       :amarelosEquipa ?as ;
       :vermelhosEquipa ?vs ;
       :xgEquipa ?xg;
       :vitoriasEquipa ?v ;
       :empatesEquipa ?es ;
       :derrotasEquipa ?ds ;
       :lotacaoMediaEquipa ?lm .
    ?e :nomeEstadio ?ne ;
       :capacidadeEstadio ?ce .
    FILTER (?c = :{id})
}}
'''
    resultado = sparql_get_query(query)
    content = resultado['results']['bindings'][0]
    capacidade = int(content['ce']['value'])
    lotacao = int(content['lm']['value'])
    info = {
        'nomeEstadio': content['ne']['value'],
        'capacidadeEstadio': capacidade,
        'fundacaoClube': content['f']['value'],
        'nomeClube': content['n']['value'],
        'nomeCompletoClube': content['nc']['value'],
        'golos': content['gs']['value'],
        'golosSofridos': content['gss']['value'],
        'penaltisFavor': content['pf']['value'],
        'penaltisContra': content['pc']['value'],
        'amarelos': content['as']['value'],
        'vermelhos': content['vs']['value'],
        'xg': content['xg']['value'],
        'vitorias': content['v']['value'],
        'empates': content['es']['value'],
        'derrotas': content['ds']['value'],
        'lotacaoMedia': lotacao,
        'lotacaoPerc': round(float(lotacao) / float(capacidade) * 100, 1)
    }

    query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?tr ?nt WHERE {{
    ?tr :treina ?c ;
        :nomePessoa ?nt ;
    FILTER (?c = :{id})
}}
'''
    resultado = sparql_get_query(query)
    treinadores = []
    for linha in resultado['results']['bindings']:
        treinadores.append({
            'id': linha['tr']['value'].split("/")[-1],
            'nome': linha['nt']['value']
        })

    query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?j ?n ?num ?p ?dn ?nac ?nc ?aj ?pj ?vm WHERE {{
	?c a :Clube .
    ?j a :Jogador ;
       :joga ?c ;
	   :nomePessoa ?n ;
       :numeroJogador ?num ;
       :posicaoJogador ?p ;
       :dataNascimento ?dn ;
       :nacionalidade ?nac ;
       :nomeCompleto ?nc ;
       :alturaJogador ?aj ;
       :peJogador ?pj ;
       :valorJogador ?vm .
    FILTER (?c = :{id})
}}
'''
    resultado = sparql_get_query(query)
    jogadores = []
    for linha in resultado['results']['bindings']:
        jogadores.append({
            'id': linha['j']['value'].split("/")[-1],
            'nome': linha['n']['value'],
            'numero': linha['num']['value'],
            'posicao': linha['p']['value'].split('- ')[-1],
            'dataNascimento': linha['dn']['value'],
            'nacionalidade': linha['nac']['value'].replace('  ', ' / '),
            'nomeCompleto': linha['nc']['value'],
            'altura': linha['aj']['value'],
            'pe': linha['pj']['value'],
            'valor': linha['vm']['value']
        })

    query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?ec ?nec ?ef ?nef ?ar ?nar ?d ?es ?fc ?ff ?hj ?res ?pj ?xgc ?xgf ?jor WHERE {{
    ?j a :Jogo ;
       :equipaCasa ?ec ;
       :equipaFora ?ef ;
       :temArbitro ?ar ;
       :dataJogo ?d ;
       :espectadores ?es ;
       :formacaoCasa ?fc ;
       :formacaoFora ?ff ;
       :horaJogo ?hj ;
       :posseJogo ?pj ;
       :resultado ?res ;
       :xgCasa ?xgc ;
       :xgFora ?xgf ;
       :jornada ?jor .
    ?ec :nomeClube ?nec .
    ?ef :nomeClube ?nef .
    ?ar :nomePessoa ?nar .
    FILTER(?ec = :{id} || ?ef = :{id})
}} ORDER BY (?d)
'''
    resultado = sparql_get_query(query)
    jogos = []
    for linha in resultado['results']['bindings']:
        split_data = linha['d']['value'].split('-')
        data = split_data[2] + '/' + split_data[1] + '/' + split_data[0]
        jogos.append({
            'idEquipaCasa': linha['ec']['value'].split("/")[-1],
            'nomeEquipaCasa': linha['nec']['value'],
            'idEquipaFora': linha['ef']['value'].split("/")[-1],
            'nomeEquipaFora': linha['nef']['value'],
            'idArbitro': linha['ar']['value'].split("/")[-1],
            'nomeArbitro': linha['nar']['value'],
            'dataJogo': data,
            'espectadores': linha['es']['value'],
            'formacaoCasa': linha['fc']['value'],
            'formacaoFora': linha['ff']['value'],
            'hora': linha['hj']['value'],
            'resultado': linha['res']['value'].replace('-', ' - '),
            'posseJogo': linha['pj']['value'].replace('-', '% - ') + '%',
            'xgCasa': linha['xgc']['value'],
            'xgFora': linha['xgf']['value'],
            'jornada': linha['jor']['value'],
        })

    query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>

SELECT * WHERE {{
    ?j a :Jogador;
       :joga :{id};
       :nomePessoa ?n ;
       :jogosJogador ?jj ;
       :minutosJogador ?min ;
       :posicaoJogador "Guarda-redes" ;
       :numeroJogador ?num ;
       :golosSofridosGR ?gs ;
       :rematesSofridosGR ?rs;
       :cleanSheets ?cs;
       :penaltisContraGR ?pc;
       :penaltisDefendidosGR ?pd;
       :xgSofridosGR ?xgs .   
}}
'''
    resultado = sparql_get_query(query)
    gr = []
    for linha in resultado['results']['bindings']:
        csp = 0
        if float(linha['jj']['value']) != 0:
            csp = round(float(linha['cs']['value'])/float(linha['jj']['value'])*100,1)
        diff = round(float(linha['xgs']['value'])-float(linha['gs']['value']),1)
        gr.append({
            'id': linha['j']['value'].split("/")[-1],
            'nome': linha['n']['value'],
            'numero': linha['num']['value'],
            'jogos' : linha['jj']['value'],
            'minutos': linha['min']['value'],
            'golosSofridos': linha['gs']['value'],
            'rematesSofridos': linha['rs']['value'],
            'cleanSheets': linha['cs']['value'],
            'csp' : csp,
            'penaltisContra': linha['pc']['value'],
            'penaltisDefendidos': linha['pd']['value'],
            'sofridosEsperados': linha['xgs']['value'],
            'diff': diff,
            })
        
    query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>

SELECT * WHERE {{
    ?j a :Jogador;
       :joga :{id};
       :nomePessoa ?nome ;
       :numeroJogador ?num ;
       :jogosJogador ?jj ;
       :minutosJogador ?min ;
       :cortes ?c;
	   :cortesGanhos ?cg;
	   :duelos ?d;
	   :duelosGanhos ?dg;
	   :intercecoes ?int;
	   :faltasCometidas ?fc;
	   :autoGolos ?agolos;
	   :bolasRecuperadas ?br;
	   :aereosGanhos ?ag; 
	   :caJogador ?ca;
	   :cvJogador ?cv;
       :posicaoJogador ?pos.
    FILTER(?pos != "Guarda-redes")
}}
'''
    resultado = sparql_get_query(query)
    stats_defensivas = []
    for linha in resultado['results']['bindings']:
        stats_defensivas.append({
            'id': linha['j']['value'].split("/")[-1],
            'numero': linha['num']['value'],
            'nome': linha['nome']['value'],
            'jogos': linha['jj']['value'],
            'mins': linha['min']['value'],
            'cortes': linha['c']['value'],
            'cortesGanhos': linha['cg']['value'],
            'duelos': linha['d']['value'],
            'duelosGanhos': linha['dg']['value'],
            'intercecoes': linha['int']['value'],
            'faltasCometidas': linha['fc']['value'],
            'autoGolos': linha['agolos']['value'],
            'bolasRec': linha['br']['value'],
            'aereosGanhos': linha['ag']['value'],
            'cartoesA': linha['ca']['value'],
            'cartoesV': linha['cv']['value'],
        })

    query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>

SELECT * WHERE {{
    ?j a :Jogador;
       :joga :{id};
       :nomePessoa ?nome ;
       :numeroJogador ?num ;
       :jogosJogador ?jj ;
       :minutosJogador ?min ;
       :toques ?t ;
       :passesCompletos ?pc;
	   :percentagemPasses ?pp;
       :passesProgressivos ?pprog;
	   :xgJogador ?xg;
	   :xaJogador ?xa;
	   :rematesJogador ?r;
	   :rematesBalizaJogador ?rb;
	   :keyPasses ?kp;
       :golosJogador ?golos ;
       :assistenciasJogador ?assists ;
	   :gca ?gca;
       :conducoesProgressivas ?cond ;
	   :forasDeJogo ?fj;
	   :cruzamentos ?c; 
	   :faltasSofridas ?fs;
       :posicaoJogador ?pos.
    FILTER(?pos != "Guarda-redes")
}}
'''
    resultado = sparql_get_query(query)
    stats_atacantes = []
    for linha in resultado['results']['bindings']:
        diffa = 0
        diffg = 0
        if linha['assists']['value'] and linha['xa']['value']:
            diffa = round(float(linha['assists']['value'])-float(linha['xa']['value']),1)
        if linha['golos']['value'] and linha['xg']['value']:
            diffg = round(float(linha['golos']['value'])-float(linha['xg']['value']),1)
        stats_atacantes.append({
            'id': linha['j']['value'].split("/")[-1],
            'numero': linha['num']['value'],
            'nome': linha['nome']['value'],
            'jogos': linha['jj']['value'],
            'mins': linha['min']['value'],
            'toques': linha['t']['value'],
            'passesComp': linha['pc']['value'],
            'percentagemPasses': linha['pp']['value'],
            'passesProg': linha['pprog']['value'],
            'xg': linha['xg']['value'],
            'xa': linha['xa']['value'],
            'remates': linha['r']['value'],
            'rematesBaliza': linha['rb']['value'],
            'golos': linha['golos']['value'],
            'assists': linha['assists']['value'],
            'keypasses': linha['kp']['value'],
            'gca': linha['gca']['value'],
            'conducoes': linha['cond']['value'],
            'forasJogo': linha['fj']['value'],
            'cruzamentos': linha['c']['value'],
            'faltasSofridas': linha['fs']['value'],
            'diffa': diffa,
            'diffg': diffg,
        })
    
    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?c ?g ?gs ?v ?e ?d ?n WHERE {
    ?c a :Clube ;
           :nomeClube ?n .
}
'''
    resultado = sparql_get_query(query)
    tabela = []

    for linha in resultado['results']['bindings']:
        id = linha['c']['value'].split("/")[-1]

        tabela.append({
            'id': id,
            'clube': linha['n']['value'],
        })

    return jsonify({'info': info, 'treinadores': treinadores, 'jogadores': jogadores, 'jogos': jogos, 'grs': gr, 'stats_def': stats_defensivas, 'stats_atac': stats_atacantes, 'tabela': tabela}), 200


@app.get('/arbitros')
def arbitros():
    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?a ?dn ?n ?np ?nc ?aa ?assa ?daa ?ja ?pa ?va WHERE {
    ?a a :Árbitro ;
       :dataNascimento ?dn ;
       :nacionalidade ?n ;
       :nomePessoa ?np ;
       :nomeCompleto ?nc ;
       :amarelosArbitro ?aa ;
       :associacaoArbitro ?assa ;
       :duplosAmarelosArbitro ?daa ;
       :jogosArbitro ?ja ;
       :penaltisArbitro ?pa ;
       :vermelhosArbitro ?va .
} ORDER BY (?np)
'''
    resultado = sparql_get_query(query)
    arbitros = []
    last = None
    for linha in resultado['results']['bindings']:
        id = linha['a']['value'].split("/")[-1]
        arbitros.append({
            'id': id,
            'dataNascimento': linha['dn']['value'],
            'nacionalidade': linha['n']['value'].replace('  ', ' / '),
            'nome': linha['np']['value'],
            'nomeCompleto': linha['nc']['value'],
            'amarelos': linha['aa']['value'],
            'associacao': linha['assa']['value'],
            'duplosAmarelos': linha['daa']['value'],
            'jogos': linha['ja']['value'],
            'penaltis': linha['pa']['value'],
            'vermelhos': linha['va']['value']
        })

        if last == None or int(id[1:]) > int(last[1:]):
            last = id

    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?c ?g ?gs ?v ?e ?d ?n WHERE {
    ?c a :Clube ;
           :nomeClube ?n .
}
'''
    resultado = sparql_get_query(query)
    tabela = []

    for linha in resultado['results']['bindings']:
        id = linha['c']['value'].split("/")[-1]

        tabela.append({
            'id': id,
            'clube': linha['n']['value'],
        })

    return jsonify({'arbitros': arbitros, 'tabela': tabela, 'last': last}), 200


@app.get('/jogadores')
def jogadores():
    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?j WHERE {
    ?j a :Jogador .
}
'''
    resultado = sparql_get_query(query)
    last = None
    for linha in resultado['results']['bindings']:
        id = linha['j']['value'].split('/')[-1]
        if last == None or int(id[2:]) > int(last[2:]):
            last = id

    return jsonify({'last': last}), 200


@app.get('/jogadores/<idJogador>')
def get_jogador(idJogador):

    query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT * WHERE {{
    :{idJogador} ?p ?o .
}} 
'''
    resultado = sparql_get_query(query)['results']['bindings']
    jogador = {}
    jogador['id'] = idJogador
    for result in resultado:
        n_type = result['p']['value'].split('/')[-1]
        if n_type in player_all_properties:
            if n_type == 'joga':
                jogador[n_type] = result['o']['value'].split('/')[-1]
            else:
                jogador[n_type] = result['o']['value']

    return jsonify({'jogador': jogador}), 200


@app.get('/arbitros/<idArbitro>')
def get_arbitro(idArbitro):

    query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?a ?dn ?n ?np ?nc ?aa ?assa ?daa ?ja ?pa ?va WHERE {{
    ?a a :Árbitro ;
       :dataNascimento ?dn ;
       :nacionalidade ?n ;
       :nomePessoa ?np ;
       :nomeCompleto ?nc ;
       :amarelosArbitro ?aa ;
       :associacaoArbitro ?assa ;
       :duplosAmarelosArbitro ?daa ;
       :jogosArbitro ?ja ;
       :penaltisArbitro ?pa ;
       :vermelhosArbitro ?va .
       FILTER(?a = :{idArbitro})
}} ORDER BY (?np)
'''
    resultado = sparql_get_query(query)['results']['bindings'][0]
    arbitro = {
        'id': resultado['a']['value'].split("/")[-1],
        'dataNascimento': resultado['dn']['value'],
        'nacionalidade': resultado['n']['value'].replace('  ', ' / '),
        'nomePessoa': resultado['np']['value'],
        'nomeCompleto': resultado['nc']['value'],
        'amarelosArbitro': resultado['aa']['value'],
        'associacao': resultado['assa']['value'],
        'duplosAmarelos': resultado['daa']['value'],
        'jogosArbitro': resultado['ja']['value'],
        'penaltisArbitro': resultado['pa']['value'],
        'vermelhosArbitro': resultado['va']['value'],
        'associacaoArbitro': resultado['assa']['value'],
        'duplosAmarelosArbitro': resultado['daa']['value']
    }

    return jsonify({'arbitro': arbitro}), 200


@app.get('/treinadores')
def treinadores():
    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?t ?dn ?n ?np ?ncp ?tr ?ntr ?dt ?et ?ft ?vt WHERE {
    ?t a :Treinador ;
       :dataNascimento ?dn ;
       :nacionalidade ?n ;
       :nomePessoa ?np ;
       :nomeCompleto ?ncp ;
       :treina ?tr ;
       :derrotasTreinador ?dt ;
       :empatesTreinador ?et ;
       :formacaoTreinador ?ft ;
       :vitoriasTreinador ?vt .
    ?tr :nomeClube ?ntr .
} ORDER BY (?np)
'''
    resultado = sparql_get_query(query)
    treinadores = {}
    last = None
    for linha in resultado['results']['bindings']:
        id = linha['t']['value'].split("/")[-1]
        nome = linha['np']['value']
        if nome not in treinadores:
            treinadores[nome] = {
                'id': id,
                'dataNascimento': linha['dn']['value'],
                'nacionalidade': linha['n']['value'].replace('  ', ' / '),
                'nomeCompleto': linha['ncp']['value'],
                'treina': {},
                'derrotas': linha['dt']['value'],
                'empates': linha['et']['value'],
                'formacao': linha['ft']['value'],
                'vitorias': linha['vt']['value']
            }

        treinadores[nome]['treina'][linha['tr']['value'].split('/')[-1]] = linha['ntr']['value']
        if last == None or int(id[1:]) > int(last[1:]):
            last = id
    
    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?c ?g ?gs ?v ?e ?d ?n WHERE {
    ?c a :Clube ;
           :nomeClube ?n .
}
'''
    resultado = sparql_get_query(query)
    tabela = []

    for linha in resultado['results']['bindings']:
        id = linha['c']['value'].split("/")[-1]

        tabela.append({
            'id': id,
            'clube': linha['n']['value'],
        })

    return jsonify({'treinadores': treinadores, 'tabela': tabela, 'last': last}), 200


@app.get('/treinadores/<idTreinador>')
def get_treinador(idTreinador):

    query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?t ?dn ?n ?np ?ncp ?tr ?dt ?et ?ft ?vt WHERE {{
    ?t a :Treinador ;
       :dataNascimento ?dn ;
       :nacionalidade ?n ;
       :nomePessoa ?np ;
       :nomeCompleto ?ncp ;
       :treina ?tr ;
       :derrotasTreinador ?dt ;
       :empatesTreinador ?et ;
       :formacaoTreinador ?ft ;
       :vitoriasTreinador ?vt .
     FILTER(?t = :{idTreinador})
}}
'''
    resultado = sparql_get_query(query)['results']['bindings'][0]
    treinador = {
        'id': resultado['t']['value'].split("/")[-1],
        'dataNascimento': resultado['dn']['value'],
        'nomePessoa': resultado['np']['value'],
        'nacionalidade': resultado['n']['value'].replace('  ', ' / '),
        'nomeCompleto': resultado['ncp']['value'],
        'derrotasTreinador': resultado['dt']['value'],
        'empatesTreinador': resultado['et']['value'],
        'formacaoTreinador': resultado['ft']['value'],
        'vitoriasTreinador': resultado['vt']['value'],
        'treina': resultado['tr']['value'].split('/')[-1]
    }
    return jsonify({'treinador': treinador}), 200
   

@app.get('/lideres')
def lideres():
    at_arbitros = [ ('jogosArbitro', 'Jogos'), ('amarelosArbitro', 'Cartões amarelos'), ('duplosAmarelosArbitro', 'Duplos cartões amarelos')]
    at_arbitros += [('vermelhosArbitro', 'Cartões vermelhos'), ('penaltisArbitro', 'Penáltis assinalados')]

    dict_arbitros = {}
    for at in at_arbitros:
        query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>

SELECT ?nome ?valor ?jogos WHERE {{
	   ?t a :Árbitro ;
       	  :nomePessoa ?nome ;
          :{at[0]} ?valor ;
          :jogosArbitro ?jogos .
}} ORDER BY DESC(?valor) ASC(?jogos) ASC(?nome) LIMIT 10
'''
        resultado = sparql_get_query(query)
        list = []
        for linha in resultado['results']['bindings']:
            list.append({
                'nome': linha['nome']['value'],
                'valor': linha['valor']['value'],
            })
        dict_arbitros[at[1]] = list

    at_jogadores = [('jogosJogador', 'Jogos'), ('minutosJogador', 'Minutos'), ('conducoesProgressivas', 'Conduções progressivas'), ('autoGolos', 'Autogolos')]
    at_jogadores += [('passesProgressivos', 'Passes progressivos'), ('golosJogador', 'Golos'), ('assistenciasJogador', 'Assistências'), ('percentagemPasses', 'Percentagem de passes acertados')]
    at_jogadores += [('caJogador', 'Cartões amarelos'), ('cvJogador', 'Cartões vermelhos'), ('keyPasses', 'Passes chave'), ('gca', 'Ações de criação de golo')]
    at_jogadores += [('intercecoes', 'Interceções'), ('toques', 'Toques na bola'), ('faltasCometidas', 'Faltas cometidas'), ('faltasSofridas', 'Faltas sofridas')]
    at_jogadores += [('forasDeJogo', 'Foras de jogo'), ('cruzamentos', 'Cruzamentos', 'autoGolos', 'Autogolos'), ('bolasRecuperadas', 'Bolas recuperadas')]
    at_jogadores += [('aereosGanhos', 'Percentagem de lances aéreos ganhos'), ('golosSofridosGR', 'Golos sofridos'), ('cleanSheets', 'Clean sheets')]
                     
    dict_jogadores = {}
    for at in at_jogadores:
        if at[0] not in ['jogosJogador', 'minutosJogador', 'caJogador', 'cvJogador', 'golosSofridosGR', 'cleanSheets']:
            query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>

SELECT ?nome ?valor ?clube ?nclube WHERE {{
    ?j a :Jogador ;
       :jogosJogador ?jogos ;
       :nomePessoa ?nome ;
       :{at[0]} ?valor ;
       :joga ?clube .
    ?clube :nomeClube ?nclube .
    FILTER (?jogos > 10)
    FILTER (NOT EXISTS {{ ?j :posicaoJogador "Guarda-redes" }})
}} ORDER BY DESC(?valor) ASC(?jogos) ASC(?nome) LIMIT 10
"""
        else:
            query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>

SELECT ?nome ?valor ?clube ?nclube WHERE {{
    ?j a :Jogador ;
       :jogosJogador ?jogos ;
       :nomePessoa ?nome ;
       :{at[0]} ?valor ;
       :joga ?clube .
    ?clube :nomeClube ?nclube .
    FILTER (?jogos > 10)
}} ORDER BY DESC(?valor) ASC(?jogos) ASC(?nome) LIMIT 10
"""
        resultado = sparql_get_query(query)
        list = []
        for linha in resultado['results']['bindings']:
            list.append({
                'nome': linha['nome']['value'],
                'valor': linha['valor']['value'],
                'clube': linha['clube']['value'].split('/')[-1],
                'nclube': linha['nclube']['value']
            })
        dict_jogadores[at[1]] = list

    double_at_jogadores = [('penaltisTentadosJogador', 'penaltisMarcadosJogador', 'Percentagem de penáltis convertidos')]
    double_at_jogadores += [('cortes', 'cortesGanhos', 'Percentagem de cortes bem sucedidos'), ('duelos', 'duelosGanhos', 'Percentagem de duelos ganhos')]
    double_at_jogadores += [('penaltisContraGR', 'penaltisDefendidosGR', 'Percentagem de penáltis defendidos')]

    for at in double_at_jogadores:
        if at[0] != 'penaltisContraGR':

            query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>

SELECT ?nome ?valor ?valorF ?clube ?nclube WHERE {{
    ?j a :Jogador ;
       :jogosJogador ?jogos ;
       :nomePessoa ?nome ;
       :{at[0]} ?valor ;
       :{at[1]} ?valorF ;
       :joga ?clube .
    ?clube :nomeClube ?nclube .
    FILTER (?jogos > 10)
    FILTER (NOT EXISTS {{ ?j :posicaoJogador "Guarda-redes" }})
}} ORDER BY DESC(?valor) ASC(?jogos) ASC(?nome) LIMIT 10
"""
        else:
            query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>

SELECT ?nome ?valor ?valorF ?clube ?nclube WHERE {{
    ?j a :Jogador ;
       :jogosJogador ?jogos ;
       :nomePessoa ?nome ;
       :{at[0]} ?valor ;
       :{at[1]} ?valorF ;
       :joga ?clube .
    ?clube :nomeClube ?nclube .
    FILTER (?jogos > 10)
}} ORDER BY DESC(?valor) ASC(?jogos) ASC(?nome) LIMIT 10
"""

        resultado = sparql_get_query(query)
        list = []
        for linha in resultado['results']['bindings']:
            list.append({
                'nome': linha['nome']['value'],
                'valor': round(float(linha['valorF']['value']) / float(linha['valor']['value']) * 100, 1),
                'clube': linha['clube']['value'].split('/')[-1],
                'nclube': linha['nclube']['value']
            })

        list = sorted(list, key=lambda x: x['valor'], reverse=True)
        dict_jogadores[at[2]] = list

    query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>

SELECT ?nome ?clube ?nclube ((?valor + ?valorF) AS ?value) WHERE {{
    ?j a :Jogador ;
       :jogosJogador ?jogos ;
       :nomePessoa ?nome ;
       :golosJogador ?valor ;
       :assistenciasJogador ?valorF ;
       :joga ?clube .
    ?clube :nomeClube ?nclube .
    FILTER (?jogos > 10)
}} ORDER BY DESC(?value) ASC(?jogos) ASC(?nome) LIMIT 10
"""
    resultado = sparql_get_query(query)
    list = []
    for linha in resultado['results']['bindings']:
        list.append({
            'nome': linha['nome']['value'],
            'valor': linha['value']['value'],
            'clube': linha['clube']['value'].split('/')[-1],
            'nclube': linha['nclube']['value']
        })
    dict_jogadores['G + A'] = list

    query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>

SELECT ?nome ?clube ?nclube ((?valor - ?valorF) AS ?value) WHERE {{
    ?j a :Jogador ;
       :jogosJogador ?jogos ;
       :nomePessoa ?nome ;
       :golosJogador ?valor ;
       :xgJogador ?valorF ;
       :joga ?clube .
    ?clube :nomeClube ?nclube .
    FILTER (?jogos > 10)
}} ORDER BY DESC(?value) ASC(?jogos) ASC(?nome) LIMIT 10
"""
    resultado = sparql_get_query(query)
    list = []
    for linha in resultado['results']['bindings']:
        list.append({
            'nome': linha['nome']['value'],
            'valor': f'+{round(float(linha["value"]["value"]),1)}',
            'clube': linha['clube']['value'].split('/')[-1],
            'nclube': linha['nclube']['value']
        })
    dict_jogadores['xG +/-'] = list

    query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>

SELECT ?nome ?clube ?nclube ?valor WHERE {{
    ?j a :Jogador ;
       :jogosJogador ?jogos ;
       :nomePessoa ?nome ;
       :valorJogador ?valor ;
       :joga ?clube .
    ?clube :nomeClube ?nclube .
    FILTER (?jogos > 10)
}}
"""
    resultado = sparql_get_query(query)
    list = []
    for linha in resultado['results']['bindings']:
        value = linha['valor']['value']
        if 'M' in value:
            value = float(value.replace(' M', ''))
        elif 'k' in value:
            value = float(value.replace(' k', '')) / 1000
        list.append({
            'nome': linha['nome']['value'],
            'valor': value,
            'clube': linha['clube']['value'].split('/')[-1],
            'nclube': linha['nclube']['value']
        })
    jogadores_ordenados = sorted(list, key=lambda x: x['valor'], reverse=True)[:10]
    dict_jogadores['Valor de mercado (€ M)'] = jogadores_ordenados

    query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>

SELECT ?nome ?clube ?nclube ((?valorF / ?valor) AS ?value) WHERE {{
    ?j a :Jogador ;
       :jogosJogador ?jogos ;
       :nomePessoa ?nome ;
       :golosJogador ?valor ;
       :minutosJogador ?valorF ;
       :joga ?clube .
    ?clube :nomeClube ?nclube .
    FILTER (?jogos > 10 && ?valor > 5)
}} ORDER BY (?value) ASC(?jogos) ASC(?nome) LIMIT 10
"""
    resultado = sparql_get_query(query)
    list = []
    for linha in resultado['results']['bindings']:
        list.append({
            'nome': linha['nome']['value'],
            'valor': round(float(linha['value']['value']),1),
            'clube': linha['clube']['value'].split('/')[-1],
            'nclube': linha['nclube']['value']
        })
    dict_jogadores['Minutos para golo'] = list

    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?c ?g ?gs ?v ?e ?d ?n WHERE {
    ?c a :Clube ;
           :nomeClube ?n .
}
'''
    resultado = sparql_get_query(query)
    tabela = []

    for linha in resultado['results']['bindings']:
        id = linha['c']['value'].split("/")[-1]

        tabela.append({
            'id': id,
            'clube': linha['n']['value'],
        })

    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>

SELECT (COUNT(?t) AS ?num) ?associacao WHERE {
    ?t a :Árbitro ;
       :associacaoArbitro ?associacao .
} GROUP BY ?associacao order by desc (?num) limit 10
'''

    resultado = sparql_get_query(query)
    tabelaAssoc = []

    for linha in resultado['results']['bindings']:
        assoc = linha['associacao']['value'],
        num = linha['num']['value']

        tabelaAssoc.append({
            'assoc': assoc[0],
            'num': num,
        })

    league_stat_selector = [
    ('vermelhosEquipa','Cartões vermelhos', 'Mais Cartões Vermelhos'), ('amarelosEquipa','Cartões Amarelos', 'Mais Cartões Amarelos'),
    ('penaltisFavorEquipa', 'Penáltis a Favor', 'Mais Penáltis a Favor'), ('penaltisContraEquipa', 'Penáltis Contra', 'Mais Penáltis Contra'),
    ('lotacaoMediaEquipa', 'Lotação Média', 'Maior Lotação Média'), ('lotacaoMediaEquipa', 'Taxa de ocupação (%)', 'Maior Taxa de Ocupação')
]

    dict_clubes = {}
    for selector in league_stat_selector:

        if selector[2] == 'Maior Taxa de Ocupação':
            query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?c ?nome ?valor ?ce ((?valor / ?ce) AS ?taxaOcupacao) WHERE {{
        ?c a :Clube ;
           :temEstadio ?e ;
           :nomeClube ?nome ;
           :lotacaoMediaEquipa ?valor .
        ?e :capacidadeEstadio ?ce .
}} ORDER BY DESC(?taxaOcupacao) LIMIT 10
    '''
            clubs = []
            resultado = sparql_get_query(query)
            for linha in resultado['results']['bindings']:
                clubs.append({
                       'id': linha['c']['value'].split("/")[-1],
                       'nome': linha['nome']['value'],
                       'stat': round(float(linha['taxaOcupacao']['value'])*100,1)
                   })
            dict_clubes[selector[2]] = [selector[1], clubs]
            
        else:
            query = f'''
        PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
        SELECT * WHERE {{
            ?c a :Clube ;
               :temEstadio ?e ;
               :nomeClube ?nome ;
               :{selector[0]} ?valor .
            ?e :capacidadeEstadio ?ce .
        }} ORDER BY DESC (?valor) ASC(?nome) LIMIT 10
        '''
            resultado = sparql_get_query(query)

            clubs = []
            for linha in resultado['results']['bindings']:
                clubs.append({
                    'id': linha['c']['value'].split("/")[-1],
                    'nome': linha['nome']['value'],
                    'stat': linha['valor']['value']
                })
            dict_clubes[selector[2]] = [selector[1], clubs]
        
    query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?c ?nome ((?valor - ?valorF) AS ?value) WHERE {{
        ?c a :Clube ;
           :nomeClube ?nome ;
           :xgEquipa ?valorF ;
           :golosEquipa ?valor .
}} ORDER BY DESC (?value) ASC(?nome) LIMIT 10
    '''
    resultado = sparql_get_query(query)
    clubs = []
    for linha in resultado['results']['bindings']:
        clubs.append({
            'id': linha['c']['value'].split("/")[-1],
            'nome': linha['nome']['value'],
            'stat': f'+{round(float(linha["value"]["value"]),1)}'
        })
    dict_clubes['xG +/-'] = ['xG +/-', clubs]

    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?clube ?nomeClube (SUM(?valorJogador) AS ?valorTotalPlantel) WHERE {
    ?jogador a :Jogador ;
             :joga ?clube ;
             :valorJogador ?valor .
    ?clube :nomeClube ?nomeClube .
    BIND(
        IF(CONTAINS(?valor, "M"), xsd:float(STRBEFORE(?valor, " M")),
        IF(CONTAINS(?valor, "k"), xsd:float(STRBEFORE(?valor, " k")) / 1000, 0.0))
        AS ?valorJogador
    )
}
GROUP BY ?clube ?nomeClube
ORDER BY DESC(?valorTotalPlantel)
LIMIT 10
'''
    resultado = sparql_get_query(query)
    clubs = []
    for linha in resultado['results']['bindings']:
        clubs.append({
            'id': linha['clube']['value'].split("/")[-1],
            'nome': linha['nomeClube']['value'],
            'stat': round(float(linha['valorTotalPlantel']['value']),1)
        })
    dict_clubes['Valor de mercado do plantel (M €)'] = ['Valor de mercado do plantel (M €)', clubs]

    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?clube ?nomeClube ?nomeJogador ?dataNascimento WHERE {
    ?jogador a :Jogador ;
             :joga ?clube ;
             :dataNascimento ?dataNascimento ;
             :nomePessoa ?nomeJogador .
    ?clube :nomeClube ?nomeClube .
}
'''
    resultado = sparql_get_query(query)
    
    clubes = {}

    for linha in resultado['results']['bindings']:
        id = linha['clube']['value'].split("/")[-1],
        nome_clube = linha['nomeClube']['value']
        data_nascimento = linha['dataNascimento']['value']
        nascimento = datetime.datetime.strptime(data_nascimento, "%d/%m/%Y")
        hoje = datetime.datetime.today()
        idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
    
        if nome_clube not in clubes:
            clubes[nome_clube] = {'id': id, 'idades': []}
    
        clubes[nome_clube]['idades'].append(idade)
        
    idade_media_plantel = {clube: sum(data['idades']) / len(data['idades']) for clube, data in clubes.items()}
    clubes_ordenados = sorted(idade_media_plantel.items(), key=lambda x: x[1])[:10]

    clubs = []
    for clube, idade_media in clubes_ordenados:
        clubs.append({'id': clubes[clube]['id'][0], 'nome': clube, 'stat': round(idade_media, 1)})

    dict_clubes['Idade média do plantel'] = ['Idade média do plantel', clubs]

    dict_resultados = {}
    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?jornada (SUM(?golsCasa + ?golsFora) AS ?totalGoals) WHERE {
    ?jogo a :Jogo ;
          :jornada ?jornada ;
          :resultado ?resultado .
    BIND (STRAFTER(?resultado, "-") AS ?golsVisitanteStr)
    BIND (STRBEFORE(?resultado, "-") AS ?golsCasaStr)
    BIND (xsd:integer(?golsCasaStr) AS ?golsCasa)
    BIND (xsd:integer(?golsVisitanteStr) AS ?golsFora)
}
GROUP BY ?jornada
ORDER BY DESC(?totalGoals)
LIMIT 10
'''
    resultado = sparql_get_query(query)
    resultados = []
    for linha in resultado['results']['bindings']:
        resultados.append({
            'nome': linha['jornada']['value'],
            'stat': linha['totalGoals']['value']
        })
    dict_resultados['Golos'] = ['Golos', resultados]

    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?jogo ?casa ?fora ?resultado ?ncasa ?nfora (SUM(?golsCasa + ?golsFora) AS ?totalGoals) WHERE {
    ?jogo a :Jogo ;
          :resultado ?resultado ;
          :equipaCasa ?casa ;
          :equipaFora ?fora .
    ?casa :nomeClube ?ncasa .
    ?fora :nomeClube ?nfora .
    BIND (STRAFTER(?resultado, "-") AS ?golsVisitanteStr)
    BIND (STRBEFORE(?resultado, "-") AS ?golsCasaStr)
    BIND (xsd:integer(?golsCasaStr) AS ?golsCasa)
    BIND (xsd:integer(?golsVisitanteStr) AS ?golsFora)
}
GROUP BY ?jogo ?casa ?fora ?resultado ?ncasa ?nfora
ORDER BY DESC(?totalGoals)
LIMIT 10
'''
    resultado = sparql_get_query(query)
    resultados = []
    for linha in resultado['results']['bindings']:
        resultados.append({
            'casa': linha['casa']['value'].split("/")[-1],
            'fora': linha['fora']['value'].split("/")[-1],
            'nome': linha['resultado']['value'].replace('-', '  - '),
            'stat': linha['totalGoals']['value'],
            'ncasa': linha['ncasa']['value'],
            'nfora': linha['nfora']['value']
        })
    dict_resultados['Total de Golos'] = ['Golos', resultados]

    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?jornada (SUM (?espectadores) AS ?totalEspectadores) WHERE {
    ?jogo a :Jogo ;
          :jornada ?jornada ;
          :espectadores ?espectadores .
}
GROUP BY ?jornada
ORDER BY DESC(?totalEspectadores)
LIMIT 10
'''
    resultado = sparql_get_query(query)
    resultados = []
    for linha in resultado['results']['bindings']:
        resultados.append({
            'nome': linha['jornada']['value'],
            'stat': linha['totalEspectadores']['value']
        })
    dict_resultados['Espectadores Acumulados'] = ['Espectadores', resultados]

    return jsonify({'arbitros': dict_arbitros, 'jogadores': dict_jogadores, 'clubes': dict_clubes , 'resultados': dict_resultados, 'tabela': tabela, 'tabelaAssoc': tabelaAssoc}), 200


@app.get('/gerir')
def gerir():
    msg, code = check_token()
    if code != 200:
        return msg, code
    
    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT * WHERE {
    ?c a :Clube ;
       :nomeClube ?nc .
    ?j a :Jogador ;
       :joga ?c ;
	   :nomePessoa ?np .
} ORDER BY(?np)
'''
    resultado = sparql_get_query(query)
    clubes = {}
    for linha in resultado['results']['bindings']:
        iclube = linha['c']['value'].split('/')[-1]
        if iclube not in clubes:
            clubes[iclube] = {
                'jogadores': [],
                'nome': linha['nc']['value']
            }
        clubes[iclube]['jogadores'].append((linha['j']['value'].split('/')[-1], linha['np']['value']))
    
    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?c ?g ?gs ?v ?e ?d ?n WHERE {
    ?c a :Clube ;
           :nomeClube ?n .
}
'''
    resultado = sparql_get_query(query)
    tabela = []

    for linha in resultado['results']['bindings']:
        id = linha['c']['value'].split("/")[-1]

        tabela.append({
            'id': id,
            'clube': linha['n']['value'],
        })

    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?a ?np WHERE {
    ?a a :Árbitro ;
       :nomePessoa ?np .
} ORDER BY (?np)
'''
    resultado = sparql_get_query(query)
    arbitros = {}
    for linha in resultado['results']['bindings']:
        id = linha['a']['value'].split("/")[-1]
        arbitros[id] = linha['np']['value']

    query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
SELECT ?t ?np WHERE {
    ?t a :Treinador ;
       :nomePessoa ?np .
} ORDER BY (?np)
'''
    resultado = sparql_get_query(query)
    treinadores = {}
    for linha in resultado['results']['bindings']:
        id = linha['t']['value'].split("/")[-1]
        treinadores[id] = linha['np']['value']

    return jsonify({'info': clubes, 'tabela': tabela, 'arbitros': arbitros, 'treinadores': treinadores}), 200


@app.post('/adicionar_jogador')
def post_jogador():
    dados = request.json

    int_keys = ['assistenciasJogador', 'autoGolos', 'bolasRecuperadas', 'caJogador', 'conducoesProgressivas', 'cortes', 'cortesGanhos', 'cruzamentos', 'cvJogador']
    int_keys += ['duelos', 'duelosGanhos', 'faltasCometidas', 'faltasSofridas', 'forasDeJogo', 'gca', 'golosJogador', 'intercecoes', 'jogosJogador', 'keyPasses']
    int_keys += ['minutosJogador', 'numeroJogador', 'passesCompletos', 'passesProgressivos', 'penaltisMarcadosJogador', 'penaltisTentadosJogador', 'rematesBalizaJogador']
    int_keys += ['rematesJogador', 'toques']
    float_keys = ['aereosGanhos', 'percentagemPasses', 'xaJogador', 'xgJogador']

    if not dados:
        return jsonify({"erro": "Não foram enviados dados do jogador a criar..."}), 400
    else:
        triplos = []
        for key in dados:
            if key == 'joga':
                triplos.append(f":{dados['id']} :{key} :{dados[key]} .")
            elif key != 'id':
                if key in int_keys:
                    triplos.append(f":{dados['id']} :{key} \"{dados[key]}\"^^xsd:int .")
                elif key in float_keys:
                    triplos.append(f":{dados['id']} :{key} \"{dados[key]}\"^^xsd:float .")

                else:
                    triplos.append(f":{dados['id']} :{key} \"{dados[key]}\" .")

    content = '\n'.join(triplos)
    query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
INSERT DATA {{
    :{dados['id']} a :Jogador, owl:NamedIndividual .
    {content}
}}
"""
    sparql_post_query(query)
    return jsonify({'mensagem':f"Jogador criado com sucesso: {dados['id']}"}), 200


@app.post('/adicionar_treinador')
def post_treinador():
    dados = request.json

    int_keys = ['derrotasTreinador', 'vitoriasTreinador', 'empatesTreinador']

    if not dados:
        return jsonify({"erro": "Não foram enviados dados do treinador a criar..."}), 400
    else:
        triplos = []
        for key in dados:
            if key == 'treina':
                triplos.append(f":{dados['id']} :{key} :{dados[key]} .")
            elif key != 'id':
                if key in int_keys:
                    triplos.append(f":{dados['id']} :{key} \"{dados[key]}\"^^xsd:int .")
                else:
                    triplos.append(f":{dados['id']} :{key} \"{dados[key]}\" .")

    content = '\n'.join(triplos)
    query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
INSERT DATA {{
    :{dados['id']} a :Treinador, owl:NamedIndividual .
    {content}
}}
"""
    sparql_post_query(query)
    return jsonify({'mensagem':f"Treinador criado com sucesso: {dados['id']}"}), 200


@app.post('/adicionar_arbitro')
def post_arbitro():
    dados = request.json

    int_keys = ['amarelosArbitro', 'vermelhosArbitro', 'duplosAmarelosArbitro', 'jogosArbitro', 'penaltisArbitro']

    if not dados:
        return jsonify({"erro": "Não foram enviados dados do árbitro a criar..."}), 400
    else:
        triplos = []
        for key in dados:
            if key != 'id':
                if key in int_keys:
                    triplos.append(f":{dados['id']} :{key} \"{dados[key]}\"^^xsd:int .")
                else:
                    triplos.append(f":{dados['id']} :{key} \"{dados[key]}\" .")

    content = '\n'.join(triplos)
    query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
INSERT DATA {{
    :{dados['id']} a :Árbitro, owl:NamedIndividual .
    {content}
}}
"""
    sparql_post_query(query)
    return jsonify({'mensagem':f"Árbitro criado com sucesso: {dados['id']}"}), 200


@app.delete('/apagar_registo/<id>')
def delete(id):
    query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
    DELETE {{
        :{id} ?p ?o .
    }}
    WHERE {{
        :{id} ?p ?o .
    }}
"""
    sparql_post_query(query)
    return jsonify({"mensagem": 'Registo de jogador removido com sucesso!'}), 200


@app.put('/editar_treinador/<idTreinador>')
def update_treinador(idTreinador):
    dados = request.json

    int_keys = ['amarelosArbitro', 'vermelhosArbitro', 'duplosAmarelosArbitro', 'jogosArbitro', 'penaltisArbitro']

    if not dados:
        return jsonify({"erro": "Não foram enviados dados do treinador a alterar..."}), 400
    else:
        triplos_apagar = []
        triplos_inserir = []

        for key in dados:
            if key == 'treina':
                triplos_apagar.append(f":{dados['id']} :{key} ?o .")
                triplos_inserir.append(f":{dados['id']} :{key} :{dados[key]} .")
            elif key != 'id':
                if key in int_keys:
                    triplos_apagar.append(f":{dados['id']} :{key} ?o .")
                    triplos_inserir.append(f":{dados['id']} :{key} \"{dados[key]}\"^^xsd:int .")
                else:
                    triplos_apagar.append(f":{dados['id']} :{key} ?o .")
                    triplos_inserir.append(f":{dados['id']} :{key} \"{dados[key]}\" .")


        content_apagar = "\n".join(triplos_apagar)
        content_inserir = "\n".join(triplos_inserir)
        query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
DELETE{{
    {content_apagar}
}}
INSERT{{
    {content_inserir}
}}
WHERE{{
    :{idTreinador} ?p ?o . 
}}
            """
        sparql_post_query(query)
        return jsonify({"mensagem": f"Treinador alterado com sucesso: {idTreinador}"}), 200


@app.put('/editar_arbitro/<idArbitro>')
def update_arbitro(idArbitro):
    dados = request.json

    int_keys = ['amarelosArbitro', 'vermelhosArbitro', 'duplosAmarelosArbitro', 'jogosArbitro', 'penaltisArbitro']
    
    if not dados:
        return jsonify({"erro": "Não foram enviados dados do árbitro a alterar..."}), 400

    else:
        triplos_apagar = []
        triplos_inserir = []

        for key in dados:
            
            if key != 'id':
                if key in int_keys:
                    triplos_apagar.append(f":{dados['id']} :{key} ?o .")
                    triplos_inserir.append(f":{dados['id']} :{key} \"{dados[key]}\"^^xsd:int .")
                else:
                    triplos_apagar.append(f":{dados['id']} :{key} ?o .")
                    triplos_inserir.append(f":{dados['id']} :{key} \"{dados[key]}\" .")


        content_apagar = "\n".join(triplos_apagar)
        content_inserir = "\n".join(triplos_inserir)
        query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
DELETE{{
    {content_apagar}
}}
INSERT{{
    {content_inserir}
}}
WHERE{{
    :{idArbitro} ?p ?o . 
}}
            """
        sparql_post_query(query)
        return jsonify({"mensagem": f"Árbitro alterado com sucesso: {idArbitro}"}), 200


@app.put('/editar_jogador/<idJogador>')
def update_jogador(idJogador):
    dados = request.json

    int_keys = ['assistenciasJogador', 'autoGolos', 'bolasRecuperadas', 'caJogador', 'conducoesProgressivas', 'cortes', 'cortesGanhos', 'cruzamentos', 'cvJogador']
    int_keys += ['duelos', 'duelosGanhos', 'faltasCometidas', 'faltasSofridas', 'forasDeJogo', 'gca', 'golosJogador', 'intercecoes', 'jogosJogador', 'keyPasses']
    int_keys += ['minutosJogador', 'numeroJogador', 'passesCompletos', 'passesProgressivos', 'penaltisMarcadosJogador', 'penaltisTentadosJogador', 'rematesBalizaJogador']
    int_keys += ['rematesJogador', 'toques']
    float_keys = ['aereosGanhos', 'percentagemPasses', 'xaJogador', 'xgJogador']
    
    if not dados:
        return jsonify({"erro": "Não foram enviados dados do árbitro a alterar..."}), 400
    
    else:
        triplos_apagar = []
        triplos_inserir = []

        for key in dados:

            if key == 'joga':
                triplos_apagar.append(f":{dados['id']} :{key} ?o .")
                triplos_inserir.append(f":{dados['id']} :{key} :{dados[key]} .")
            elif key != 'id':
                if key in int_keys:
                    triplos_apagar.append(f":{dados['id']} :{key} ?o .")
                    triplos_inserir.append(f":{dados['id']} :{key} \"{dados[key]}\"^^xsd:int .")
                elif key in float_keys:
                    triplos_apagar.append(f":{dados['id']} :{key} ?o .")
                    triplos_inserir.append(f":{dados['id']} :{key} \"{dados[key]}\"^^xsd:float .")
                else:
                    triplos_apagar.append(f":{dados['id']} :{key} ?o .")
                    triplos_inserir.append(f":{dados['id']} :{key} \"{dados[key]}\" .")

        content_apagar = "\n".join(triplos_apagar)
        content_inserir = "\n".join(triplos_inserir)
        query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/gfootdz/>
DELETE{{
    {content_apagar}
}}
INSERT{{
    {content_inserir}
}}
WHERE{{
    :{idJogador} ?p ?o . 
}}
            """
        sparql_post_query(query)
    
        return jsonify({"mensagem": f"Jogador alterado com sucesso: {idJogador}"}), 200


if __name__ == '__main__':
    app.run(port=23241, debug=True)