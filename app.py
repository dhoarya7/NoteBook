import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify
from pymongo import MongoClient
import requests
from datetime import datetime
from bson import ObjectId

# environment variabel dri env
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# nilai dari file .env
mongo_password = os.getenv("MONGO_PASSWORD")
mongo_user = os.getenv("MONGO_USER")
mongo_host = os.getenv("MONGO_HOST")
mongo_db_name = os.getenv("MONGO_DB")
api_key = os.getenv("DICTIONARY_API_KEY")

# inisial flask
app = Flask(__name__)

# Setup MongoDB connection
cxn_str = f'mongodb://{mongo_user}:{mongo_password}@{mongo_host}/?ssl=true&replicaSet=atlas-ld9kmy-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(cxn_str)
db = client[mongo_db_name]

@app.route('/')
def main():
    words_result = db.words.find({}, {'_id': False})
    words = []
    for word in words_result:
        definition = word['definitions'][0]['shortdef']
        definition = definition if type(definition) is str else definition[0]
        words.append({
            'word': word['word'],
            'definition': definition,
        })
    msg = request.args.get('msg')
    return render_template(
        'index.html',
        words=words,
        msg=msg
    )

@app.route('/detail/<keyword>')
def detail(keyword):
    api_key = '3e0a68a9-2fdc-4b85-9e8e-64488a147c6d'
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response = requests.get(url)
    definitions = response.json()

    if not definitions:
        return render_template('error.html', word=keyword)

    # Jika API memberikan saran kata (array string)
    if isinstance(definitions[0], str):
        suggestions = definitions
        return render_template('error.html', word=keyword, suggestions=suggestions)

    # Jika kata ditemukan, tampilkan definisi
    status = request.args.get('status_give', 'new')
    return render_template(
        'detail.html',
        word=keyword,
        definitions=definitions,
        status=status
    )


@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')
    doc = {
        'word': word,
        'definitions': definitions,
        'date' : datetime.now().strftime('%Y%m%d'),
    }
    db.words.insert_one(doc)
    return jsonify({
        'result': 'success',
        'msg': f'the word, {word}, was saved!!!',
    })

@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    db.words.delete_one({'word': word})
    return jsonify({
        'result': 'success',
        'msg': f'The word {word} was deleted'
    })

@app.route('/api/get_exs', methods=['GET'])
def get_exs():
    word = request.args.get('word')
    example_data = db.examples.find({'word':word})
    examples =[]
    for example in example_data:
        examples.append({
            'examples' :example.get('example'),
            'id': str(example.get('_id')),
        })
    return jsonify({
        'result': 'success',
        'examples' : examples
        })

@app.route('/api/save_ex', methods=['POST'])
def save_ex():
    json_data = request.get_json()
    word = json_data.get('word')
    example = json_data.get('example')
    doc = {
        'word': word,
        'example': example,
    }
    db.examples.insert_one(doc)
    return jsonify({
        'result': 'success',
        'msg': f'Your example, "{example}", for the word "{word}" was saved!',
    })



@app.route('/api/delete_ex', methods=['POST'])
def delete_ex():
    json_data = request.get_json()
    id = json_data.get('id')
    word = json_data.get('word')
    db.examples.delete_one({'_id': ObjectId(id)})
    return jsonify({
        'result': 'success',
        'msg': f'Your example for the word "{word}" was deleted!',
    })

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)