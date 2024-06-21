from django_neomodel import DjangoNode
from neomodel import StructuredNode, StringProperty, RelationshipTo, Relationship, IntegerProperty, UniqueIdProperty

from apps.search_engine.domain.entities.affiliation import Affiliation
from apps.search_engine.domain.entities.topic import Topic


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

    @classmethod
    def from_dict(cls, author_data: dict) -> 'Author':
        scopus_id = author_data.get('authid', '')

        if not scopus_id:
            raise ValueError("Invalid scopus_id")

        try:
            author = cls.nodes.get(scopus_id=scopus_id)
        except cls.DoesNotExist:
            author_data = {
                'first_name': author_data.get('author-profile', {}).get('preferred-name', {}).get('given-name', ''),
                'last_name': author_data.get('author-profile', {}).get('preferred-name', {}).get('surname', ''),
                'auth_name': author_data.get('author-profile', {}).get('preferred-name', {}).get('indexed-name', ''),
                'initials': author_data.get('author-profile', {}).get('preferred-name', {}).get('initials', ''),
                'scopus_id': scopus_id,
            }

            author = cls(**author_data).save()

            keywords = author_data.get('subject-areas', {}).get("subject-area", [])

            for keyword in keywords:
                keyword_instance = Topic.from_json(keyword.get('$', ''))
                if not author.topics.is_connected(keyword_instance):
                    author.topics.connect(keyword_instance)

            affiliations = author_data.get('author-profile', {}).get('affiliation-history', {}).get('affiliation', [])
            for affiliation_data in affiliations:
                affiliation_instance = Affiliation.from_dict(affiliation_data)
                if not author.affiliations.is_connected(affiliation_instance):
                    author.affiliations.connect(affiliation_instance)

            author = cls(**author_data).save()

        return author
