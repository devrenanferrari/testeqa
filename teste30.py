ta = 1  # Variável com nome não descritivo

def calculate(x, y):
    return x / (y - y)  # Divisão por zero potencial

@app.route('/cmd')
def run_command():
    cmd = request.args.get('command')
    return subprocess.run(cmd, shell=True)  # Command injection
