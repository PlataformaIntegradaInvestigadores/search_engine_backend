from neomodel import StructuredNode, StringProperty, IntegerProperty


class Author(StructuredNode):
    name = StringProperty(unique_index=True)
    email = StringProperty(unique_index=True)
    affiliation = StringProperty()
    scopus_id = StringProperty(unique_index=True)
    scopus_h_index = IntegerProperty()
    scopus_citations = IntegerProperty()
    scopus_documents = IntegerProperty()
    scopus_co_authors = IntegerProperty()
    scopus_cited_by = IntegerProperty()
    scopus_cited_by_count = IntegerProperty()