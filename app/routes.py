from flask import render_template, request, jsonify
from app import app
from app.tcr_main import resolver_sistema_tcr

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/resolver', methods=['POST'])
def resolver():
    dados = request.get_json()
    resultado = resolver_sistema_tcr(dados)
    return jsonify(resultado)