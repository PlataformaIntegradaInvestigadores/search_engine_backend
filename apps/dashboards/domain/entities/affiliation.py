from mongoengine import Document, fields


class Affiliation(Document):
    scopus_id = fields.IntField(required=True, unique=True)
    name = fields.StringField()
    total_articles = fields.IntField()
