from django_neomodel import DjangoNode
from neomodel import StringProperty, UniqueIdProperty


class Affiliation(DjangoNode):
    scopus_id = UniqueIdProperty()
    name = StringProperty()
    city = StringProperty()
    country = StringProperty()

    class Meta:
        app_label = 'search_engine'

    @classmethod
    def from_dict(cls, affiliation_data):
        scopus_id = affiliation_data.get('afid')
        name = affiliation_data.get('affilname')
        city = affiliation_data.get('affiliation-city')
        country = affiliation_data.get('affiliation-country')

        try:
            affiliation_instance = cls.nodes.get(scopus_id=scopus_id)
        except cls.DoesNotExist:
            affiliation_instance = cls(
                scopus_id=scopus_id,
                name=name,
                city=city,
                country=country
            ).save()
        return affiliation_instance
