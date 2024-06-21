from django_neomodel import DjangoNode
from neomodel import StringProperty, RelationshipTo, Relationship, IntegerProperty, UniqueIdProperty, db
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
    def from_json(cls, article_data) -> 'Article':

        scopus_id = cls.validate_scopus_id(article_data.get('dc:identifier', ''))
        if scopus_id is None:
            raise ValueError("Invalid scopus_id")

        try:
            article = cls.nodes.get(scopus_id=scopus_id)
        except cls.DoesNotExist:
            article_data = {
                'title': article_data.get('dc:title', ''),
                'doi': article_data.get('prism:doi', '') if article_data.get('prism:doi', '') else None,
                'publication_date': article_data.get('prism:coverDate', ''),
                'abstract': article_data.get('dc:description', ''),
                'author_count': len(article_data.get('author', [])),
                'affiliation_count': len(article_data.get('affiliation', [])),
                'scopus_id': scopus_id,
            }
            article = cls(**article_data).save()

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
