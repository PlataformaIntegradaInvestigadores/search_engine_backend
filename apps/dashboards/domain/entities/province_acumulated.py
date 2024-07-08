from mongoengine import Document, fields


class ProvinceAcumulated(Document):
    province_name = fields.StringField()
    year = fields.IntField()
    total_articles = fields.IntField()
