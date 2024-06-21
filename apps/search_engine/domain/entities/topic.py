from django_neomodel import DjangoNode
from neomodel import StructuredNode, StringProperty, RelationshipFrom


class Topic(DjangoNode):
    name = StringProperty(unique_index=True)

    class Meta:
        app_label = 'search_engine'

    @classmethod
    def from_json(cls, topic):
        try:
            topic_instance = cls.nodes.get(name=topic)
        except cls.DoesNotExist:
            topic_instance = cls(name=topic).save()
        return topic_instance

