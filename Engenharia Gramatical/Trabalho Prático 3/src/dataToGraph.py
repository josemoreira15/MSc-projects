from PIL import Image
import graphviz, io, json, sys


with open(f'../data/graph/{sys.argv[1]}.txt') as dot_file:
    data = dot_file.read()

graph = graphviz.Source(data)
image = Image.open(io.BytesIO(graph.pipe(format='png')))
image.save(f'../output/graph/{sys.argv[1]}.png')
