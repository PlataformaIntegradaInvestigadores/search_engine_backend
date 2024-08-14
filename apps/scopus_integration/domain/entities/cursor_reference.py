from django_neomodel import DjangoNode
from neomodel import StringProperty


class CursorReference(DjangoNode):
    next_url = StringProperty(unique_index=True)
    reference = StringProperty(unique_index=True)

    class Meta:
        app_label = 'scopus_integration'
