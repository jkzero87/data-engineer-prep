transacciones = [
    {"id": 1, "usuario": "juan", "monto": "150.50", "ciudad": "Bogota"},
    {"id": 2, "usuario": "ana", "monto": "abc", "ciudad": "Medellin"},
    {"id": 3, "usuario": "juan", "monto": "200.00", "ciudad": "Bogota"},
    {"id": 4, "usuario": "luis", "monto": "75.25", "ciudad": "Cali"},
    {"id": 5, "usuario": "ana", "monto": "300.00", "ciudad": "Medellin"},
    {"id": 6, "usuario": "juan", "monto": "", "ciudad": "Bogota"},
]

acumulador = {}
    
for transaccion in transacciones:
    usuario = transaccion["usuario"]

    try:
        monto = float(transaccion["monto"])
    
    except ValueError:
        continue

    if usuario not in acumulador:
        acumulador[usuario] = 0
    acumulador[usuario] += monto

print (acumulador)