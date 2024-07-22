import json
import re
import ast

with open('dataset.json') as file:
    content = json.load(file)

def convert_to_list(value):
    try:
        return ast.literal_eval(value)
    
    except (ValueError, SyntaxError):
        return value

processed_content = []
for obj in content:
    final_content = {}
    for key, value in obj.items():
        if key in ['genres', 'characters', 'awards', 'ratingsByStars', 'setting']:
            final_content[key] = convert_to_list(value)
        else:
            final_content[key] = value
    processed_content.append(final_content)


with open('clean_dataset.json', 'w') as final_file:
    json.dump(processed_content, final_file, indent=4)