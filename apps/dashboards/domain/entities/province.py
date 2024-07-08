from mongoengine import Document, fields


class Province(Document):
    province_name = fields.StringField()
    total_articles = fields.IntField()
