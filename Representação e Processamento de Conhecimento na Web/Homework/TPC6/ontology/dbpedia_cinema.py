import requests
import json

sparql_endpoint = "http://dbpedia.org/sparql"

cinema_json = {
    'films': dict(),
    'people': dict()
}

sparql_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbo: <http://dbpedia.org/ontology/>

select distinct ?film ?title ?description ?actor ?actor_name ?actor_bdate ?composer ?composer_name ?composer_bdate ?country ?director ?director_name ?director_bdate ?genre ?producer ?producer_name ?producer_bdate ?writer ?writer_name ?writer_bdate ?release ?duration where {
     ?film rdf:type <http://dbpedia.org/ontology/Film> ;
               rdfs:label ?title .
     optional {?film dbo:abstract ?description . }
     optional { ?film dbo:starring ?actor .
          optional { ?actor foaf:name ?actor_name . }
          optional { ?actor dbo:birthDate ?actor_bdate . }
     }
     optional { ?film dbo:musicComposer ?composer . 
          optional { ?composer foaf:name ?composer_name . }
          optional { ?composer dbo:birthDate ?composer_bdate . }
     }
     optional { ?film dbo:country ?country . }
     optional { ?film dbo:director ?director . 
          optional { ?director foaf:name ?director_name . }
          optional { ?director dbo:birthDate ?director_bdate . }
     }
     optional { ?film dbo:genre ?genre . }
     optional { ?film dbo:producer ?producer . 
          optional { ?producer foaf:name ?producer_name . }
          optional { ?producer dbo:birthDate ?producer_bdate . }     
}
     optional { ?film dbo:writer ?writer . 
          optional { ?writer foaf:name ?writer_name . }
          optional { ?writer dbo:birthDate ?writer_bdate . }     
}
     optional { ?film dbo:releaseDate ?release . }
     optional { ?film dbo:runtime ?duration . }
     filter(lang(?title)='en') .
     filter(lang(?description)='en') .
}
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
        if uri not in cinema_json['films']:
            cinema_json['films'][uri] = {
                'title': result['title']['value'],
                'description': set(),
                'actors': set(),
                'composers': set(),
                'countries': set(),
                'directors': set(),
                'genres': set(),
                'producers': set(),
                'writers': set(),
                'release_dates': set(),
                'durations': set()
            }
        if 'description' in result.keys():
            cinema_json['films'][uri]['description'].add(result['description']['value'])
        if 'actor' in result.keys():
            actor_uri = result['actor']['value']
            cinema_json['films'][uri]['actors'].add(actor_uri)
            if actor_uri not in cinema_json['people']:
                cinema_json['people'][actor_uri] = {
                    'name': "",
                    'bdate': "",
                }
            if 'actor_name' in result.keys():
                cinema_json['people'][actor_uri]['name'] = result['actor_name']['value']
            if 'actor_bdate' in result.keys():
                cinema_json['people'][actor_uri]['bdate'] = result['actor_bdate']['value']
        if 'composer' in result.keys():
            composer_uri = result['composer']['value']
            cinema_json['films'][uri]['composers'].add(composer_uri)
            if composer_uri not in cinema_json['people']:
                cinema_json['people'][composer_uri] = {
                    'name': "",
                    'bdate': ""
                }
            if 'composer_name' in result.keys():
                cinema_json['people'][composer_uri]['name'] = result['composer_name']['value']
            if 'composer_bdate' in result.keys():
                cinema_json['people'][composer_uri]['bdate'] = result['composer_bdate']['value']
        if 'country' in result.keys():
            cinema_json['films'][uri]['countries'].add(result['country']['value'])
        if 'director' in result.keys():
            director_uri = result['director']['value']
            cinema_json['films'][uri]['directors'].add(director_uri)
            if director_uri not in cinema_json['people']:
                cinema_json['people'][director_uri] = {
                    'name': "",
                    'bdate': ""
                }
            if 'director_name' in result.keys():
                cinema_json['people'][director_uri]['name'] = result['director_name']['value']
            if 'director_bdate' in result.keys():
                cinema_json['people'][director_uri]['bdate'] = result['director_bdate']['value']
        if 'genre' in result.keys():
            cinema_json['films'][uri]['genres'].add(result['genre']['value'])
        if 'producer' in result.keys():
            producer_uri = result['producer']['value']
            cinema_json['films'][uri]['producers'].add(producer_uri)
            if producer_uri not in cinema_json['people']:
                cinema_json['people'][producer_uri] = {
                    'name': "",
                    'bdate': ""
                }
            if 'producer_name' in result.keys():
                cinema_json['people'][producer_uri]['name'] = result['producer_name']['value']
            if 'producer_bdate' in result.keys():
                cinema_json['people'][producer_uri]['bdate'] = result['producer_bdate']['value']
        if 'writer' in result.keys():
            writer_uri = result['writer']['value']
            cinema_json['films'][uri]['writers'].add(writer_uri)
            if writer_uri not in cinema_json['people']:
                cinema_json['people'][writer_uri] = {
                    'name': "",
                    'bdate': ""
                }
            if 'producer_name' in result.keys():
                cinema_json['people'][writer_uri]['name'] = result['producer_name']['value']
            if 'producer_bdate' in result.keys():
                cinema_json['people'][writer_uri]['bdate'] = result['producer_bdate']['value']
        if 'release' in result.keys():
            cinema_json['films'][uri]['release_dates'].add(result['release']['value'])
        if 'duration' in result.keys():
            cinema_json['films'][uri]['durations'].add(result['duration']['value'])

