from mongoengine import Document, fields


class AuthorTopicsYear(Document):
    scopus_id = fields.IntField()
    topic_name = fields.StringField()
    year = fields.IntField()
    total_articles = fields.IntField()
