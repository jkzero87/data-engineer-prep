def calcular_resumen(montos):
    """Recibe lista de montos. Devuelve (total, cantidad)."""
    total = sum(montos)
    cantidad = len(montos)
    return total, cantidad


def formatear_resumen(total, cantidad, metadata):
    """Recibe datos crudos. Devuelve string listo para mostrar."""
    lineas = [f"Total: {total}", f"Transacciones: {cantidad}"]
    for clave, valor in metadata.items():
        lineas.append(f"{clave}: {valor}")
    return "\n".join(lineas)


def registrar(*args, **kwargs):
    """Orquesta el flujo: calcula, formatea, imprime."""
    total, cantidad = calcular_resumen(args)
    texto = formatear_resumen(total, cantidad, kwargs)
    print(texto)

registrar(150.50, 200.00, 75.25, usuario="juan", ciudad="Bogota", fecha="2026-05-04")