else:
    print("error:", response.status_code)


ttl = '''@prefix : <http://rpcw.di.uminho.pt/2024/cinema/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <http://rpcw.di.uminho.pt/2024/cinema/> .

<http://rpcw.di.uminho.pt/2024/cinema> rdf:type owl:Ontology .

#################################################################
#    Object Properties
#################################################################

###  http://rpcw.di.uminho.pt/2024/cinema#hasCountry
:hasCountry rdf:type owl:ObjectProperty ;
            rdfs:domain :Film ;
            rdfs:range :Country .


###  http://rpcw.di.uminho.pt/2024/cinema/acted
:acted rdf:type owl:ObjectProperty ;
       owl:inverseOf :hasActor ;
       rdfs:domain :Person ;
       rdfs:range :Film .


###  http://rpcw.di.uminho.pt/2024/cinema/composed
:composed rdf:type owl:ObjectProperty ;
          owl:inverseOf :hasComposer ;
          rdfs:domain :Person .


###  http://rpcw.di.uminho.pt/2024/cinema/directed
:directed rdf:type owl:ObjectProperty ;
          owl:inverseOf :hasDirector ;
          rdfs:domain :Person ;
          rdfs:range :Film .


###  http://rpcw.di.uminho.pt/2024/cinema/hasActor
:hasActor rdf:type owl:ObjectProperty ;
          rdfs:domain :Film ;
          rdfs:range :Person .


###  http://rpcw.di.uminho.pt/2024/cinema/hasComposer
:hasComposer rdf:type owl:ObjectProperty ;
             rdfs:domain :Film ;
             rdfs:range :Composer ,
                        :Person .


###  http://rpcw.di.uminho.pt/2024/cinema/hasCountry
:hasCountry rdf:type owl:ObjectProperty ;
            rdfs:domain :Film .


###  http://rpcw.di.uminho.pt/2024/cinema/hasDirector
:hasDirector rdf:type owl:ObjectProperty ;
             rdfs:domain :Film ;
             rdfs:range :Person .


###  http://rpcw.di.uminho.pt/2024/cinema/hasGenre
:hasGenre rdf:type owl:ObjectProperty ;
          rdfs:domain :Film ;
          rdfs:range :Genre .


###  http://rpcw.di.uminho.pt/2024/cinema/hasProducer
:hasProducer rdf:type owl:ObjectProperty ;
             owl:inverseOf :produced ;
             rdfs:domain :Film ;
             rdfs:range :Person .


###  http://rpcw.di.uminho.pt/2024/cinema/hasWriter
:hasWriter rdf:type owl:ObjectProperty ;
           owl:inverseOf :wrote ;
           rdfs:domain :Film ;
           rdfs:range :Writer ,
                      :Person .


###  http://rpcw.di.uminho.pt/2024/cinema/produced
:produced rdf:type owl:ObjectProperty ;
          rdfs:domain :Person .


###  http://rpcw.di.uminho.pt/2024/cinema/wrote
:wrote rdf:type owl:ObjectProperty ;
       rdfs:domain :Writer ,
                   :Person .


#################################################################
#    Data properties
#################################################################

###  http://rpcw.di.uminho.pt/2024/cinema#releaseDate
:releaseDate rdf:type owl:DatatypeProperty ;
             rdfs:domain :Film ;
             rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2024/cinema/birthDate
:birthDate rdf:type owl:DatatypeProperty ;
           rdfs:domain :Person ;
           rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2024/cinema/description
:description rdf:type owl:DatatypeProperty ;
             rdfs:domain :Film ;
             rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2024/cinema/duration
:duration rdf:type owl:DatatypeProperty ;
          rdfs:domain :Film ;
          rdfs:range xsd:double .


###  http://rpcw.di.uminho.pt/2024/cinema/name
:name rdf:type owl:DatatypeProperty ;
      rdfs:domain :Person ;
      rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2024/cinema/title
:title rdf:type owl:DatatypeProperty ;
       rdfs:domain :Film ;
       rdfs:range xsd:string .


#################################################################
#    Classes
#################################################################

###  http://rpcw.di.uminho.pt/2024/cinema#Composer
:Composer rdf:type owl:Class ;
          owl:equivalentClass [ owl:intersectionOf ( :Person
                                                     [ rdf:type owl:Restriction ;
                                                       owl:onProperty :composed ;
                                                       owl:someValuesFrom :Film
                                                     ]
                                                   ) ;
                                rdf:type owl:Class
                              ] ;
          rdfs:subClassOf :Person .


###  http://rpcw.di.uminho.pt/2024/cinema#Country
:Country rdf:type owl:Class .


###  http://rpcw.di.uminho.pt/2024/cinema#Writer
:Writer rdf:type owl:Class ;
        owl:equivalentClass [ owl:intersectionOf ( :Person
                                                   [ rdf:type owl:Restriction ;
                                                     owl:onProperty :wrote ;
                                                     owl:someValuesFrom :Film
                                                   ]
                                                 ) ;
                              rdf:type owl:Class
                            ] ;
        rdfs:subClassOf :Person .


###  http://rpcw.di.uminho.pt/2024/cinema/Actor
:Actor rdf:type owl:Class ;
       owl:equivalentClass [ owl:intersectionOf ( :Person
                                                  [ rdf:type owl:Restriction ;
                                                    owl:onProperty :acted ;
                                                    owl:someValuesFrom :Film
                                                  ]
                                                ) ;
                             rdf:type owl:Class
                           ] .


###  http://rpcw.di.uminho.pt/2024/cinema/Director
:Director rdf:type owl:Class ;
          owl:equivalentClass [ owl:intersectionOf ( :Person
                                                     [ rdf:type owl:Restriction ;
                                                       owl:onProperty :directed ;
                                                       owl:someValuesFrom :Film
                                                     ]
                                                   ) ;
                                rdf:type owl:Class
                              ] .


###  http://rpcw.di.uminho.pt/2024/cinema/Film
:Film rdf:type owl:Class .


###  http://rpcw.di.uminho.pt/2024/cinema/Genre
:Genre rdf:type owl:Class .


###  http://rpcw.di.uminho.pt/2024/cinema/Person
:Person rdf:type owl:Class .


###  http://rpcw.di.uminho.pt/2024/cinema/Producer
:Producer rdf:type owl:Class ;
          owl:equivalentClass [ owl:intersectionOf ( :Person
                                                     [ rdf:type owl:Restriction ;
                                                       owl:onProperty :produced ;
                                                       owl:someValuesFrom :Film
                                                     ]
                                                   ) ;
                                rdf:type owl:Class
                              ] .


#################################################################
#    Individuals
#################################################################

'''

