from neomodel import IntegerProperty, StructuredRel, FloatProperty


class CoAuthored(StructuredRel):
    shared_pubs = IntegerProperty()
    collab_strength = FloatProperty()
