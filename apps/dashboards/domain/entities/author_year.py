from mongoengine import Document, fields


class AuthorYear(Document):
    scopus_id = fields.IntField()
    year = fields.IntField()
    total_articles = fields.IntField()
