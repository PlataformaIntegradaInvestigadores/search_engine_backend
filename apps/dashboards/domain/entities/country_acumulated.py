from mongoengine import Document, fields


class CountryAcumulated(Document):
    year = fields.IntField()
    total_authors = fields.IntField()
    total_articles = fields.IntField()
    total_affiliations = fields.IntField()
    total_topics = fields.IntField()
