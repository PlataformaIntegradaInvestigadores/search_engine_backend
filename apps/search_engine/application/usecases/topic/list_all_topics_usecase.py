from apps.search_engine.application.services.topic_service import TopicService


class ListAllTopicsUseCase:
    def __init__(self, topic_service: TopicService):
        self.topic_service = topic_service

    def execute(self):
        return self.topic_service.get_all()
