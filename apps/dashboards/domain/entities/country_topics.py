from mongoengine import Document, fields


class CountryTopics(Document):
    topic_name = fields.StringField()
    total_articles = fields.IntField()
