from django_neomodel import DjangoNode
from neomodel import StructuredNode, StringProperty


class Topic(DjangoNode):
    name = StringProperty(unique_index=True)

    class Meta:
        app_label = 'search_engine'

    @classmethod
    def from_list(cls, topic):
        try:
            topic_instance = cls.nodes.get(name=topic)
        except cls.DoesNotExist:
            topic_instance = cls(name=topic).save()
        return topic_instance

    @staticmethod
    def from_list_(topic):
        try:
            topic_instance = {
                'name': topic
            }
            return topic_instance
        except Exception as e:
            raise Exception('Error creating topic instance: ', e)
