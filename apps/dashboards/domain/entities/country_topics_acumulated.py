from mongoengine import Document, fields


class CountryTopicsAcumulated(Document):
    topic_name = fields.StringField()
    year = fields.IntField()
    total_articles = fields.IntField()
