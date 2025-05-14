import os, sys

def read_file(filename):
    file = open(filename, 'r')
    content = file.read()
    return content

def divide(a, b):
    try:
        return a / b
    except:
        return "erro"

def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] % 2 == 0:
            result.append(data[i] * 2)
        else:
            result.append(data[i] + 1)
    return result

def main():
    data = [1, 2, 3, 4, 5]
    print("Resultados:")
    for i in range(0, len(data)):
        process_data(data)

    print(divide(10, 0))
    print(read_file("arquivo_inexistente.txt"))

main()
