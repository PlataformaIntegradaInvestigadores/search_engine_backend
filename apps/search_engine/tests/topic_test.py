from neomodel import DoesNotExist
from rest_framework.test import APITestCase
from apps.search_engine.domain.entities.topic import Topic


class TopicTestCase(APITestCase):
    def setUp(self):
        self.topic = Topic.from_json(topic="Test Topic2")

    def test_topic_name(self):
        self.assertEqual(self.topic.name, 'Test Topic2')

    def test_search_topic(self):
        topic = Topic.nodes.get(name="Test Topic2")
        self.assertEqual(topic, self.topic)

    def test_delete_topic(self):
        topic = Topic.nodes.get(name="Test Topic2")
        print("Before delete:", topic.name)
        topic.delete()
        with self.assertRaises(DoesNotExist):
            Topic.nodes.get(name="Test Topic2")

        try:
            Topic.nodes.get(name="Test Topic2")
        except DoesNotExist:
            print("Topic successfully deleted.")
        else:
            print("Topic not deleted.")

    def test_after_delete_topic(self):
        with self.assertRaises(DoesNotExist):
            Topic.nodes.get(name="Test Topic2")
