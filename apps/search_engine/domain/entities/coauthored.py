from neomodel import IntegerProperty, StructuredRel, FloatProperty


class CoAuthored(StructuredRel):
    collab_strength = FloatProperty()