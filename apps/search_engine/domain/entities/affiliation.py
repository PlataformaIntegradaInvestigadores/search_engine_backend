import time

from django_neomodel import DjangoNode
from neomodel import StringProperty, UniqueIdProperty


class Affiliation(DjangoNode):
    scopus_id = UniqueIdProperty()
    name = StringProperty(unique_index=True)
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
            affiliation_instance = cls.nodes.get(name=name)
        except cls.DoesNotExist:
            affiliation_instance = cls(
                scopus_id=scopus_id,
                name=name,
                city=city,
                country=country
            ).save()
        return affiliation_instance

    @classmethod
    def retrieve_from_json(cls, affiliation_data):
        global name, country, city
        scopus_id = affiliation_data.get('@affiliation-id')
        extra_information = affiliation_data.get('ip-doc')
        address = extra_information.get('address', {})
        parent_name_data = extra_information.get('parent-preferred-name', None)
        preferred_name_data = extra_information.get('preferred-name', None)
        if parent_name_data:
            if not isinstance(parent_name_data, dict):
                return None
            name = parent_name_data.get('$', None)
        if not parent_name_data and preferred_name_data:
            name = preferred_name_data.get('$', None)

        if not name:
            return None

        if isinstance(address, dict):
            city = address.get('city')
            country = address.get('country')

        try:
            affiliation_instance = cls.nodes.get(name=name)
        except cls.DoesNotExist:
            affiliation_instance = cls(
                scopus_id=scopus_id,
                name=name,
                city=city,
                country=country
            ).save()
        return affiliation_instance
    # @classmethod
    # def from_retrieve_json(cls, affiliation_data):
    #     try:
    #         time_0 = time.time()
    #         scopus_id = affiliation_data.get('@affiliation-id')
    #         extra_information = affiliation_data.get('ip-doc')
    #         parent_name_data = extra_information.get('parent-preferred-name', None)
    #         preferred_name_data = extra_information.get('preferred-name', None)
    #         name = None
    #
    #         existing_affiliation = cls.nodes.get_or_none(scopus_id=scopus_id)
    #         if existing_affiliation:
    #             return existing_affiliation
    #
    #         if parent_name_data:
    #             if not isinstance(parent_name_data, dict):
    #                 return None
    #
    #             name = parent_name_data.get('$', None)
    #
    #         if not parent_name_data and preferred_name_data:
    #             name = preferred_name_data.get('$', None)
    #
    #         if not name:
    #             return None
    #
    #         address = extra_information.get('address', {})
    #         city = None
    #         country = None
    #         if isinstance(address, dict):
    #             city = address.get('city')
    #             country = address.get('country')
    #         try:
    #             affiliation_instance = cls.nodes.get(name=name, city=city, country=country)
    #
    #         except cls.DoesNotExist:
    #             affiliation_instance = cls(
    #                 scopus_id=scopus_id,
    #                 name=name,
    #                 city=city,
    #                 country=country
    #             ).save()
    #         print("Time to create affiliation: ", time.time() - time_0)
    #         return affiliation_instance
    #     except Exception as e:
    #         raise ValueError(f"Error creating affiliation: {e}")
