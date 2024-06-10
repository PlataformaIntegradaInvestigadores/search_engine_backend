from apps.search_engine.domain.entities.topic import Topic


class TopicService:
    def get_all_topics(self):
        return Topic.nodes.all()
