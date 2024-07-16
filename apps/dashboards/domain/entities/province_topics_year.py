from mongoengine import Document, fields


class ProvinceTopicsYear(Document):
    province_name = fields.StringField()
    topic_name = fields.StringField()
    year = fields.IntField()
    total_articles = fields.IntField()
