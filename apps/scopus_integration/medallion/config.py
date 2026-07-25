import os


class MedallionConfig:
    mongo_uri = os.getenv("SCOPUS_MEDALLION_MONGO_URI")
    mongo_db_name = os.getenv("SCOPUS_MEDALLION_DB_NAME", "ETL_Centinela_refactor")

    raw_articles_collection = os.getenv("SCOPUS_RAW_ARTICLES_COLLECTION", "raw_data")
    raw_authors_collection = os.getenv("SCOPUS_RAW_AUTHORS_COLLECTION", "raw_authors")
    raw_affiliations_collection = os.getenv("SCOPUS_RAW_AFFILIATIONS_COLLECTION", "raw_affiliations")
    cursors_collection = os.getenv("SCOPUS_CURSORS_COLLECTION", "cursors")

    silver_articles_collection = os.getenv("SCOPUS_SILVER_ARTICLES_COLLECTION", "silver_articles")
    silver_authors_collection = os.getenv("SCOPUS_SILVER_AUTHORS_COLLECTION", "silver_authors")
    silver_affiliations_collection = os.getenv("SCOPUS_SILVER_AFFILIATIONS_COLLECTION", "silver_affiliations")

    gold_ml_features_collection = os.getenv("SCOPUS_GOLD_ML_FEATURES_COLLECTION", "gold_ml_features")
    gold_graph_entities_collection = os.getenv("SCOPUS_GOLD_GRAPH_ENTITIES_COLLECTION", "gold_graph_entities")
    gold_dashboard_metrics_collection = os.getenv("SCOPUS_GOLD_DASHBOARD_METRICS_COLLECTION", "gold_dashboard_metrics")

    default_query = os.getenv("SCOPUS_DEFAULT_QUERY", "AFFIL(AFFILCOUNTRY(ECUADOR))")
    payload_version = os.getenv("SCOPUS_PAYLOAD_VERSION", "2026-06-24")

    @classmethod
    def resolve_mongo_uri(cls) -> str:
        if cls.mongo_uri:
            return cls.mongo_uri

        username = os.getenv("MONGO_DB_USERNAME", "")
        password = os.getenv("MONGO_DB_PASSWORD", "")
        host = os.getenv("MONGO_DB_HOST", "mongo")
        port = os.getenv("MONGO_DB_PORT", "27017")
        auth_source = os.getenv("MONGO_AUTH_SOURCE", "admin")
        if username and password:
            return f"mongodb://{username}:{password}@{host}:{port}/{cls.mongo_db_name}?authSource={auth_source}"
        return f"mongodb://{host}:{port}/{cls.mongo_db_name}"
