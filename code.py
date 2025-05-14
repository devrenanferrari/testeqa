# problematic_code.py
import os
import subprocess
import pickle
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/unsafe')
def unsafe_operations():
    # 1. Command Injection
    cmd = request.args.get('command')
    subprocess.run(cmd, shell=True)  # Risco alto
    
    # 2. SQL Injection
    user_id = request.args.get('id')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # Risco alto
    
    # 3. Uso de pickle inseguro
    data = request.get_data()
    loaded = pickle.loads(data)  # Risco alto
    
    # 4. Hardcoded password
    db_password = "senha123"  # Risco médio
    
    # 5. Divisão por zero potencial
    x = 10
    y = 0
    result = x / y  # Risco alto
    
    # 6. Variáveis não descriptivas
    a = 1  # Risco baixo
    b = 2
    
    # 7. Código duplicado
    print("Starting process...")
    print("Starting process...")  # Risco baixo
    
    # 8. Retorno inconsistente
    if x > 5:
        return "Success"
    # Falta else/return
    
    # 9. Uso de versão vulnerável de biblioteca
    # (Será detectado pelo requirements.txt)
    
    return "Done"

# 10. Falta de tratamento de exceções
def read_file():
    with open('secret.txt') as f:
        return f.read()

# 11. Uso de métodos depreciados
def old_method():
    import md5  # Risco médio
    return md5.new("text").hexdigest()

# 12. Vazamento de informação
@app.errorhandler(500)
def handle_error(e):
    return str(e)  # Mostra detalhes internos - Risco alto
