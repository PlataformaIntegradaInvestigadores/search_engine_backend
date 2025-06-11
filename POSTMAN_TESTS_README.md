# 🧪 Text Processing API - Test Collection

Esta colección de Postman contiene casos de prueba completos para el servicio de vectorización de texto.

## 📁 Archivos incluidos

- `text_processing_api_tests.postman_collection.json` - Colección principal con todos los casos de prueba
- `text_processing_environment.postman_environment.json` - Entorno de desarrollo con variables configuradas

## 🚀 Cómo usar

### 1. Importar en Postman

1. Abrir Postman
2. Click en **Import**
3. Seleccionar ambos archivos JSON
4. Los archivos se importarán automáticamente

### 2. Configurar el entorno

1. Seleccionar el entorno **"Text Processing - Development"**
2. Verificar que las variables estén configuradas:
   - `base_url`: `http://localhost:8001`
   - `api_prefix`: `/api-se/v1`

### 3. Levantar el servidor

Asegúrate de que tu servidor esté corriendo:
```bash
docker compose up
```

## 🧪 Casos de prueba incluidos

### ✅ Casos exitosos

1. **Health Check** - Verificar que el servicio esté funcionando
2. **Vectorize Spanish Text** - Texto en español con traducción automática
3. **Vectorize English Text** - Texto en inglés sin traducción
4. **Vectorize Without Translation** - Procesar texto sin traducir
5. **Vectorize Without Cleaning** - Procesar texto sin limpiar caracteres especiales
6. **Vectorize Long Text** - Texto largo para probar rendimiento
7. **Vectorize Minimal Options** - Solo con opciones básicas

### ❌ Casos de error

8. **Empty Text Error** - Probar validación cuando falta el campo text
9. **Empty String Error** - Probar validación con string vacío

## 📊 Estructura de respuesta esperada

### Respuesta exitosa:
```json
{
    "vector": [0.1, 0.2, -0.3, ...],
    "dimension": 768,
    "original_language": "es",
    "was_translated": true,
    "processed_text": "processed text here",
    "processing_time": {
        "translation_time": 0.15,
        "embedding_time": 0.25,
        "total_time": 0.40
    }
}
```

### Respuesta de error:
```json
{
    "error": "Text field is required"
}
```

## 🔧 Configuración de variables

Puedes modificar las variables del entorno para probar contra diferentes servidores:

- **Desarrollo local**: `http://localhost:8001`
- **Docker**: `http://localhost:8001`
- **Producción**: Cambiar según tu configuración

## 📝 Tests automáticos incluidos

Cada request incluye tests automáticos que verifican:

- ✅ Códigos de estado HTTP correctos
- ✅ Estructura de respuesta válida
- ✅ Tipos de datos correctos
- ✅ Validaciones de negocio
- ✅ Tiempos de procesamiento
- ✅ Detección de idioma
- ✅ Comportamiento de traducción

## 🏃‍♂️ Ejecutar todos los tests

1. Seleccionar la colección **"Text Processing API - Test Collection"**
2. Click en **Run**
3. Configurar las opciones de ejecución
4. Click en **Run Text Processing API**

Los tests se ejecutarán secuencialmente y mostrarán un reporte completo.

## 🐛 Troubleshooting

### Error de conexión
- Verificar que Docker esté corriendo
- Verificar que el puerto 8001 esté disponible
- Revisar la URL base en las variables de entorno

### Tests fallando
- Verificar que los modelos estén descargados correctamente
- Revisar logs del contenedor: `docker logs <container_name>`
- Verificar la configuración de spaCy y otros modelos

## 📋 Endpoints disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api-se/v1/text-processing/health/` | Health check del servicio |
| POST | `/api-se/v1/text-processing/vectorize/` | Vectorizar texto |

## 🔗 Documentación adicional

Para más información sobre la API, consultar:
- Swagger UI: `http://localhost:8001/api-se/schema/swagger-ui/`
- ReDoc: `http://localhost:8001/api-se/schema/redoc/`
