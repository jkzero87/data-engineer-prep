"""
session4.py
Análisis básico de logs de servidor web.
Filtra errores, genera alertas, calcula estadísticas y produce un reporte.
"""
# --- Datos de entrada ---
logs = [
    {"timestamp": "2026-05-05 08:15:32", "endpoint": "/api/users",    "status": 200, "duration_ms": 145, "user_id": 1042},
    {"timestamp": "2026-05-05 08:16:01", "endpoint": "/api/login",    "status": 401, "duration_ms": 89,  "user_id": 2891},
    {"timestamp": "2026-05-05 08:16:45", "endpoint": "/api/orders",   "status": 500, "duration_ms": 2340, "user_id": 1042},
    {"timestamp": "2026-05-05 08:17:12", "endpoint": "/api/products", "status": 200, "duration_ms": 67,  "user_id": 3401},
    {"timestamp": "2026-05-05 08:17:55", "endpoint": "/api/orders",   "status": 503, "duration_ms": 5102, "user_id": 2891},
    {"timestamp": "2026-05-05 08:18:23", "endpoint": "/api/users",    "status": 404, "duration_ms": 23,  "user_id": 7711},
    {"timestamp": "2026-05-05 08:18:59", "endpoint": "/api/checkout", "status": 200, "duration_ms": 312, "user_id": 1042},
    {"timestamp": "2026-05-05 08:19:30", "endpoint": "/api/login",    "status": 500, "duration_ms": 1890, "user_id": 4523},
]

def es_error(log):
   return log["status"] >= 400

def filtrar_errores(logs):
   errores = filter(es_error,logs)
   return list(errores) 

def crear_alerta(log):
   return f"[ALERTA] {log['timestamp']} | status {log['status']} | {log['endpoint']} | {log['duration_ms']}ms" 

def generar_alertas(logs_error):
   lista_alertas = map(crear_alerta,logs_error) 
   return list(lista_alertas)

def calcular_estadisticas(logs_error):
   total = len(logs_error)
   promedio = sum(log["duration_ms"] for log in logs_error) / total
   log_mas_lento = max(logs_error, key=lambda log:log["duration_ms"])
   endpoint_mas_lento = log_mas_lento["endpoint"]

   return {
        "total_errores": total,
        "duracion_promedio_ms": promedio,
        "endpoint_mas_lento": endpoint_mas_lento
    }

def generar_reporte(alertas,stats):
   bloque_alertas = "\n".join(alertas)

   reporte = f"""=== REPORTE DE ANALISIS DE LOGS ===

ALERTAS:
{bloque_alertas}

ESTADISTICAS:
Total de errores: {stats["total_errores"]}
Duracion promedio: {stats["duracion_promedio_ms"]:.2f}
Endpoint mas lento: {stats["endpoint_mas_lento"]}
""" 
   return reporte

def analizar_logs(logs):
    errores = filtrar_errores(logs)
    alertas = generar_alertas(errores)
    stats = calcular_estadisticas(errores)
    reporte = generar_reporte(alertas, stats)
    return reporte


def guardar_reporte(reporte, ruta="reporte.txt"):
    with open(ruta, "w") as archivo:
        archivo.write(reporte)

reporte = analizar_logs(logs)
print(reporte)
guardar_reporte(reporte)