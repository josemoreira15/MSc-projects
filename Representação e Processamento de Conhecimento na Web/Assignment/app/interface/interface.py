from flask import Flask, redirect, render_template, request, url_for
import bcrypt, os, requests

app = Flask(__name__)
app.config['UPLOAD_FOLDER_JOGADORES'] = 'static/images/jogadores'
app.config['UPLOAD_FOLDER_TREINADORES'] = 'static/images/treinadores'
app.config['UPLOAD_FOLDER_ARBITROS'] = 'static/images/arbitros'
AUTH_URL = 'http://127.0.0.1:23240'
API_URL = 'http://127.0.0.1:23241'
CLIENT = None
TOKEN = None


COLORS = {
    'C1': '#008057',
    'C2': '#e71c23',
    'C3': '#00428c',
    'C4': '#e70200',
    'C5': '#000000',
    'C6': '#145f24',
    'C7': '#fce901',
    'C8': '#20447b',
    'C9': '#030304',
    'C10': '#231f20',
    'C11': '#009036',
    'C12': '#fe2120',
    'C13': '#fff200',
    'C14': '#3d8f47',
    'C15': '#000000',
    'C16': '#000000',
    'C17': '#114093',
    'C18': '#ab0e32'
}


player_general_properties = [
    ('nomePessoa', 'Nome', 'Nome'), ('nomeCompleto', 'Nome Completo', 'Nome Completo'), ('dataNascimento', 'Data de Nascimento', 'DD/MM/YYYY'),
    ('nacionalidade', 'País', 'País'), ('alturaJogador', 'Altura', '0'), ('numeroJogador', 'Número da camisola', '0'), ('posicaoJogador', 'Posição', 'Posição'),
    ('peJogador', 'Pé Preferencial', 'Pé'), ('jogosJogador', 'Nº de Jogos', '0'), ('minutosJogador', 'Nº de Minutos Jogados', '0'), ('valorJogador', 'Valor de Mercado (M €)', '0')
]


player_offensive_properties = [
    ('assistenciasJogador', 'Assistências', '0'), ('conducoesProgressivas', 'Conduções Progressivas', '0'), ('cruzamentos', 'Cruzamentos', '0'),
    ('faltasSofridas', 'Faltas Sofridas', '0'), ('forasDeJogo', 'Foras de Jogo', '0'), ('gca', 'Ações de Criação de Golo', '0'), ('golosJogador', 'Golos', '0'),
    ('keyPasses', 'Passes Chave', '0'), ('passesCompletos', 'Passes Completos', '0'), ('passesProgressivos', 'Passes Progressivos', '0'),
    ('penaltisMarcadosJogador', 'Penáltis Convertidos', '0'), ('penaltisTentadosJogador', 'Penáltis Batidos', '0'), ('percentagemPasses', 'Percentagem de Acerto de Passes', '0.0'),
    ('rematesBalizaJogador', 'Remates à Baliza', '0'), ('rematesJogador', 'Remates Efetuados', '0'), ('toques', 'Toques na Bola', '0'),
    ('xaJogador', 'xAssists', '0.0'), ('xgJogador', 'xGoals', '0.0')
]


player_deffensive_properties = [
    ('aereosGanhos', 'Percentagem de duelos aéreos ganhos', '0.0'), ('autoGolos', 'AutoGolos', '0'), ('bolasRecuperadas', 'Bolas recuperadas', ''),
    ('caJogador', 'Cartões Amarelos', '0'), ('cortes', 'Cortes', '0'), ('cortesGanhos', 'Cortes ganhos', '0'), ('cvJogador', 'Cartões Vermelhos', '0'),
    ('duelos', 'Duelos', '0'), ('duelosGanhos', 'Duelos Ganhos', '0'), ('faltasCometidas', 'Faltas Cometidas', '0'), ('intercecoes', 'Interceções', '0')
]


player_gr_properties = [
    ('cleanSheets', 'Jogos sem sofrer golos', '0'), ('golosSofridosGR', 'Golos sofridos', '0'), ('penaltisContraGR', 'Penáltis Enfrentados', '0'), ('penaltisDefendidosGR', 'Penáltis Defendidos', '0'),
    ('rematesSofridosGR', 'Remates Enfrentados', '0'), ('xgSofridosGR', 'Golos sofridos esperados', '0.0')
]


