# Define la función generadora
def leer_personas(archivo):
    with open(archivo, "r") as f:
        next(f)  # saltar el header
        for linea in f:
            nombre, edad, ciudad = linea.strip().split(",")
            try:
                edad = int(edad)
            except ValueError:
                print(f"Edad inválida '{edad}', se omite la fila")
                continue
            yield {
                "nombre": nombre,
                "edad": edad,
                "ciudad": ciudad
            }

# Consumir el generador y construir lista de personas
personas = [p for p in leer_personas("datos.csv")]

# Filtrar bogotanos
bogotanos = [p for p in personas if p["ciudad"] == "Bogota"]

print(bogotanos)