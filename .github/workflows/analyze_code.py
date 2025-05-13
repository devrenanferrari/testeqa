import subprocess

def analyze_pylint():
    result = subprocess.run(['pylint', '--disable=R,C', '--output-format=text'], capture_output=True, text=True)
    return result.stdout

def analyze_flake8():
    result = subprocess.run(['flake8', '--max-line-length=79'], capture_output=True, text=True)
    return result.stdout

def analyze_bandit():
    result = subprocess.run(['bandit', '-r', '.'], capture_output=True, text=True)
    return result.stdout

def main():
    pylint_result = analyze_pylint()
    flake8_result = analyze_flake8()
    bandit_result = analyze_bandit()

    # Salvar os resultados em um arquivo de texto
    with open("analysis_report.txt", "w") as file:
        file.write("Resultado da análise com PyLint:\n")
        file.write(pylint_result)
        file.write("\nResultado da análise com Flake8:\n")
        file.write(flake8_result)
        file.write("\nResultado da análise de segurança com Bandit:\n")
        file.write(bandit_result)

if __name__ == "__main__":
    main()
