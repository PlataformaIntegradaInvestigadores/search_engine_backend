from mongoengine import Document, fields


class Affiliation(Document):
    scopus_id = fields.IntField()
    name = fields.StringField()
    total_articles = fields.IntField()
