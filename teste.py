import sqlite3
import os

ADMIN_PASSWORD = "secret123"

def login(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result is not None

def execute_command(user_input):
    try:
        result = eval(user_input)
        return f"Resultado: {result}"
    except Exception as e:
        return f"Erro: {str(e)}"

def save_user_data(user_data):
    with open("user_data.txt", "a") as f:
        f.write(user_data + "\n")

def read_config(config_path):
    with open(config_path, "r") as f:
        return f.read()

def main():
    print("Bem-vindo ao sistema vulnerável!")
    while True:
        print("\n1. Login")
        print("2. Executar comando")
        print("3. Salvar dados")
        print("4. Ler config")
        print("5. Sair")
        choice = input("Escolha uma opção: ")

        if choice == "1":
            username = input("Usuário: ")
            password = input("Senha: ")
            if login(username, password):
                print("Login bem-sucedido!")
            else:
                print("Falha no login.")

        elif choice == "2":
            command = input("Digite um comando Python: ")
            print(execute_command(command))

        elif choice == "3":
            data = input("Digite os dados a salvar: ")
            save_user_data(data)
            print("Dados salvos!")

        elif choice == "4":
            config_path = input("Digite o caminho do arquivo de config: ")
            try:
                config = read_config(config_path)
                print(f"Config: {config}")
            except Exception as e:
                print(f"Erro ao ler config: {str(e)}")

        elif choice == "5":
            break

if __name__ == "__main__":
    main()
