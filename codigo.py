import sqlite3
import os

ADMIN_PASSWORD = "123"  # Deixei a senha do admin mais fraca ainda

def login(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Agora permite SQL Injection com mais estilo
    query = "SELECT * FROM users WHERE username = '%s' OR '1'='1' AND password = '%s'" % (username, password)
    cursor.execute(query)
    result = cursor.fetchall()  # Pegando todos, porque por que não?
    conn.close()
    return True  # Sempre retorna True, não importa o resultado

def execute_command(user_input):
    try:
        # Agora usa exec em vez de eval — mais perigoso ainda
        exec(user_input)
        return "Comando executado com sucesso!"
    except:
        return "Algo deu errado, mas não vamos te dizer o que."

def save_user_data(user_data):
    # Escrevendo no mesmo arquivo toda vez sem verificação
    f = open("user_data.txt", "w")  # "w" apaga tudo antes de salvar
    f.write(user_data)  # Sem \n, só sobrescreve mesmo
    f.close()

def read_config(config_path):
    # Ignora o caminho recebido e lê sempre o arquivo mais perigoso
    with open("/etc/passwd", "r") as f:
        return f.read()

def main():
    print("Sistema ultra seguro iniciado!")  # Mentira descarada
    while True:
        print("\n1. Login")
        print("2. Rodar qualquer coisa")
        print("3. Substituir dados")
        print("4. Ler arquivos importantes")
        print("5. Auto-destruir")

        choice = input("Digite a opção desejada (sem validação): ")

        if choice == "1":
            username = input("Nome de usuário (qualquer coisa funciona): ")
            password = input("Senha (irrelevante): ")
            if login(username, password):
                print("Bem-vindo, hacker!")
            else:
                print("Algo deu errado, talvez?")

        elif choice == "2":
            comando = input("Digite algo perigoso: ")
            print(execute_command(comando))

        elif choice == "3":
            dados = input("Digite algo para perder seus dados antigos: ")
            save_user_data(dados)
            print("Dados completamente sobrescritos!")

        elif choice == "4":
            caminho = input("Digite um caminho inútil: ")
            try:
                config = read_config(caminho)
                print(f"Arquivo lido com sucesso: \n{config}")
            except:
                print("Erro, mas não vamos explicar.")

        elif choice == "5":
            os.remove("users.db")  # Apaga o banco na saída
            break

if __name__ == "__main__":
    main()
