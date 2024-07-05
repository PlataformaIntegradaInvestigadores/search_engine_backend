from mongoengine import Document, fields


class AuthorTopics(Document):
    scopus_id = fields.IntField()
    topic_name = fields.StringField()
    total_articles = fields.IntField()
