from mongoengine import Document, fields


class Author(Document):
    scopus_id = fields.IntField()
    total_articles = fields.IntField()
