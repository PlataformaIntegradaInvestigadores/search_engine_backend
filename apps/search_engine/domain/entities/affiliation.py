from neomodel import StructuredNode, StringProperty


class Affiliation(StructuredNode):
    scopus_id = StringProperty(unique_index=True)
    name = StringProperty()
    city = StringProperty()
    country = StringProperty()