# Servidor API de Documentos Fiscales

Este servidor FastAPI proporciona un endpoint para consultar documentos fiscales filtrados y calcular la suma total.

## Instalación

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución

Para iniciar el servidor, ejecuta:
```bash
python server.py
```

O usando uvicorn directamente:
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

El servidor estará disponible en `http://localhost:8000`

## Endpoints

### GET `/`
Endpoint raíz que muestra información sobre la API.

### GET `/health`
Health check del servidor.

### GET `/api/documentos-fiscales`
Obtiene los documentos fiscales filtrados por `group_info='Emitido'` y calcula la suma total.

**Parámetros de consulta (opcionales):**
- `identification`: Identificación del usuario (por defecto: "1000747836")
- `password`: Contraseña del usuario (por defecto: "Admin2024!")

**Ejemplo de uso:**
```bash
# Usando credenciales por defecto
curl http://localhost:8000/api/documentos-fiscales

# Especificando credenciales
curl "http://localhost:8000/api/documentos-fiscales?identification=1000747836&password=Admin2024!"
```

**Respuesta:**
```json
{
  "total_registros": 10,
  "suma_total": 150000.50,
  "registros": [...],
  "estadisticas": {
    "minimo": 1000.00,
    "maximo": 50000.00,
    "promedio": 15000.05
  }
}
```

## Documentación Interactiva

Una vez que el servidor esté corriendo, puedes acceder a:
- Documentación Swagger: `http://localhost:8000/docs`
- Documentación ReDoc: `http://localhost:8000/redoc`

## Notas

- El servidor se conecta a la API local en `http://localhost:8080/api`
- Los datos se filtran por `group_info == 'Emitido'`
- La suma se calcula sobre la columna `total`

