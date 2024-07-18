from mongoengine import Document, fields


class CountryTopics(Document):
    topic_name = fields.StringField(required=True, unique=True)
    total_articles = fields.IntField()