coach_properties = [
    ('nomePessoa', 'Nome', 'Nome'), ('nomeCompleto', 'Nome Completo', 'Nome Completo'), ('dataNascimento', 'Data de Nascimento', 'DD/MM/YYYY'),
    ('nacionalidade', 'País', 'País'), ('vitoriasTreinador', 'Nº de Vitórias', '0'),  ('empatesTreinador', 'Nº de Empates', '0'),  ('derrotasTreinador', 'Nº de Derrotas', '0'), ('formacaoTreinador', 'Formação mais Utilziada', 'Formação')
]


referee_properties = [
    ('nomePessoa', 'Nome', 'Nome'), ('nomeCompleto', 'Nome Completo', 'Nome Completo'), ('dataNascimento', 'Data de Nascimento', 'DD/MM/YYYY'),
    ('nacionalidade', 'País', 'País'), ('associacaoArbitro', 'Associação de Futebol', 'Associação'), ('amarelosArbitro', 'Amarelos', '0'),
    ('vermelhosArbitro', 'Vermelhos', '0'), ('duplosAmarelosArbitro', 'Duplos Amarelos', '0'), ('jogosArbitro','Nº de Jogos', '0') ,('penaltisArbitro', 'Penáltis Assinalados', '0')
]


@app.get('/')
def index():
    response = requests.get(f'{API_URL}/')
    return render_template('index.html', data={'client': CLIENT, 'data': response.json()})


@app.get('/entrar')
def login_page(error=''):
    if CLIENT == None:
        return render_template('entrar.html', data={'error': error})
    
    else:
        return redirect(url_for('index'))


@app.post('/entrar')
def login():
    response = requests.post(f'{AUTH_URL}/entrar', json={'username': request.form.get('username'), 'password': request.form.get('password')})

    if response.status_code == 200:
        data = response.json()
        global CLIENT, TOKEN
        CLIENT = data.get('username')
        TOKEN = data.get('token')

        return redirect(url_for('index'))

    else:
        return login_page(error='Credenciais inválidas!')

@app.post('/sair')
def logout():
    global CLIENT, TOKEN

    headers = {'Authorization': f'Bearer {TOKEN}'}
    response = requests.post(f'{AUTH_URL}/sair', json={'username': CLIENT}, headers=headers)

    if response.status_code == 200:
        CLIENT = None
        TOKEN = None
    
    return redirect(url_for('index'))


@app.get('/clubes/<id>')
def clube(id):
    response = requests.get(f'{API_URL}/clubes/{id}')
    return render_template('clube.html', data={'client': CLIENT, 'color': COLORS[id], 'club': id, 'data': response.json()})


@app.get('/arbitros')
def arbitros():
    response = requests.get(f'{API_URL}/arbitros')
    return render_template('arbitros.html', data={'client': CLIENT, 'arbitros': response.json()})


@app.get('/treinadores')
def treinadores():
    response = requests.get(f'{API_URL}/treinadores')
    return render_template('treinadores.html', data={'client': CLIENT, 'treinadores': response.json()})


@app.get('/lideres')
def lideres():
    response = requests.get(f'{API_URL}/lideres')
    return render_template('lideres.html', data={'client': CLIENT, 'data': response.json()})


@app.get('/gerir')
def gerir():
    message = request.args.get('message', '.')
    headers = {'Authorization': f'Bearer {TOKEN}'}
    response = requests.get(f'{API_URL}/gerir', headers=headers)

    if response.status_code == 200:
        content = response.json()
        content['info'] = dict(sorted(content['info'].items(), key=lambda item: item[1]['nome']))
        content['arbitros'] = dict(sorted(content['arbitros'].items(), key=lambda item: item[1]))
        content['treinadores'] = dict(sorted(content['treinadores'].items(), key=lambda item: item[1]))
        return render_template('gerir.html', data={'client': CLIENT, 'data': content, 'message': message, 'player_general_properties': player_general_properties, 'player_offensive_properties': player_offensive_properties, 'player_deffensive_properties': player_deffensive_properties, 'coach_properties': coach_properties, 'referee_properties': referee_properties, 'player_gr_properties': player_gr_properties})
    else:
        return redirect(url_for('index'))
    

