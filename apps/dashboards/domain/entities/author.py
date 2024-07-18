from mongoengine import Document, fields


class Author(Document):
    scopus_id = fields.IntField(required=True, unique=True)
    total_articles = fields.IntField()
