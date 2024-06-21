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
    def from_json(cls, json) -> 'Article':

        scopus_id = cls.validate_scopus_id(json.get('dc:identifier', ''))
        if scopus_id is None:
            raise ValueError("Invalid scopus_id")

        try:
            article = cls.nodes.get(scopus_id=scopus_id)
        except cls.DoesNotExist:
            article_data = {
                'title': json.get('dc:title', ''),
                'doi': json.get('prism:doi', '') if json.get('prism:doi', '') else None,
                'publication_date': json.get('prism:coverDate', ''),
                'abstract': json.get('dc:description', ''),
                'author_count': len(json.get('author', [])),
                'affiliation_count': len(json.get('affiliation', [])),
                'scopus_id': scopus_id,
            }
            article = cls(**article_data).save()

        # Process topics (keywords)
        keywords = json.get('authkeywords', '').split(' | ')
        for keyword in keywords:
            keyword_instance = Topic.from_list(keyword)
            if not article.topics.is_connected(keyword_instance):
                article.topics.connect(keyword_instance)

        # Process affiliations
        affiliations = json.get('affiliation', [])
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
