import subprocess

def analyze_pylint():
    result = subprocess.run(
        ['pylint', '.', '--disable=R,C', '--output-format=text'],
        capture_output=True, text=True
    )
    return result.stdout

def analyze_flake8():
    result = subprocess.run(['flake8', '.'], capture_output=True, text=True)
    return result.stdout

def analyze_bandit():
    result = subprocess.run(['bandit', '-r', '.'], capture_output=True, text=True)
    return result.stdout

def main():
    pylint_result = analyze_pylint()
    flake8_result = analyze_flake8()
    bandit_result = analyze_bandit()

    with open("analysis_report.txt", "w") as report_file:
        report_file.write("### Pylint Report ###\n")
        report_file.write(pylint_result + "\n")
        report_file.write("### Flake8 Report ###\n")
        report_file.write(flake8_result + "\n")
        report_file.write("### Bandit Report ###\n")
        report_file.write(bandit_result + "\n")

if __name__ == "__main__":
    main()
