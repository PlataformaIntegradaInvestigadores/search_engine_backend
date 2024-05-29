from django_neomodel import DjangoNode
from neomodel import StringProperty, UniqueIdProperty


class Affiliation(DjangoNode):
    scopus_id = UniqueIdProperty()
    name = StringProperty()
    city = StringProperty()
    country = StringProperty()

    class Meta:
        app_label = 'search_engine'
