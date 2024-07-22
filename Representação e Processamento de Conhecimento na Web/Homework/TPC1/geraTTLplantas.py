import json

f = open("plantas.json")
bd = json.load(f)
f.close()

ttl = ""

for planta in bd:
    registo = f"""
###  http://rpcw.di.uminho.pt/2024/plantas#{planta['_id']}
<http://rpcw.di.uminho.pt/2024/plantas#{planta['_id']}> rdf:type owl:NamedIndividual ,
                                                      :Planta ;
                                             :_id "{planta['_id']}" ;
                                             :NumeroDeRegisto "{planta['NumeroDeRegisto']}"^^xsd:int ;
                                             :CodigoDeRua "{planta['CodigoDeRua']}"^^xsd:int ;
                                             :Rua "{planta['Rua']}" ;
                                             :noLocal :{planta['Local'].replace(" ","_")} ;
                                             :naFreguesia :{planta['Freguesia'].replace(" ","_")} ;
                                             :temEspecie :{planta['Especie'].replace(" ","_")} ; 
                                             :temNomeCientifico :{planta['NomeCientifico'].replace(" ","_")} ;
                                             :temOrigem :{planta['Origem'].replace(" ","_")} ;
                                             :DataDePlantacao "{planta['DataDePlantacao']}"
                                             :Estado "{planta['Estado']}" ;
                                             :Caldeira "{planta['Caldeira']}" ;
                                             :Tutor "{planta['Tutor']}" ;
                                             :Implantacao "{planta['Implantacao']}" ;
                                             :temGestor :{planta['Gestor'].replace(" ","_")} ;
                                             :DataDeActualizacao "{planta['DataDeActualizacao']}" ;
                                             :NumeroDeIntervencoes "{planta['NumeroDeIntervencoes']}" .

###  http://rpcw.di.uminho.pt/2024/plantas#{planta['Local'].replace(" ","_")}
:{planta['Local'].replace(" ","_")} rdf:type owl:NamedIndividual ,
                :Local .

###  http://rpcw.di.uminho.pt/2024/plantas#{planta['Freguesia'].replace(" ","_")}
:{planta['Freguesia'].replace(" ","_")} rdf:type owl:NamedIndividual ,
                :Freguesia .

###  http://rpcw.di.uminho.pt/2024/plantas#{planta['Especie'].replace(" ","_")}
:{planta['Especie'].replace(" ","_")} rdf:type owl:NamedIndividual ,
                :Especie .

###  http://rpcw.di.uminho.pt/2024/plantas#{planta['NomeCientifico'].replace(" ","_")}
:{planta['NomeCientifico'].replace(" ","_")} rdf:type owl:NamedIndividual ,
                :NomeCientifico .

###  http://rpcw.di.uminho.pt/2024/plantas#{planta['Origem'].replace(" ","_")}
:{planta['Origem'].replace(" ","_")} rdf:type owl:NamedIndividual ,
                :Origem .

###  http://rpcw.di.uminho.pt/2024/plantas#{planta['Gestor'].replace(" ","_")}
:{planta['Gestor'].replace(" ","_")} rdf:type owl:NamedIndividual ,
                :Gestor .
""" 
    ttl += registo

print(ttl)
