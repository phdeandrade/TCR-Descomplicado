from flask import render_template, request, jsonify
from app import app
# Importamos a lógica que vamos criar para o TCR
from app.tcr_solver import resolver_sistema_tcr

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
    # Chama a função de lógica (que está no tcr_solver.py)
    resultado = resolver_sistema_tcr(dados)
    return jsonify(resultado)