@app.post('/remover')
def remover():
    pessoa = request.form.get('pessoa')
    clube = request.form.get('clube')
    
    resposta = requests.delete(f'{API_URL}/apagar_registo/{pessoa}', json={'pessoa': pessoa})
    if resposta.status_code == 200:
        if pessoa[0] == 'P':
            path = os.path.join('static', 'images', 'jogadores', clube, f'{pessoa}.png')
        elif pessoa[0] == 'A':
            path = os.path.join('static', 'images', 'arbitros', f'{pessoa}.png')
        else:
            path = os.path.join('static', 'images', 'treinadores', f'{pessoa}.png')

        os.remove(path)
        message = 'Registo removido com sucesso!'

    else:
        message = 'Não foi possível remover o registo!'

    return redirect(url_for('gerir', message=message))


@app.post('/adicionar_jogador')
def adicionar_jogador():
    response = requests.get(f'{API_URL}/jogadores')
    id_num = int(response.json()["last"][2:]) + 1

    jogador = {
        'id': f'PL{id_num}',
        'joga': request.form['clube'],
        'alturaJogador': request.form['alturaJogador'],
        'dataNascimento': request.form['dataNascimento'],
        'jogosJogador': request.form['jogosJogador'],
        'minutosJogador': request.form['minutosJogador'],
        'nacionalidade': request.form['nacionalidade'],
        'nomeCompleto': request.form['nomeCompleto'],
        'nomePessoa': request.form['nomePessoa'],
        'numeroJogador': request.form['numeroJogador'],
        'peJogador': request.form['peJogador'],
        'posicaoJogador': request.form['posicaoJogador'],
        'valorJogador': f"{request.form['valorJogador']} M",
        'assistenciasJogador': request.form['assistenciasJogador'],
        'conducoesProgressivas': request.form['conducoesProgressivas'],
        'cruzamentos': request.form['cruzamentos'],
        'faltasSofridas': request.form['faltasSofridas'],
        'forasDeJogo': request.form['forasDeJogo'],
        'gca': request.form['gca'],
        'golosJogador': request.form['golosJogador'],
        'keyPasses': request.form['keyPasses'],
        'passesCompletos': request.form['passesCompletos'],
        'passesProgressivos': request.form['passesProgressivos'],
        'penaltisMarcadosJogador': request.form['penaltisMarcadosJogador'],
        'penaltisTentadosJogador': request.form['penaltisTentadosJogador'],
        'percentagemPasses': request.form['percentagemPasses'],
        'rematesBalizaJogador': request.form['rematesBalizaJogador'],
        'rematesJogador': request.form['rematesJogador'],
        'toques': request.form['toques'],
        'xaJogador': request.form['xaJogador'],
        'xgJogador': request.form['xgJogador'],
        'aereosGanhos': request.form['aereosGanhos'],
        'autoGolos': request.form['autoGolos'],
        'bolasRecuperadas': request.form['bolasRecuperadas'],
        'caJogador': request.form['caJogador'],
        'cortes': request.form['cortes'],
        'cortesGanhos': request.form['cortesGanhos'],
        'cvJogador': request.form['cvJogador'],
        'duelos': request.form['duelos'],
        'duelosGanhos': request.form['duelosGanhos'],
        'faltasCometidas': request.form['faltasCometidas'],
        'intercecoes': request.form['intercecoes']
    }

    if request.form['posicaoJogador'] == 'Guarda-redes':
        for key, _, _ in player_gr_properties:
            jogador[key] = request.form[key]

    resposta = requests.post(f'{API_URL}/adicionar_jogador', json=jogador)
    if resposta.status_code == 200:
        foto = request.files['foto']
        foto.save(os.path.join(app.config['UPLOAD_FOLDER_JOGADORES'], f'{request.form["clube"]}/PL{id_num}.png'))

        return redirect(url_for('clube', id=request.form['clube']))
    else:
        return redirect(url_for('index'))


