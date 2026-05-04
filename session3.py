transacciones = [
    {"id": 1, "usuario": "juan", "monto": "150.50", "ciudad": "Bogota"},
    {"id": 2, "usuario": "ana", "monto": "abc", "ciudad": "Medellin"},
    {"id": 3, "usuario": "juan", "monto": "200.00", "ciudad": "Bogota"},
    {"id": 4, "usuario": "luis", "monto": "75.25", "ciudad": "Cali"},
    {"id": 5, "usuario": "ana", "monto": "300.00", "ciudad": "Medellin"},
    {"id": 6, "usuario": "juan", "monto": "", "ciudad": "Bogota"},
]
# 1. Definir el acumulador
acumulador = 0
# 2. Recorrer cada transacción
for transaccion in transacciones:
 
    # 3. Intentar convertir el monto
    try:
        monto = float(transaccion["monto"])
    # 4. Si falla, saltar
    except ValueError:
        continue
    
    # 5. Si la ciudad es Bogotá, sumar al total
    if transaccion["ciudad"] == "Bogota":
        acumulador += monto    
    
# 6. Imprimir el total
print (f"Total gastado en bogota: {acumulador}")