
import os
import subprocess
from flask import Flask, request

app = Flask(__name__)

@app.route('/execute')
def execute_command():
    # Vulnerabilidade grave: Command Injection
    cmd = request.args.get('cmd')
    return subprocess.check_output(cmd, shell=True)  # UNSAFE!

def calculate_age(birth_year):
    # Problema lógico: não verifica ano futuro
    return 2023 - birth_year  # Bug se birth_year > 2023

def get_user_data(user_id):
    # Problema de segurança: SQL Injection
    query = f"SELECT * FROM users WHERE id = {user_id}"  # UNSAFE!
    return db.execute(query)

def process_payment(amount):
    # Problema de estilo: código duplicado
    if amount > 1000:
        print("Large payment")
    if amount > 1000:  # Duplicação
        print("Large payment")
    
    # Falta tratamento de erros
    return
