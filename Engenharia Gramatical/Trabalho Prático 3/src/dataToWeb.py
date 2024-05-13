import json, sys


with open(f'../data/web/{sys.argv[1]}.json') as json_file:
    dados = json.load(json_file)

html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Source Code Analyzer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            color: #333;
        }
        header {
            background-color: #333;
            color: #fff;
            padding: 20px;
            text-align: center;
        }
        .container {
            max-width: 1200px;
            margin: auto;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;

        }
        .column {
            width: 22%;
            padding: 10px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        h1, h2 {
            margin-top: 20px;
        }
        li {
            margin-bottom: 10px;
        }
        li ul {
            margin-top: 5px;
            margin-left: 20px;
        }
        li ul li {
            margin-bottom: 5px;
        }
        footer {
            background-color: #333;
            color: #fff;
            padding: 5px;
            text-align: center;
        }

    </style>
</head>
<body>
    <header>
        <h1>Functions</h1>
    </header>
'''

for function in dados['infos'].keys():
    if function != 'global':


        html += f'''
        <ul>        
            <li><h1>{function}</h1></li>
        </ul>
        <div class="container">
            <div class="column">
                <h2>Instructions</h2>'''
        
        for instruction, count in dados['infos'][function]['instructions'].items():

            html += f'''
            <ul>     
                <li>{instruction}: {count}</li>
            </ul>'''
        html += '''        </div>\n        <div class="column">
            <h2>Variables logs</h2>'''
        for log in dados['infos'][function]['vars_logs']:
            html += f'''    <ul>
                <li>{ log }</li>
            </ul>'''
        html += '''        </div>\n        <div class="column">
            <h2>Errors</h2>'''
        for error in dados['infos'][function]['errors']:
            html += f'''    <ul>
                <li>{ error }</li>
            </ul>\n'''
    
    html +='''    </div>
    </div>'''

html += '''
    <header>
        <h1>Scripted code</h1>
    </header>
        <div class="container">
            <div class="column">
                <h2>Instructions</h2>'''
        
for instruction, count in dados['infos']['global']['instructions'].items():
    html += f'''
            <ul>
                <li>{instruction}: {count}</li>
            </ul>\n'''
html += '''        </div>\n        <div class="column">
            <h2>Variables logs</h2>\n'''
for log in dados['infos']['global']['vars_logs']:
    html += f'''            <ul>
                <li>{ log }</li>
            </ul>\n'''
html += '''        </div>\n        <div class="column">
        <h2>Errors</h2>\n'''
for error in dados['infos']['global']['errors']:
    html += f'''            <ul>
                <li>{ error }</li>
            </ul>\n'''

html += '''        </div>
    </div>
    <header>
        <h1>Global Statistics</h1>
    </header>
    <div class="container">
        <div class="column">
                <h2>Variables per Type</h2>
            <ul>\n'''

for tipo, count in dados['gstats']['vars_per_type'].items():
    html += f'''                <li>{ tipo }: { count }</li>\n'''
            
    
html += f'''            </ul>
        </div>
        <div class="column">
            <h2>Functions</h2>
            <ul>\n'''

for function, (tipo, args) in dados['gstats']['functions'].items():
    html += f'''                <li>{ function } ({ tipo }) - Args: { args }</li>\n'''
            
    
html += f'''            </ul>
        </div>
        <div class="column">
            <h2>Instructions</h2>
            <ul>\n'''

for instruction, count in dados['gstats']['instructions'].items():
    html += f'''                <li>{ instruction }: { count }</li>\n'''
        
html += f'''            </ul>
        </div>
        <div class="column">
            <h2>Nested Structures</h2>
                <p>{dados['gstats']['nested_structures'] }</p>
            <h2>Nested "ifs" that can be replaced by one</h2>
                <p>{ dados['gstats']['nested_replace_ifs']}</p>
        </div>
    </div>
    <footer>
        <p>Duarte Parente, Gonçalo Pereira, José Moreira - Engenharia de Linguagens - Mestrado em Engenharia Informática, Universidade do Minho</p>
    </footer>
</body>
</html>
'''

with open(f"../output/web/{sys.argv[1]}.html", "w") as file:
    file.write(html)