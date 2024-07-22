import json

file = open("aval-alunos.json")
bd = json.load(file)
file.close()

ttl = """@prefix : <http://rpcw.di.uminho.pt/2024/alunos/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <http://rpcw.di.uminho.pt/2024/alunos/> .

<http://rpcw.di.uminho.pt/2024/alunos> rdf:type owl:Ontology .

#################################################################
#    Object Properties
#################################################################

###  http://rpcw.di.uminho.pt/2024/alunos#temExame
:temExame rdf:type owl:ObjectProperty ;
          rdfs:domain :Aluno ;
          rdfs:range :Exame .


###  http://rpcw.di.uminho.pt/2024/alunos#temTPC
:temTPC rdf:type owl:ObjectProperty ;
        rdfs:domain :Aluno ;
        rdfs:range :TPC .


#################################################################
#    Data properties
#################################################################

###  http://rpcw.di.uminho.pt/2024/alunos#curso
:curso rdf:type owl:DatatypeProperty ;
       rdfs:domain :Aluno ;
       rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2024/alunos#epoca
:epoca rdf:type owl:DatatypeProperty ;
       rdfs:domain :Exame ;
       rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2024/alunos#id
:id rdf:type owl:DatatypeProperty ;
    rdfs:domain :Aluno ;
    rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2024/alunos#nome
:nome rdf:type owl:DatatypeProperty ;
      rdfs:domain :Aluno ;
      rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2024/alunos#notaexame
:notaexame rdf:type owl:DatatypeProperty ;
           rdfs:domain :Exame ;
           rdfs:range xsd:int .


###  http://rpcw.di.uminho.pt/2024/alunos#notatpc
:notatpc rdf:type owl:DatatypeProperty ;
         rdfs:domain :TPC ;
         rdfs:range xsd:float .


###  http://rpcw.di.uminho.pt/2024/alunos#projeto
:projeto rdf:type owl:DatatypeProperty ;
         rdfs:domain :Aluno ;
         rdfs:range xsd:int .


###  http://rpcw.di.uminho.pt/2024/alunos#tp
:tp rdf:type owl:DatatypeProperty ;
    rdfs:domain :TPC ;
    rdfs:range xsd:string .


#################################################################
#    Classes
#################################################################

###  http://rpcw.di.uminho.pt/2024/alunos#Aluno
:Aluno rdf:type owl:Class .


###  http://rpcw.di.uminho.pt/2024/alunos#Exame
:Exame rdf:type owl:Class .


###  http://rpcw.di.uminho.pt/2024/alunos#TPC
:TPC rdf:type owl:Class .


#################################################################
#    Individuals
#################################################################

"""

for aluno in bd['alunos']:
    ttl += f"""###  http://rpcw.di.uminho.pt/2024/alunos#{aluno['idAluno']}
:{aluno['idAluno']} rdf:type owl:NamedIndividual ,
                             :Aluno ;
          :curso "{aluno['curso']}" ;
          :id "{aluno['idAluno']}" ;
          :nome "{aluno['nome']}" ;
          :projeto "{aluno['projeto']}"^^xsd:int ;
          :temExame """
    
    for ekey in aluno['exames'].keys():
        aekey = aluno['idAluno'] + '_' + ekey
        ttl += f""":{aekey} ,
                    """
    ttl = ttl[:-22] + """;
          :temTPC """

    for tpc in aluno['tpc']:
        atkey = aluno['idAluno'] + '_' + tpc['tp']
        ttl += f""":{atkey} ,
                  """
        
    ttl = ttl[:-20] + """.
    

"""

    for ekey in aluno['exames'].keys():
        aekey = aluno['idAluno'] + '_' + ekey
        ttl += f"""###  http://rpcw.di.uminho.pt/2024/alunos#{aekey}
:{aekey} rdf:type owl:NamedIndividual ,
                  :Exame ;
        :epoca "{ekey}" ;
        :notaexame "{aluno['exames'][ekey]}"^^xsd:int .
        
        
"""


    for tpc in aluno['tpc']:
        atkey = aluno['idAluno'] + '_' + tpc['tp']
        ttl += f"""###  http://rpcw.di.uminho.pt/2024/alunos#{atkey}
:{atkey} rdf:type owl:NamedIndividual ,
                  :TPC ;
      :notatpc "{tpc['nota']}"^^xsd:float ;
      :tp "{tpc['tp']}" .
      
      
"""
        
print(ttl)