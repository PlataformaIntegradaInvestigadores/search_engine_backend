from neomodel import StructuredNode, StringProperty, RelationshipTo, Relationship, IntegerProperty


class Article(StructuredNode):
    title = StringProperty()
    abstract = StringProperty()
    doi = StringProperty(unique_index=True)
    publication_date = StringProperty()
    author_count = IntegerProperty()
    affiliation_count = IntegerProperty()
    corpus = StringProperty()
    authors = RelationshipTo('Author', 'WROTE')
    affiliations = RelationshipTo('Affiliation', 'BELONGS_TO')
    topics = RelationshipTo('Topic', 'USES')

    def __str__(self):
        return self.title
