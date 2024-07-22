import requests
import json

sparql_endpoint = "http://dbpedia.org/sparql"
cinema_json = []

for counter in range(18):
    offset = counter * 10000

    sparql_query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>

    select distinct ?film where {{
    ?film rdf:type <http://dbpedia.org/ontology/Film> .
    }} limit 10000 offset {offset}
    """

    headers = {
        "Accept": "application/sparql-results+json"
    }

    params = {
        "query": sparql_query,
        "format": "json"
    }

    response = requests.get(sparql_endpoint, params=params, headers=headers)

    if response.status_code == 200:
        results = response.json()
        for result in results["results"]["bindings"]:
            uri = result["film"]["value"]
            cinema_json.append({
                'uri': uri
            })

    else:
        print("error:", response.status_code)

with open('dbpedia_cinema.json', 'w') as cinema_json_file:
    json.dump(cinema_json, cinema_json_file, indent=4)


for filme in cinema_json:

    sparql_query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>

    select distinct ?film_name ?film_actor ?film_director ?film_writer ?film_composer ?film_time where {{
    ?film rdf:type <http://dbpedia.org/ontology/Film> .
    optional {{ ?film rdfs:label ?film_name . }}
    optional {{ ?film dbo:starring ?film_actor . }}
    optional {{ ?film dbo:director ?film_director .}}
    optional {{ ?film dbo:writer ?film_writer .}}
    optional {{ ?film dbo:musicComposer ?film_composer .}}
    optional {{ ?film dbo:runtime ?film_time . }}

    filter(str(?film)="{filme["uri"]}")
    filter(lang(?film_name)='en')
    }} 
    """

    headers = {
        "Accept": "application/sparql-results+json"
    }

    params = {
        "query": sparql_query,
        "format": "json"
    }

    response = requests.get(sparql_endpoint, params=params, headers=headers)

    if response.status_code == 200:
        atores = []
        realizadores = []
        escritores = []
        musicos = []

        results = response.json()
        for result in results["results"]["bindings"]:
            if 'film_name' in result.keys():
                filme['name'] = result['film_name']['value']
            if 'film_actor' in result.keys():
                if result['film_actor']['value'] not in atores:
                    atores.append(result['film_actor']['value'])
            if 'film_director' in result.keys():
                if result['film_director']['value'] not in realizadores:
                    realizadores.append(result['film_director']['value'])
            if 'film_writer' in result.keys():
                if result['film_writer']['value'] not in escritores:
                    escritores.append(result['film_writer']['value'])
            if 'film_composer' in result.keys():
                if result['film_composer']['value'] not in musicos:
                    musicos.append(result['film_composer']['value'])
            if 'film_time' in result.keys():
                filme['time'] = float(result['film_time']['value'])

        if len(atores) > 0:
            filme['actors'] = atores
        if len(realizadores) > 0:
            filme['directors'] = realizadores
        if len(escritores) > 0:
            filme['writers'] = escritores
        if len(musicos) > 0:
            filme['composers'] = musicos

    else:
        print("error:", response.status_code)

with open('dbpedia_cinema_final.json', 'w') as cinema_final_json_file:
    json.dump(cinema_json, cinema_final_json_file, indent=4)