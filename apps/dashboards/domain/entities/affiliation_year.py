from mongoengine import Document, fields


class AffiliationYear(Document):
    scopus_id = fields.IntField()
    name = fields.StringField()
    year = fields.IntField()
    total_articles = fields.IntField()
