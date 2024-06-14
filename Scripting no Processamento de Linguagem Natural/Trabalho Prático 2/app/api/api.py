from flask import Flask, request, jsonify
from word_embeddings import WB_Model
from transformers import pipeline
import os

wb_model = WB_Model('../../data/dre.json')
wb_model.load_model('models/dr.model')

app = Flask(__name__)

context = ''

def get_text(id):
    file_path = f'../../data/texts/{id}.txt'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    return ''


@app.post('/chat')
def chat():
    user_message = request.json['message']
   
    most_similar = wb_model.get_most_similar(user_message, 10)
    context = ''.join(get_text(id) for id, note, score in most_similar )
 
    question_answerer = pipeline("question-answering", model="mrm8488/bert-base-portuguese-cased-finetuned-squad-v1-pt")
    result = question_answerer(question=user_message, context=context)
    return jsonify({'response': result['answer']})


if __name__ == '__main__':
    app.run(port=23241, debug=True)