from flask import Flask, render_template, url_for
from datetime import datetime
import requests

app = Flask(__name__)

# data do sistema no formato ISO
data_hora_atual = datetime.now()
data_iso_formatada = data_hora_atual.strftime('%Y-%m-%dT%H:%M:%S')

# GraphDB endpoint
graphdb_endpoint = "http://localhost:7200/repositories/tabelaPeriodica"

@app.route('/')
def index():
    return render_template('index.html', data = { 'data': data_iso_formatada })


@app.route('/elementos')
def elementos():
    sparql_query = '''
prefix tp: <http://www.daml.org/2003/01/periodictable/PeriodicTable#>
select ?nome ?simb ?na ?group where {
    ?s a tp:Element ;
       tp:name ?nome ;
       tp:symbol ?simb ;
       tp:atomicNumber ?na ;
       tp:group ?group .
}
order by (?nome)
'''
    resposta = requests.get(graphdb_endpoint, params={ 'query': sparql_query }, headers={ 'Accept': 'application/sparql-results+json' })
    if resposta.status_code == 200:
        dados = resposta.json()['results']['bindings']
        return render_template('elementos.html', data = dados)
    else:
        return render_template('empty.html', data = { 'data': data_iso_formatada })


@app.route('/elementos/<elemento>')
def elemento(elemento):
    sparql_query = f'''
PREFIX tp: <http://www.daml.org/2003/01/periodictable/PeriodicTable#>
select ?an ?aw ?b ?cr ?c ?col ?g ?p ?ss ?symb where {{
    ?s a tp:Element ;
       tp:name "{elemento}" ;
       tp:group ?g ;
       tp:symbol ?symb ;
       tp:atomicNumber ?an .
    optional {{
        ?s tp:atomicWeight ?aw .
    }}
    optional {{
        ?s tp:block ?b .
    }}
    optional {{
        ?s tp:casRegistryID ?cr .
    }}
    optional {{
        ?s tp:classification ?c .
    }}
    optional {{
        ?s tp:color ?col .
    }}
    optional {{
    	?s tp:period ?p .   
    }}
    optional {{
        ?s tp:standardState ?ss .
    }}
}}
'''
    resposta = requests.get(graphdb_endpoint, params={ 'query': sparql_query }, headers={ 'Accept': 'application/sparql-results+json' })
    if resposta.status_code == 200:
        dados = resposta.json()['results']['bindings']
        return render_template('elemento.html', data = { 'name': elemento, 'data': dados })
    else:
        return render_template('empty.html', data = { 'data': data_iso_formatada })


@app.route('/grupos')
def grupos():
    sparql_query = '''
PREFIX tp: <http://www.daml.org/2003/01/periodictable/PeriodicTable#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
select ?group (count (?elem) as ?nelem) where {
    ?group a tp:Group ;
           tp:element ?elem .
} group by ?group
order by (xsd:integer(strafter(str(?group), '_')))
'''
    resposta = requests.get(graphdb_endpoint, params={ 'query': sparql_query }, headers={ 'Accept': 'application/sparql-results+json' })
    if resposta.status_code == 200:
        dados = resposta.json()['results']['bindings']
        return render_template('grupos.html', data = dados)
    else:
        return render_template('empty.html', data = { 'data': data_iso_formatada })


@app.route('/grupos/<grupo>')
def grupo(grupo):
    sparql_query = f'''
prefix tp: <http://www.daml.org/2003/01/periodictable/PeriodicTable#>
select ?group ?nome ?num ?elnome where {{
    ?group a tp:Group .
    optional {{
        ?group tp:name ?nome .
    }}
    optional {{
        ?group tp:number ?num .
    }}
    ?group tp:element ?elem .
    ?elem tp:name ?elnome .
    filter(str(?group) = "http://www.daml.org/2003/01/periodictable/PeriodicTable#{grupo}")
}}
'''
    resposta = requests.get(graphdb_endpoint, params={ 'query': sparql_query }, headers={ 'Accept': 'application/sparql-results+json' })
    if resposta.status_code == 200:
        dados = resposta.json()['results']['bindings']
        return render_template('grupo.html', data = dados)
    else:
        return render_template('empty.html', data = { 'data': data_iso_formatada })


if __name__ == '__main__':
    app.run(debug=True)