def leer_lineas(archivo):
    with open(archivo, "r") as f:
        for linea in f:
            yield linea.strip()

for linea in leer_lineas("datos.csv"):
    print(linea)

generador = leer_lineas("datos.csv")
print(type(generador))