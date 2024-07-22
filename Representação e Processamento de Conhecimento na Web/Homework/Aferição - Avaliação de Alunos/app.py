from flask import Flask, render_template, url_for, request
from datetime import datetime
import requests

app = Flask(__name__)


graphdb_endpoint = "http://localhost:7200/repositories/Alunos"


@app.route('/api/alunos')
def alunos_curso():
    curso = request.args.get('curso')
    group_by = request.args.get('groupBy')

    if curso:
        sparql_query = f'''
    PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    select ?nome where {{
        ?aluno rdf:type :Aluno ;
               :nome ?nome ;
               :curso ?curso .
        filter (?curso = "{curso}")
    }}
    '''
        
    elif group_by:
        if group_by == 'curso':
            sparql_query = '''
        PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        select ?curso (count(?aluno) as ?naluno) where {
            ?aluno rdf:type :Aluno ;
                   :curso ?curso ;
        } group by ?curso order by ?curso
        '''
            
        elif group_by == 'projeto':
            sparql_query = '''
        PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        select ?projeto (count(?aluno) as ?naluno) where {
            ?aluno rdf:type :Aluno ;
        		   :projeto ?projeto .
        } group by ?projeto
        '''
            
        elif group_by == 'recurso':
            sparql_query = '''
        PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        select ?idAluno ?nome ?curso ?recurso where {
            ?aluno rdf:type :Aluno ;
                   :id ?idAluno ;
                   :nome ?nome ;
                   :curso ?curso ;
        		   :temExame ?recurso .
            ?recurso :epoca "recurso" .
        } order by ?nome
        '''
        
    else:
        sparql_query = '''
    PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    select ?idAluno ?nome ?curso where {
        ?aluno rdf:type :Aluno ;
               :id ?idAluno ;
               :nome ?nome ;
               :curso ?curso .
    } order by ?nome
    '''
        
    resposta = requests.get(graphdb_endpoint, params={ 'query': sparql_query }, headers={ 'Accept': 'application/sparql-results+json' })
    if resposta.status_code == 200:
        dados = resposta.json()['results']['bindings']
        return dados
    else:
        return ""


@app.route('/api/alunos/<id>')
def aluno(id):
    sparql_query = f'''
PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
select ?nome ?curso ?projeto ?epoca ?notaexame ?tp ?notatpc where {{
    ?aluno rdf:type :Aluno ;
           :id ?idAluno ;
           :nome ?nome ;
           :curso ?curso ;
           :projeto ?projeto ;
           :temTPC ?tpc ;
           :temExame ?exame .
    ?exame :epoca ?epoca ;
           :notaexame ?notaexame .
    ?tpc :tp ?tp ;
         :notatpc ?notatpc .
    filter (?idAluno = "{id}")
}}
'''
    
    resposta = requests.get(graphdb_endpoint, params={ 'query': sparql_query }, headers={ 'Accept': 'application/sparql-results+json' })
    if resposta.status_code == 200:
        dados = resposta.json()['results']['bindings']
        return dados
    else:
        return ""


@app.route('/api/alunos/tpc')
def tpc():
    sparql_query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
select ?idAluno ?nome ?curso (count(?tpc) as ?ntpc) where {
    ?aluno rdf:type :Aluno ;
           :id ?idAluno ;
           :nome ?nome ;
           :curso ?curso ;
           :temTPC ?tpc .
} group by ?idAluno ?nome ?curso order by (?nome)
'''

    resposta = requests.get(graphdb_endpoint, params={ 'query': sparql_query }, headers={ 'Accept': 'application/sparql-results+json' })
    if resposta.status_code == 200:
        dados = resposta.json()['results']['bindings']
        return dados
    else:
        return ""


@app.route('/api/alunos/avaliados')
def avaliados():
    sparql_query = '''
PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?idAluno ?nome ?curso ?notaFinal WHERE {
    ?aluno rdf:type :Aluno ;
           :id ?idAluno ;
           :nome ?nome ;
           :curso ?curso ;
           :projeto ?notaProjeto ;
           :temTPC ?tpc .
    ?tpc :notatpc ?notatpc .
    
    {
        select ?aluno (max(?notaexame) as ?maxNotaExame) (sum(?notatpc) as ?sumNotaTpc) where {
            ?aluno :temExame ?exame .
            ?exame :notaexame ?notaexame .
        } group by ?aluno
    }
    
    bind(if(?notaProjeto < 10 || ?maxNotaExame < 10, "R",
             if((?sumNotaTpc + (?notaProjeto * 0.4) + (?maxNotaExame * 0.4)) < 10, "R",
                ?sumNotaTpc + (?notaProjeto * 0.4) + (?maxNotaExame * 0.4))) as ?notaFinal)
} group by ?idAluno ?nome ?curso ?notaFinal order by ?nome
'''

    resposta = requests.get(graphdb_endpoint, params={ 'query': sparql_query }, headers={ 'Accept': 'application/sparql-results+json' })
    if resposta.status_code == 200:
        dados = resposta.json()['results']['bindings']
        return dados
    else:
        return ""


if __name__ == '__main__':
    app.run(debug=True)