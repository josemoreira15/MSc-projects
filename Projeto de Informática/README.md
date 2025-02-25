
# Documentação da Camada Operacional do Projeto


## Índice
1. [Visão Geral das Classes](#visão-geral-dos-ficheiros)
2. [Ficheiro `dxf_reader.py`](#ficheiro-dxf_readerpy)
3. [Ficheiro `dxf_interpreter.py`](#ficheiro-dxf_interpreterpy)
4. [Ficheiro `dxf_graph.py`](#ficheiro-dxf_graphpy)
5. [Exemplo de um Fluxo de Execução Completo](#exemplos-de-utilização)
6. [Dependências](#dependências)

---

## Visão Geral das Classes

### `DXF_Reader`
Responsável por ler ficheiros DXF utilizando a biblioteca `ezdxf`. Converte as entidades DXF em uma estrutura em formato JSON contendo informações detalhadas sobre geometrias e atributos.

### `DXF_Interpreter`
Processa os dados lidos pelo `dxf_reader.py`, identificando e categorizando elementos na imagem.

#### Inicializador do construtor

```python
DXF_Interpreter( full_dxf_filepath , v1_dxf_filepath, table_image, class_configs )
```

### `DXF_Graph`
Constrói um grafo utilizando as detecções processadas pelo `dxf_interpreter.py`, permitindo modelar as relações espaciais entre os elementos da tábua.

#### Inicializador do construtor

```
DXF_Graph( DXF_Interpreter.detections, DXF_Interpreter.get_red_lines(), class_configs )
```

### `class_configs`
Ficheiro de configuração em formato json, representando as definições de cada classe de deteção de componentes

```json
{
  "nome da classe": {
    
    "color": determina a cor da caixa de deteção do componente. Caso não exista siginifica que a deteção do componente não é desenhada na interface da aplicação
    "is_labeled": determina se o componente pode ter ou não etiqueta
    "fix": determina se a classe pode ser apagada ou não
  }
}
```

---

## Ficheiro `dxf_reader.py`

### Funções Principais
1. **`read_dxf(dxf_filepath)`**  
   Lê o ficheiro DXF e retorna uma estrutura num formato JSON dos dados.  
   - **Input**: Caminho do ficheiro DXF.  
   - **Output**: Estrutura de dados contendo informações esquematizadas por blocos e com informações sobre as suas respetivas entidades e atributos.

### Dados DXF
Os dados extraídos são estruturados da seguinte forma:
```json
{
    "*Model_Space": [
        {
            "type": "POLYLINE",
            "attributes": {
                "layer": "SELECTION",
                "color": 1,
                "handle": "1B",
                "owner": "7C26"
            },
            "geometry": [
                [
                    3197.7,
                    648.51,
                    0.0
                ],
                [
                    3199.7,
                    648.51,
                    0.0
                ]
            ]
        }
    ]
}
```


### Exemplo de Utilização
```python
from dxf_reader import DXF_Reader

data = DXF_Reader.read_dxf("example.dxf")
print(data)
```

---

## Ficheiro `dxf_interpreter.py`

### Funções Principais
1. **`get_red_lines()`**  
   Extrai as linhas vermelhas, em representação das ligações entre os componentes, presentes no DXF relativo à versão 1 da tábua de montagem.
2. **`get_text()`**  
   Retorna todos os elementos textuais presentes no DXF, incluindo a sua layer e coordenadas.
3. **`process_dxf_file()`**  
   Processa as entidades DXF para tentar identificar:
   - Nós (`nodes`)
   - Entidades com prefixo `2P6` (`forks`)
   - Entidades com prefixo `2P_` (`clamp`)
   - Entidades com prefixo `1P55_MARCA` (`perno_marca`)
   - Entidades com prefixo `1P65_6L` (`pin`)
   - Entidades com prefixo `1P60_6` (`assembly_guide`)
   - Entidades com prefixo `1E` (`olhal`)
   - Entidades com prefixo `$SPACETAPE$` (`markings_up`)
   - Entidades com prefixo `$SPIRALTAPE$` (`spiral_up`)
   - Entidades com prefixo `$HANDTAPE$` (`total_bandage_up`)
   - Entidades com prefixo `$USPACETAPE$` (`markings_down`)
   - Entidades com prefixo `P0` (`component`)
   - Clips, componentes com prefico `P0` associados a um Clip_ID por proximidade (`clip`)
   - Tubos, com a respetiva identificação e coordenada da ponta da seta (`tubo`)
   - Splices, com a respetiva identificação, associação ao nodo de ligação na tábua de montagem, e identificação dos fios nela contidos
   - Módulos, contendo `modbi` e `mod` na sua identificação (`big_node`)
   - Conectores, com a respetiva identificação dos fios nele contidos(`wire_boxes`)
4. **`process_pos_graph(leaf_nodes)`**
    - **Input**: Nós folha do grafo.

   Efetua o mapeamento final dos componentes através de uma estratégia de associação por proximidade. Associa as etiquetas aos nodos terminais mais próximos e às respetivas `wire_boxes`
5. **`get_wire_connections()`**
   Retorna uma lista com os fios capturados na tábua de montagem e a respetiva informação do nodo de entrada e saída.

   - **Output**: (Wire_ID, node1, node2).



### Estruturas de Saída
- **`detections`**: Dicionário com informações sobre objetos detectados.  

```json
{
  "detection_id": {
    "class" : classe atribuída à deteção do objeto
    "value" : se a classe for node corresponde ao id do objeto, se for mm corresponde aos milímetros
    "center" : coordenadas da posição em que se encontra
    "splice": id do componente splice correspondente
    "x1": coordenada do limite à esquerda num referencial 2D com (0,0) no canto superior esquerdo
    "x2": coordenada do limite à direita num referencial 2D com (0,0) no canto superior esquerdo
    "y1": coordenada do limite superior num referencial 2D com (0,0) no canto superior esquerdo
    "y2": coordenada do limite inferior num referencial 2D com (0,0) no canto superior esquerdo
    "text": texto associado
    "insert_coords": coordenadas de inserção do componente 
    "drilling_points": coordenadas de perfuração do componente
    "arrow_pointer": coordenadas da seta
    "wires": lista de fios do componente
  }
}
```


### Exemplo de Utilização
```python
from dxf_interpreter import DXF_Interpreter

interpreter = DXF_Interpreter("file.dxf", "v1_file.dxf", "file.png", class_configs)
interpreter.process_dxf_file()
print(interpreter.detections)
```

---

## Ficheiro `dxf_graph.py`

### Funções Principais
1. **`build_graph(min_length)`** 
    - **Input**: Comprimento mínimo da linha vermelha para ser considerada uma aresta.

   Constrói um grafo, em representação da tábua de montagem em questão.
2. **`update_detections(updated_detections)`** 
   Atualiza as deteções e constói a estrutura de associação entre etiquetas e os nós a elas associados
3. **`get_leaf_nodes()`** 
   Retorna os IDs dos nós folha do grafo
4. **`get_shortest_path(start_node, end_node)`**  
   Calcula o caminho mais curto entre dois nós.
  - **Output**: 
    > `None`: caso não exista caminho, ou o nó não tenha sido identificado.
    
    > Lista com os IDs das arestas do caminho identificado.

### Estruturas de Saída
- **`graph`**: Estrutura em representação do Grafo construído utilizando `networkx`.
- **`edges`**: Dicionário contendo as arestas e nós conectados.

```json
{
  "edge_id": {
    "node1": node1_id,
    "node2": node2_id,
    "length": 50.0
  }
}
```
- **`positions`**: Dicionário contendo a posição dos cada nó.
```json
{
  "node_id": (x, y)
}
```
- **`pairs`**: Dicionário contendo associação entre cada etiqueta e o respetivo nó.
```json
{
  "X403": node_id
}
```

### Exemplo de Utilização
```python
from dxf_graph import DXF_Graph

graph = DXF_Graph("Cable", detections, red_lines, configs)
graph.build_graph()
graph.update_detections(updated_detections)
print(graph.edges)
print(graph.pairs)
```

---

## Exemplo de um Fluxo de Execução Completo

```python
from dxf_interpreter import DXF_Interpreter
from dxf_graph import DXF_Graph
import json

class_configs = json.load(open("configs.json"))

interpreter = DXF_Interpreter("example.dxf", "example_v1.dxf", "example.png", class_configs)
interpreter.process_dxf_file()

graph = DXF_Graph(interpreter.detections, interpreter.get_red_lines(), configs)
graph.build_graph(min_length=20)

interpreter.process_pos_graph(graph.get_leaf_nodes())

graph.update_detections(interpreter.detections)

wires = DXF_Interpreter.get_wire_connections(interpreter.detections)

for wire in wires:
  print(wire, graph.get_shortest_path(wire[1], wire[2]))
```

---

## Dependências

- **Bibliotecas**:
  - `ezdxf`: Para leitura e manipulação de ficheiros DXF.
  - `cv2` (OpenCV): Para manipulação de imagens.
  - `networkx`: Para construção e manipulação de grafos.
  - `uuid`: Para geração de identificadores únicos.

---