@app.post('/adicionar_treinador')
def adicionar_treinador():
    response = requests.get(f'{API_URL}/treinadores')
    id_num = int(response.json()["last"][1:]) + 1
    treinador = {
        'id': f'T{id_num}',
        'treina': request.form['clube'],
        'nomePessoa': request.form['nomePessoa'],
        'nomeCompleto': request.form['nomeCompleto'],
        'dataNascimento': request.form['dataNascimento'],
        'nacionalidade': request.form['nacionalidade'],
        'vitoriasTreinador': request.form['vitoriasTreinador'],
        'empatesTreinador': request.form['empatesTreinador'],
        'derrotasTreinador': request.form['derrotasTreinador'],
        'formacaoTreinador': request.form['formacaoTreinador']
    }

    resposta = requests.post(f'{API_URL}/adicionar_treinador', json=treinador)
    if resposta.status_code == 200:
        foto = request.files['foto']
        foto.save(os.path.join(app.config['UPLOAD_FOLDER_TREINADORES'], f'T{id_num}.png'))
        return redirect(url_for('treinadores'))
    else:
        return redirect(url_for('index'))
    

@app.post('/adicionar_arbitro')
def adicionar_arbitro():
    response = requests.get(f'{API_URL}/arbitros')
    id_num = int(response.json()["last"][1:]) + 1
    arbitro = {
        'id': f'A{id_num}',
        'nomePessoa': request.form['nomePessoa'],
        'nomeCompleto': request.form['nomeCompleto'],
        'dataNascimento': request.form['dataNascimento'],
        'nacionalidade': request.form['nacionalidade'],
        'associacaoArbitro': request.form['associacaoArbitro'],
        'amarelosArbitro': request.form['amarelosArbitro'],
        'vermelhosArbitro': request.form['vermelhosArbitro'],
        'duplosAmarelosArbitro': request.form['duplosAmarelosArbitro'],
        'jogosArbitro': request.form['jogosArbitro'],
        'penaltisArbitro': request.form['penaltisArbitro']
    }

    resposta = requests.post(f'{API_URL}/adicionar_arbitro', json=arbitro)
    if resposta.status_code == 200:
        foto = request.files['foto']
        foto.save(os.path.join(app.config['UPLOAD_FOLDER_ARBITROS'], f'A{id_num}.png'))
        return redirect(url_for('arbitros'))
    else:
        return redirect(url_for('index'))
    

@app.post('/editar_registo')
def editar_registo():
    tipo = request.form['tipo']

    if tipo == 'treinador':
        response = requests.get(f'{API_URL}/treinadores/{request.form["select"]}')
        if response.status_code == 200:
            return render_template('editar_treinador.html', data={'client': CLIENT, 'data': response.json(), 'coach_properties': coach_properties})
        else:
            return redirect(url_for('index'))
    

    elif tipo == 'arbitro':
        response = requests.get(f'{API_URL}/arbitros/{request.form["select"]}')
        if response.status_code == 200:
            return render_template('editar_arbitro.html', data={'client': CLIENT, 'data': response.json(), 'referee_properties': referee_properties})
        else:
            return redirect(url_for('index'))
        
    elif tipo == 'jogador':
        response = requests.get(f'{API_URL}/jogadores/{request.form["pessoa"]}')
        if response.status_code == 200:
            return render_template('editar_jogador.html', data={'client': CLIENT, 'data': response.json(), 'player_general_properties': player_general_properties, 'player_offensive_properties': player_offensive_properties, 'player_deffensive_properties': player_deffensive_properties, 'player_gr_properties': player_gr_properties})
        else:
            return redirect(url_for('index'))


@app.post('/editar_treinador/<idTreinador>')
def editar_treinador(idTreinador):

    treinador = {
        'id': f'{idTreinador}',
        'treina': request.form['clube'],
        'nomePessoa': request.form['nomePessoa'],
        'nomeCompleto': request.form['nomeCompleto'],
        'dataNascimento': request.form['dataNascimento'],
        'nacionalidade': request.form['nacionalidade'],
        'vitoriasTreinador': request.form['vitoriasTreinador'],
        'empatesTreinador': request.form['empatesTreinador'],
        'derrotasTreinador': request.form['derrotasTreinador'],
        'formacaoTreinador': request.form['formacaoTreinador']
    }
    
    response = requests.put(f'{API_URL}/editar_treinador/{idTreinador}', json=treinador)
    if response.status_code == 200:
        return redirect(url_for('treinadores'))
    else:
        return redirect(url_for('index'))


