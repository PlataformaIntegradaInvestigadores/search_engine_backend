from mongoengine import Document, fields


class AffiliationTopicsYear(Document):
    scopus_id = fields.IntField()
    name = fields.StringField()
    topic_name = fields.StringField()
    year = fields.IntField()
    total_articles = fields.IntField()
