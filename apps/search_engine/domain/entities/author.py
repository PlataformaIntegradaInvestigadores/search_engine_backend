from django_neomodel import DjangoNode
from neomodel import StructuredNode, StringProperty, RelationshipTo, Relationship, IntegerProperty, UniqueIdProperty


class Author(DjangoNode):
    scopus_id = UniqueIdProperty()
    first_name = StringProperty()
    last_name = StringProperty()
    auth_name = StringProperty()
    initials = StringProperty()
    affiliations = RelationshipTo('apps.search_engine.domain.entities.affiliation.Affiliation', 'AFFILIATED_WITH')
    articles = RelationshipTo('apps.search_engine.domain.entities.article.Article', 'WROTE')
    co_authors = Relationship('Author', 'CO_AUTHORED')
    topics = RelationshipTo('apps.search_engine.domain.entities.topic.Topic', 'EXPERT_IN')

    def __str__(self):
        return f'{self.first_name}  {self.last_name}'

    class Meta:
        app_label = 'search_engine'