@app.post('/editar_arbitro/<idArbitro>')
def editar_arbitro(idArbitro):

    arbitro = {
        'id': f'{idArbitro}',
        'nomePessoa': request.form['nomePessoa'],
        'nomeCompleto': request.form['nomeCompleto'],
        'dataNascimento': request.form['dataNascimento'],
        'nacionalidade': request.form['nacionalidade'],
        'associacaoArbitro': request.form['associacaoArbitro'],
        'amarelosArbitro': request.form['amarelosArbitro'],
        'vermelhosArbitro': request.form['vermelhosArbitro'],
        'duplosAmarelosArbitro': request.form['duplosAmarelosArbitro'],
        'jogosArbitro': request.form['jogosArbitro'],
        'penaltisArbitro': request.form['penaltisArbitro']
    }

    response = requests.put(f'{API_URL}/editar_arbitro/{idArbitro}', json=arbitro)
    if response.status_code == 200:
        return redirect(url_for('arbitros'))
    else:
        return redirect(url_for('index'))


@app.post('/editar_jogador/<idJogador>')
def editar_jogador(idJogador):

    jogador = {
        'id': f'{idJogador}',
        'joga': request.form['clube'],
        'alturaJogador': request.form['alturaJogador'],
        'dataNascimento': request.form['dataNascimento'],
        'jogosJogador': request.form['jogosJogador'],
        'minutosJogador': request.form['minutosJogador'],
        'nacionalidade': request.form['nacionalidade'],
        'nomeCompleto': request.form['nomeCompleto'],
        'nomePessoa': request.form['nomePessoa'],
        'numeroJogador': request.form['numeroJogador'],
        'peJogador': request.form['peJogador'],
        'posicaoJogador': request.form['posicaoJogador'],
        'valorJogador': f"{request.form['valorJogador']}",
        'assistenciasJogador': request.form['assistenciasJogador'],
        'conducoesProgressivas': request.form['conducoesProgressivas'],
        'cruzamentos': request.form['cruzamentos'],
        'faltasSofridas': request.form['faltasSofridas'],
        'forasDeJogo': request.form['forasDeJogo'],
        'gca': request.form['gca'],
        'golosJogador': request.form['golosJogador'],
        'keyPasses': request.form['keyPasses'],
        'passesCompletos': request.form['passesCompletos'],
        'passesProgressivos': request.form['passesProgressivos'],
        'penaltisMarcadosJogador': request.form['penaltisMarcadosJogador'],
        'penaltisTentadosJogador': request.form['penaltisTentadosJogador'],
        'percentagemPasses': request.form['percentagemPasses'],
        'rematesBalizaJogador': request.form['rematesBalizaJogador'],
        'rematesJogador': request.form['rematesJogador'],
        'toques': request.form['toques'],
        'xaJogador': request.form['xaJogador'],
        'xgJogador': request.form['xgJogador'],
        'aereosGanhos': request.form['aereosGanhos'],
        'autoGolos': request.form['autoGolos'],
        'bolasRecuperadas': request.form['bolasRecuperadas'],
        'caJogador': request.form['caJogador'],
        'cortes': request.form['cortes'],
        'cortesGanhos': request.form['cortesGanhos'],
        'cvJogador': request.form['cvJogador'],
        'duelos': request.form['duelos'],
        'duelosGanhos': request.form['duelosGanhos'],
        'faltasCometidas': request.form['faltasCometidas'],
        'intercecoes': request.form['intercecoes']
    }

    if request.form['posicaoJogador'] == 'Guarda-redes':
        for key, _, _ in player_gr_properties:
            jogador[key] = request.form[key]
    
    response = requests.put(f'{API_URL}/editar_jogador/{idJogador}', json=jogador)
    if response.status_code == 200:
        return redirect(url_for('clube', id=request.form['clube']))
    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=23242, debug=True)