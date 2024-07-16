from mongoengine import Document, fields


class ProvinceTopicsAcumulated(Document):
    province_name = fields.StringField()
    topic_name = fields.StringField()
    year = fields.IntField()
    total_articles = fields.IntField()
