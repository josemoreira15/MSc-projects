import json
import re

ttl = ''

authors = set()
characters = set()
publishers = set()
places = set()
genres = set()
awards = set()


def replace_non_alphanumeric_with_underscore(input_string):
    # Substitui todos os caracteres que não são letras ou números por '_'
    return re.sub(r'[^a-zA-Z0-9]', '_', input_string)

def create_valid(id):
    return replace_non_alphanumeric_with_underscore(id)
    # return id.replace(' ', '_').replace('"', '').replace("'", '').replace('(', '').replace(')','').replace(',','').replace('!', '').replace('.', '').replace('?', '').replace('&', '').replace('/','').replace('’', '').replace('-','').replace('“', '').replace('”', '').replace('–', '').replace('#', '').replace('●','').replace('„', '').replace(';', '')

with open('clean_dataset.json') as file:
    content = json.load(file)


book_count = 0
for book in content:
    if len(book['ratingsByStars']) > 0:
        uma = book['ratingsByStars'][0]
        duas = book['ratingsByStars'][1]
        tres = book['ratingsByStars'][2]
        quatro = book['ratingsByStars'][3]
        cinco = book['ratingsByStars'][4]

    else:
        uma = 0
        duas = 0
        tres = 0
        quatro = 0
        cinco = 0

    description = book['description'].replace("'",'').replace('\n', '').replace('"', '')
    title = book['title'].replace('"', '').replace("'", '')
    pubdate = book['publishDate'].replace('\n', '').replace('"', '').replace("'", '')
    series = book['series'].replace('"', '').replace("'", '')
    edition = book['edition'].replace('"', '').replace("'", '')

    ttl += f'''
###  http://rpcw.di.uminho.pt/2024/untitled-ontology-34#Livro{book_count}
:Livro{book_count} rdf:type owl:NamedIndividual ,
                 :Book ;
        :bbescore "{book['bbeScore']}"^^xsd:int ;
        :bbevotes "{book['bbeVotes']}"^^xsd:int ;
        :coverimg "{book['coverImg']}" ;
        :description "{description}" ;
        :edition "{edition}" ;
        :firstpubdate "{book['firstPublishDate']}" ;
        :fivestars "{cinco}"^^xsd:int ;
        :format "{book['bookFormat']}" ;
        :fourstars "{quatro}"^^xsd:int ;
        :id "{book['bookId']}" ;
        :isbn "{book['isbn']}"^^xsd:int ;
        :language "{book['language']}" ;
        :likedpercent "{book['likedPercent']}"^^xsd:int ;
        :numratings "{book['numRatings']}"^^xsd:int ;
        :onestar "{uma}"^^xsd:int ;
        :pages "{book['pages']}"^^xsd:int ;
        :price "{book['price']}"^^xsd:float ;
        :pubdate "{pubdate}" ;
        :rating "{book['rating']}"^^xsd:float ;
        :series "{series}" ;
        :threestars "{tres}"^^xsd:int ;
        :title "{title}" ;
        :twostars "{duas}"^^xsd:int ;
'''
    
    authorss = book['author'].split(', ')
    for author in authorss:
        id = create_valid(author)
        authors.add(id)
        ttl += f'        :hasAuthor :{id};\n'

    
    for genre in book['genres']:
        id = create_valid(genre)
        genres.add(id)
        ttl += f'        :hasGenre :{id};\n'

    
    for character in book['characters']:
        id = create_valid(character)
        characters.add(id)
        ttl += f'        :hasCharacter :{id};\n'

    
    for award in book['awards']:
        id = create_valid(award)
        awards.add(id)
        ttl += f'        :hasAward :{id};\n'

    
    for setting in book['setting']:
        id = create_valid(setting)
        places.add(id)
        ttl += f'        :hasSetting :{id};\n'

    ttl += f'        :hasPublisher :{create_valid(book["publisher"])}.\n'

    book_count += 1


for award in awards:
    ttl += f'''
###  http://rpcw.di.uminho.pt/2024/untitled-ontology-34#{award}
:{award} rdf:type owl:NamedIndividual ,
                    :Award .
'''

for genre in genres:
    ttl += f'''
###  http://rpcw.di.uminho.pt/2024/untitled-ontology-34#{genre}
:{genre} rdf:type owl:NamedIndividual ,
                  :Genre .
'''
    
for character in characters:
    ttl += f'''
###  http://rpcw.di.uminho.pt/2024/untitled-ontology-34#{character}
:{character} rdf:type owl:NamedIndividual ,
                  :Character .
'''


for place in places:
    ttl += f'''
###  http://rpcw.di.uminho.pt/2024/untitled-ontology-34#{place}
:{place} rdf:type owl:NamedIndividual ,
                :Place .
'''
    

for publisher in publishers:
    ttl += f'''
###  http://rpcw.di.uminho.pt/2024/untitled-ontology-34#{publisher}
:{publisher} rdf:type owl:NamedIndividual ,
                     :Publisher .

'''
    

for author in authors:
    ttl += f'''
###  http://rpcw.di.uminho.pt/2024/untitled-ontology-34#{author}
:{author} rdf:type owl:NamedIndividual ,
                          :Author .
'''
    
print(ttl)