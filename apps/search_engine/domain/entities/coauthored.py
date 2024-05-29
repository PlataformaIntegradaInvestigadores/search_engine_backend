from neomodel import Relationship, IntegerProperty


class CoAuthored(Relationship):
    collab_strength = IntegerProperty()
