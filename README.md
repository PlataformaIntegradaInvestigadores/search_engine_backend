# CENTINELA - Search Engine

## Descripción

Este proyecto Django implementa un motor de búsqueda para la plataforma Centinela.

## Requisitos Previos

- Docker
- Docker Compose

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/PlataformaIntegradaInvestigadores/search_engine_backend.git
2. Accede al directorio del proyecto:
   ```bash
   cd search_engine_backend
3. Renombra el archivo `.env.example` a `.env`. Completa las variables de entorno con los valores correspondientes. 
   Las API keys de Elsevier necesarias para la extracción de datos son: `X_ELS_APIKEY` y `X_ELS_INSTTOKEN`.
   Para las bases de datos puedes utilizar tus propias credenciales. Con Docker Compose, la estructura de el
   archivo `.env` es la siguiente:
   ```bash
    # Django
    NEO4J_HOST=neo4j
    NEO4J_PASSWORD=your_password
    NEO4J_USERNAME=neo4j
    NEO4J_PORT=7687
    X_ELS_APIKEY=your_api_key
    X_ELS_INSTTOKEN=your_inst_token
    X_ELS_AUTHTOKEN=your_auth_token (opcional)

    DEBUG=True

    MONGO_DB_NAME=your_db_name
    MONGO_DB_USERNAME=your_username
    MONGO_DB_PASSWORD=your_password
    MONGO_DB_HOST=mongo
    MONGO_DB_PORT=27017
    # Para el admin de centinela 
    ADMIN_CENTINELA=your_admin_centinela
    PASSWORD_CENTINELA=your_password_centinela



4. Construye las imágenes y levanta los contenedores:
   ```bash
   docker compose up --build
   ```
5. (Opcional) Bootstrap con datos semilla:
   ```bash
   bash scripts/bootstrap.sh
   ```
   > El seed data **no está versionado** en este repo. Antes de correr el bootstrap,
   > coloca `seed_data/backup.json` (dump de Mongo) y `seed_data/centinela_db/` (datos de
   > Neo4j) obtenidos de la fuente institucional. Para pruebas básicas puedes levantar sin
   > seed y usar el catálogo vacío. Requiere `git-lfs` para los modelos (`resources/models/`).
6. Accede a la URL `http://localhost:8001/` para verificar que el servidor está corriendo correctamente.
7. Para detener los contenedores, ejecuta:
   ```bash
   docker compose down
   ```
8. Para acceder a la consola de Django y hacer las migraciones de Neomodel, ejecuta:
   ```bash
    docker exec -it <nombre_del_contenedor> bash
    python manage.py install_labels

## Notas
- Los servicios de Neo4j y MongoDB pueden tardar unos segundos en levantarse. Si el servidor de Django no se conecta
  a las bases de datos, intenta reiniciar los contenedores. O a su vez, puedes verificar el estado de los contenedores con el comando:
  ```bash
    docker ps
- Para acceder a la consola de Neo4j, puedes utilizar el siguiente comando:
  ```bash
  docker exec -it <nombre_del_contenedor> cypher-shell -u neo4j -p your_password
- Para acceder a la consola de MongoDB, puedes utilizar el siguiente comando:
  ```bash
    docker exec -it <nombre_del_contenedor> mongo -u your_username -p your_password --authenticationDatabase your_db_name
  ```
- Las credenciales de Centinela son las que se usarán para acceder al panel de administrador de Centinela. No existen credenciales por defecto.

## Arquitectura y Optimización de Búsqueda (Notas para Desarrolladores)
1. **Modelos TF-IDF vs. LLM:** El buscador por tópicos (`MostRelevantArticlesUseCase`) lee las palabras clave y su relevancia desde el archivo físico `resources/models/tf-idf/model-v10.0.pkl`. **Por favor no reemplazar ni sobreescribir este archivo por modelos de prueba locales acotados**, ya que esto limita el catálogo que ven los usuarios en producción a los IDs presentes en dicho archivo. El modelo oficial debe contener la totalidad del vocabulario y los artículos históricos de Neo4j.
2. **Rendimiento en Base de Datos:** En `ArticleRepository`, evitar el uso de ordenamientos cronológicos (`ORDER BY publication_date DESC`) cuando se buscan artículos por relevancia matemática (TF-IDF/Embeddings), de lo contrario Neo4j truncará los resultados relegando la literatura fundamental histórica en favor de artículos recientes. Así mismo, evitar consultas N+1 en bucles sobre `find_articles_by_ids`.
3. **Optimización de Memoria (Gunicorn):** Las librerías de NLP (`spacy`, `KeyBERT`) se encuentran cacheadas bajo el patrón Singleton en `tfidf.py`. En producción, la imagen de Docker precarga el modelo durante el build y utiliza preloading en Gunicorn para compartir memoria entre workers.