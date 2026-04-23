def sumar(*numeros):
    print(numeros)           # (1, 2, 3, 4, 5)
    return sum(numeros)


numeros_ingresados = []

while True:
    entrada = input("Ingresa un numero (o escribe 'fin' para terminar)")

    if entrada == "fin":
        break

    numero = int(entrada)
    numeros_ingresados.append(numero)

total = sumar(*numeros_ingresados)
print(f"el total es {total}")


