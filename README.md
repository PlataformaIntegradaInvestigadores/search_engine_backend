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
3. Renombra el archivo `.env.template` a `.env`. Completa las variables de entorno con los valores correspondientes. 
   Las API keys de Elsevier necesarias para la extracción de datos son: `ELSEVIER_API_KEY` y `ELSEVIER_INST_KEY`.
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
   docker-compose up --build
5. Accede a la URL `http://localhost:8000/` para verificar que el servidor está corriendo correctamente.
6. Para detener los contenedores, ejecuta:
   ```bash
   docker-compose down
7. Para acceder a la consola de Django y hacer las migraciones de Neomodel, ejecuta:
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
- Las credenciales de Centinela son las que se usarán para acceder al panel de administrador de Centinela. No existen credenciales por defecto.