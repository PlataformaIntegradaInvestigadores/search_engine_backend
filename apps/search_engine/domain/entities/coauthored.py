from neomodel import IntegerProperty, StructuredRel, FloatProperty


class CoAuthored(StructuredRel):
    shared_pubs = IntegerProperty(db_property="article_count")
    collab_strength = FloatProperty()
