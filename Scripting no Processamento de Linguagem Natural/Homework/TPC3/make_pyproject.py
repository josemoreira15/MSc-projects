#!/usr/bin/env python3
'''
NAME
    makepyproject - pyproject.toml generator
'''


import jinja2
from glob import glob
from pathlib import Path
import json


modes = glob("*.py")
if len(modes) > 1:
    if modes[0] != "make_pyproject.py":
        name = modes[0][:-3]
    else:
        name = modes[1][:-3]
else:
    name = input("Module: ")


meta_path = str(Path.home()) + "/metadata.json"
try: 
    with open (meta_path, "r") as metafile:
        metadata = json.load(metafile)
        author = metadata['author']
        email = metadata['email']

except FileNotFoundError:
    author = input("Author: ")
    email = input("Email: ")

python_version = input("Pyhton version required: ")

dps_l = []
dps = int(input("Number of dependencies: "))

for ct in range (0, dps):
    dp = input(f"Dependency {ct + 1}: ")
    dps_l.append(dp)


pp = jinja2.Template('''[build-system]
requires = ["flit_core >=3.2,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "{{name}}"
authors = [
    {name = "{{autor}}", email="{{email}}"},
]
classifiers = [
    "License :: OSI Approved :: MIT License",
]
requires-python = ">={{python_version}}"
dynamic = ["version", "description"]

dependencies = {{dependencies}}

[project.scripts]
{{name}} = "{{name}}:main"''')

r = pp.render({"name": name, "autor": author, "email": email, "python_version": python_version, "dependencies": dps_l})

with open("pyproject.toml", "w") as py_file:
    py_file.write(r)