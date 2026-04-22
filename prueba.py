with open('datos.csv', 'r') as archivo:
    next(archivo)
    for linea in archivo:
        nombre, edad, _ = linea.strip().split(',')
        if int(edad) > 28:
            print(nombre)
