from flask import Flask, render_template, url_for
from datetime import datetime
import requests

app = Flask(__name__)

# data do sistema no formato ISO
data_hora_atual = datetime.now()
data_iso_formatada = data_hora_atual.strftime('%Y-%m-%dT%H:%M:%S')

# GraphDB endpoint
graphdb_endpoint = "http://epl.di.uminho.pt:7200/repositories/cinema2024"

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/filmes')
def films():
    sparql_query = '''
prefix : <http://rpcw.di.uminho.pt/2024/cinema/>

select ?film ?title where {
    ?film a :Film ;
          :title ?title .
} order by ?title
'''
    resposta = requests.get(graphdb_endpoint, params={ 'query': sparql_query }, headers={ 'Accept': 'application/sparql-results+json' })
    if resposta.status_code == 200:
        dados = resposta.json()['results']['bindings']
        return render_template('filmes.html', data = dados)
    else:
        return render_template('empty.html')


@app.route('/filmes/<filme>')
def elemento(filme):
    sparql_query = f'''
prefix : <http://rpcw.di.uminho.pt/2024/cinema/>

select ?film ?title ?description ?duration ?country ?actor ?composer ?director ?genre ?producer ?writer ?date where {{
    ?film a :Film ;
          :title ?title .
    optional {{ ?film :description ?description . }}
    optional {{ ?film :duration ?duration . }}
    optional {{ ?film :hasCountry ?country . }}
    optional {{ ?film :hasActor ?actor . }}
    optional {{ ?film :hasComposer ?composer . }}
    optional {{ ?film :hasDirector ?director . }}
    optional {{ ?film :hasGenre ?genre . }}
    optional {{ ?film :hasProducer ?producer . }}
    optional {{ ?film :hasWriter ?writer . }}
    optional {{ ?film :releaseDate ?date . }}
    filter(str(?film) = "http://rpcw.di.uminho.pt/2024/cinema/{filme}")
}}
'''
    resposta = requests.get(graphdb_endpoint, params={ 'query': sparql_query }, headers={ 'Accept': 'application/sparql-results+json' })
    if resposta.status_code == 200:
        dados = resposta.json()['results']['bindings']

        descriptions_norep = []
        durations_norep = []
        countries_norep = []
        actors_norep = []
        composers_norep = []
        directors_norep = []
        genres_norep = []
        producers_norep = []
        writers_norep = []
        dates_norep = []

        for entry in dados:
            if 'description' in entry.keys():
                if entry['description']['value'] not in descriptions_norep:
                    descriptions_norep.append(entry['description']['value'])
            if 'duration' in entry.keys():
                if entry['duration']['value'] not in durations_norep:
                    durations_norep.append(entry['duration']['value'])
            if 'country' in entry.keys():
                if entry['country']['value'].split('/')[-1] not in countries_norep:
                    countries_norep.append(entry['country']['value'].split('/')[-1])
            if 'actor' in entry.keys():
                if entry['actor']['value'] not in actors_norep:
                    actors_norep.append(entry['actor']['value'])
            if 'composer' in entry.keys():
                if entry['composer']['value'] not in composers_norep:
                    composers_norep.append(entry['composer']['value'])
            if 'director' in entry.keys():
                if entry['director']['value'] not in directors_norep:
                    directors_norep.append(entry['director']['value'])
            if 'genre' in entry.keys():
                if entry['genre']['value'].split('/')[-1] not in genres_norep:
                    genres_norep.append(entry['genre']['value'].split('/')[-1])
            if 'producer' in entry.keys():
                if entry['producer']['value'] not in producers_norep:
                    producers_norep.append(entry['producer']['value'])
            if 'writer' in entry.keys():
                if entry['writer']['value'] not in writers_norep:
                    writers_norep.append(entry['writer']['value'])
            if 'date' in entry.keys():
                if entry['date']['value'] not in dates_norep:
                    dates_norep.append(entry['date']['value'])

        final_data = {
            'film': filme,
            'title': dados[0]['title']['value'],
            'descriptions': descriptions_norep,
            'durations': durations_norep,
            'countries': countries_norep,
            'actors': actors_norep,
            'composers': composers_norep,
            'directors': directors_norep,
            'genres': genres_norep,
            'producers': producers_norep,
            'writers': writers_norep,
            'dates': dates_norep
        }

        return render_template('filme.html', data = final_data)
    else:
        return render_template('empty.html', data = { 'data': data_iso_formatada })


@app.route('/pessoas')
def grupos():
    sparql_query = '''
prefix : <http://rpcw.di.uminho.pt/2024/cinema/>

select ?person ?name where {
    ?person a :Person ;
            :name ?name .
} order by ?person
'''
    resposta = requests.get(graphdb_endpoint, params={ 'query': sparql_query }, headers={ 'Accept': 'application/sparql-results+json' })
    if resposta.status_code == 200:
        dados = resposta.json()['results']['bindings']
        return render_template('pessoas.html', data = dados)
    else:
        return render_template('empty.html', data = { 'data': data_iso_formatada })


@app.route('/pessoas/<pessoa>')
def grupo(pessoa):
    sparql_query = f'''
prefix : <http://rpcw.di.uminho.pt/2024/cinema/>
select ?person ?name ?bdate ?film ?title where {{
    ?person a :Person ; 
            :name ?name ;
            :birthDate ?bdate .
    optional {{ ?film :hasActor ?person ; 
                      :title ?title .
             }}
    optional {{ ?film :hasComposer ?person ; 
                      :title ?title .
             }}
    optional {{ ?film :hasDirector ?person ; 
                      :title ?title .
             }}
    optional {{ ?film :hasProducer ?person ; 
                      :title ?title .
             }}
    optional {{ ?film :hasWriter ?person ; 
                      :title ?title .
             }}
    filter(str(?person) = "http://rpcw.di.uminho.pt/2024/cinema/{pessoa}")
}} order by ?film
'''
    resposta = requests.get(graphdb_endpoint, params={ 'query': sparql_query }, headers={ 'Accept': 'application/sparql-results+json' })
    if resposta.status_code == 200:
        dados = resposta.json()['results']['bindings']
        return render_template('pessoa.html', data = dados)
    else:
        return render_template('empty.html', data = { 'data': data_iso_formatada })


if __name__ == '__main__':
    app.run(debug=True)