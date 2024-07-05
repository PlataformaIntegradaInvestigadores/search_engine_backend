from mongoengine import Document, fields


class Author(Document):
    scopus_id = fields.IntField(max_length=255, unique=True)
    total_articles = fields.IntField()