for person in cinema_json['people']:
    id = person.split('/')[-1].replace('(', '_').replace(')','_').replace("'", '_').replace(',', '_').replace('.', '')

    ttl += f'''###  http://rpcw.di.uminho.pt/2024/cinema#{id}
:{id} rdf:type owl:NamedIndividual ;
                :birthDate "{cinema_json['people'][person]['bdate']}" ;
                :name "{cinema_json['people'][person]['name'].replace('"', "'")}" .

                
'''
    

for film in cinema_json['films']:
    id = list(cinema_json['films'][film]['title'])[0].replace(' ', '_').replace('(','_').replace(')', '_').replace(',','_').replace("'","_").replace('-','_')
    id = id.replace('&', '_').replace('.','_').replace('/', '_')

    ttl += f'''###  http://rpcw.di.uminho.pt/2024/cinema#{id}
:{id} rdf:type owl:NamedIndividual ;
      :title "{cinema_json['films'][film]['title']}" ;'''

    if len(cinema_json['films'][film]['description']) > 0:
        ttl += '''      
      :description '''
        for description in cinema_json['films'][film]['description']:
            ttl += f'''"{description.replace('"', "'")}" ,
                   '''
        ttl = ttl[:-21] + ';'

    if len(cinema_json['films'][film]['countries']) > 0:
        ttl += '''      
      :hasCountry '''
        for country in cinema_json['films'][film]['countries']:
            id = country.split('/')[-1]
            ttl += f''':{id} ,
                  '''
        ttl = ttl[:-20] + ';'

    if len(cinema_json['films'][film]['actors']) > 0:
        ttl += '''      
      :hasActor '''
        for actor in cinema_json['films'][film]['actors']:
            actor_id = actor.split('/')[-1].replace('(', '_').replace(')','_').replace("'", '_').replace(',', '_').replace('.', '')
            ttl += f''':{actor_id} ,
                '''
        ttl = ttl[:-18] + ';'

    if len(cinema_json['films'][film]['composers']) > 0:
        ttl += '''      
      :hasComposer '''
        for composer in cinema_json['films'][film]['composers']:
            composer_id = composer.split('/')[-1].replace('(', '_').replace(')','_').replace("'", '_').replace(',', '_').replace('.', '')
            ttl += f''':{composer_id} ,
                   '''
        ttl = ttl[:-21] + ';'

    if len(cinema_json['films'][film]['directors']) > 0:
        ttl += '''      
      :hasDirector '''
        for director in cinema_json['films'][film]['directors']:
            director_id = director.split('/')[-1].replace('(', '_').replace(')','_').replace("'", '_').replace(',', '_').replace('.', '')
            ttl += f''':{director_id} ,
                   '''
        ttl = ttl[:-21] + ';'

    if len(cinema_json['films'][film]['genres']) > 0:
        ttl += '''      
      :hasGenre '''
        for genre in cinema_json['films'][film]['genres']:
            id = genre.split('/')[-1]
            ttl += f''':{id} ,
                '''
        ttl = ttl[:-18] + ';'

    if len(cinema_json['films'][film]['producers']) > 0:
        ttl += '''      
      :hasProducer '''
        for producer in cinema_json['films'][film]['producers']:
            producer_id = producer.split('/')[-1].replace('(', '_').replace(')','_').replace("'", '_').replace(',', '_').replace('.', '')
            ttl += f''':{producer_id} ,
                   '''
        ttl = ttl[:-21] + ';'

    if len(cinema_json['films'][film]['writers']) > 0:
        ttl += '''      
      :hasWriter '''
        for writer in cinema_json['films'][film]['writers']:
            writer_id = writer.split('/')[-1].replace('(', '_').replace(')','_').replace("'", '_').replace(',', '_').replace('.', '')
            ttl += f''':{writer_id} ,
                 '''
        ttl = ttl[:-19] + ';'

    if len(cinema_json['films'][film]['release_dates']) > 0:
        ttl += '''      
      :releaseDate '''
        for date in cinema_json['films'][film]['release_dates']:
            ttl += f'''"{date}" ,
                   '''
        ttl = ttl[:-21] + ';'

    if len(cinema_json['films'][film]['durations']) > 0:
        ttl += '''      
      :duration '''
        for duration in cinema_json['films'][film]['durations']:
            ttl += f'''"{duration}"^^xsd:double ,
                '''
        ttl = ttl[:-18] + ';'

    ttl = ttl[:-1] + '.\n\n\n'


print(ttl)