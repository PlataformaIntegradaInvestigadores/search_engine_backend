from django_neomodel import DjangoNode
from neomodel import StringProperty, RelationshipTo, Relationship, IntegerProperty, UniqueIdProperty
from apps.search_engine.domain.entities.author import Author
from apps.search_engine.domain.entities.affiliation import Affiliation
from apps.search_engine.domain.entities.topic import Topic


class Article(DjangoNode):
    title = StringProperty()
    abstract = StringProperty()
    doi = UniqueIdProperty()
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
