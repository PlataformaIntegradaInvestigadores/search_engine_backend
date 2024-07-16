from mongoengine import Document, fields


class AffiliationTopics(Document):
    scopus_id = fields.IntField()
    name = fields.StringField()
    topic_name = fields.StringField()
    total_articles = fields.IntField()
