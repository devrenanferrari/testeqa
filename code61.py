def calcular_media(numeros)
    soma = 0
    for numero in numeros:
        soma += numero
    media = soma / len(numeros
    return media

lista = [1, 2, 3, "4", 5]
resultado = calcular_media(lista)
print("A média é: " + resultado)
