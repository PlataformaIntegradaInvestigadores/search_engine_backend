from django_neomodel import DjangoNode
from neomodel import StructuredNode, StringProperty


class Topic(DjangoNode):
    name = StringProperty(unique_index=True)


    class Meta:
        app_label = 'search_engine'
