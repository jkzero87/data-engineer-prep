persona = []

with open("datos.csv", "r") as archivo:
    next(archivo) # Skip the header line

    for linea in archivo:
        nombre, edad, ciudad = linea.strip().split(",")

        try:
            edad = int(edad)
     
        except ValueError:
            print(f"Error: La edad '{edad}' no es un número válido. Se omitirá esta entrada.")  
            continue
        

        persona.append({
            "nombre": nombre,
            "edad": edad,
            "ciudad": ciudad
        })

en_bogota = [p for p in persona if p["ciudad"] == "Bogota"]     
        
if en_bogota:
    print(f"Personas en Bogotá: {en_bogota}")

else:    
    print("No se encontraron personas en Bogotá.")     