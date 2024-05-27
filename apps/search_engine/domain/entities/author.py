from neomodel import StructuredNode, StringProperty, RelationshipTo, Relationship


class Author(StructuredNode):
    scopus_id = StringProperty(unique_index=True)
    first_name = StringProperty()
    last_name = StringProperty()
    auth_name = StringProperty()
    initials = StringProperty()
    affiliations = RelationshipTo('Affiliation', 'AFFILIATED_WITH')
    articles = RelationshipTo('Article', 'WROTE')
    co_authors = Relationship('Author', 'CO_AUTHORED')
