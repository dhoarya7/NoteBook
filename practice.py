from flask import Flask, jsonify
import requests

app = Flask(__name__)

# Kunci API yang valid
api_key = '3e0a68a9-2fdc-4b85-9e8e-64488a147c6d'

@app.route('/define/<word>', methods=['GET'])
def define_word(word):
    # URL dasar dari API
    root_url = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json'
    # Membuat URL lengkap dengan kata dan kunci API
    final_url = f'{root_url}/{word}?key={api_key}'

    # Mengambil data dari API
    r = requests.get(final_url)

    # Memastikan permintaan berhasil
    if r.status_code == 200:
        try:
            result = r.json()
            return jsonify(result)
        except ValueError:
            return jsonify({"error": "Response tidak bisa di-decode sebagai JSON."}), 500
    else:
        return jsonify({
            "error": "Terjadi kesalahan saat memanggil API.",
            "status_code": r.status_code,
            "content": r.text
        }), r.status_code


