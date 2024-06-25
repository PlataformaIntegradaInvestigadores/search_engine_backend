import time

from django_neomodel import DjangoNode
from neomodel import StringProperty, RelationshipTo, Relationship, IntegerProperty, UniqueIdProperty, db

from apps.scopus_integration.application.usecases.author_retrieval_usecase import AuthorRetrieval
from apps.search_engine.domain.entities.author import Author
from apps.search_engine.domain.entities.affiliation import Affiliation
from apps.search_engine.domain.entities.topic import Topic


class Article(DjangoNode):
    scopus_id = IntegerProperty(unique_index=True)
    title = StringProperty()
    abstract = StringProperty()
    doi = StringProperty()
    publication_date = StringProperty()
    author_count = IntegerProperty()
    affiliation_count = IntegerProperty()
    corpus = StringProperty()
    affiliations = RelationshipTo(Affiliation, 'BELONGS_TO')
    topics = RelationshipTo(Topic, 'USES')

    def __str__(self):
        return self.title

    class Meta:
        app_label = 'search_engine'

    @classmethod
    @db.transaction
    def from_json(cls, article_data, client) -> 'Article':
        scopus_id = cls.validate_scopus_id(article_data.get('dc:identifier', ''))
        if scopus_id is None:
            raise ValueError("Invalid scopus_id on article creation")

        try:
            article = cls.nodes.get(scopus_id=scopus_id)
            return article  # Article already exists, return it without further processing
        except cls.DoesNotExist:
            article_data_processed = {
                'title': article_data.get('dc:title', ''),
                'doi': article_data.get('prism:doi', '') if article_data.get('prism:doi', '') else None,
                'publication_date': article_data.get('prism:coverDate', ''),
                'abstract': article_data.get('dc:description', ''),
                'author_count': len(article_data.get('author', [])),
                'affiliation_count': len(article_data.get('affiliation', [])),
                'scopus_id': scopus_id,
            }
            article = cls(**article_data_processed).save()

            # Process topics (keywords)
            keywords = article_data.get('authkeywords', '').split(' | ')
            for keyword in keywords:
                keyword_instance = Topic.from_json(keyword)
                if not article.topics.is_connected(keyword_instance):
                    article.topics.connect(keyword_instance)

            # Process affiliations
            affiliations = article_data.get('affiliation', [])
            for affiliation_data in affiliations:
                affiliation_instance = Affiliation.from_dict(affiliation_data)
                if not article.affiliations.is_connected(affiliation_instance):
                    article.affiliations.connect(affiliation_instance)

            print("Iniciando procesamiento de autores")
            # Process authors
            authors = article_data.get('author', [])

            # Crear instancias de autores y conectar artículos en lotes
            author_instances = [Author.from_dict(author) for author in authors]
            for author_instance in author_instances:
                if not author_instance.articles.is_connected(article):
                    author_instance.articles.connect(article)
            time_0 = time.time()
            # Build CoAuthored relationships
            # Utilizamos un solo bucle y evitamos redundancias
            for i, author_instance in enumerate(author_instances):
                for j in range(i + 1, len(author_instances)):  # Evita comparar un autor consigo mismo y duplicados
                    co_author_instance = author_instances[j]

                    if author_instance.co_authors.is_connected(co_author_instance):
                        coauth_relationship = author_instance.co_authors.relationship(co_author_instance)
                        print(
                            "----------------------------------------------------------------------------------------------------------------------------------------------------------------")
                        print(f"Existing relationship found: {coauth_relationship.collab_strength}")
                        coauth_relationship.collab_strength += 1
                        coauth_relationship.save()
                        print(f"Updated relationship strength: {coauth_relationship.collab_strength}")
                    else:
                        coauth_relationship = author_instance.co_authors.connect(co_author_instance,
                                                                                 {'collab_strength': 1})

            author_retrievals = [AuthorRetrieval(author_id=author_instance.scopus_id) for author_instance in
                                 author_instances]
            print(f"Tiempo de creación de instancias de recuperación de autores {len(author_retrievals)}: ",
                  time.time() - time_0)

            time_1 = time.time()
            for retrieval in author_retrievals:
                retrieval.execute(client)
            print("Tiempo de ejecución de recuperación de autores: ", time.time() - time_1)
            # Actualizar en lotes las instancias de autores
            for author_instance, retrieval in zip(author_instances, author_retrievals):
                retrieval_info = retrieval.result[0]
                author_instance.update_from_json(author_data=retrieval_info)

        return article

    @staticmethod
    def validate_scopus_id(scopus_id) -> int or None:
        if scopus_id:
            try:
                scopus_id = int(scopus_id.split(":")[1])
                return scopus_id
            except ValueError:
                return None
        else:
            return None
