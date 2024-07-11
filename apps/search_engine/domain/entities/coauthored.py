from neomodel import IntegerProperty, StructuredRel


class CoAuthored(StructuredRel):
    collab_strength = IntegerProperty()
    shared_pubs = IntegerProperty()
