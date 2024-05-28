from neomodel import StructuredNode, StringProperty


class Topic(StructuredNode):
    name = StringProperty(unique_index=True)