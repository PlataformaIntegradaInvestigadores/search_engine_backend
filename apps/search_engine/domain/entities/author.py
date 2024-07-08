import time

from django_neomodel import DjangoNode
from neomodel import StructuredNode, StringProperty, RelationshipTo, Relationship, IntegerProperty, UniqueIdProperty, \
    BooleanProperty, db

from apps.search_engine.domain.entities.affiliation import Affiliation
from apps.search_engine.domain.entities.coauthored import CoAuthored
from apps.search_engine.domain.entities.topic import Topic


class Author(DjangoNode):
    scopus_id = UniqueIdProperty()
    first_name = StringProperty()
    last_name = StringProperty()
    auth_name = StringProperty()
    initials = StringProperty()
    citation_count = IntegerProperty(default=0)
    current_affiliation = StringProperty()
    affiliations = RelationshipTo('apps.search_engine.domain.entities.affiliation.Affiliation', 'AFFILIATED_WITH')
    articles = RelationshipTo('apps.search_engine.domain.entities.article.Article', 'WROTE')
    co_authors = Relationship('Author', 'CO_AUTHORED', model=CoAuthored)
    topics = RelationshipTo('apps.search_engine.domain.entities.topic.Topic', 'EXPERT_IN')
    updated = BooleanProperty(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        app_label = 'search_engine'

    @classmethod
    def from_dict(cls, author_data: dict) -> 'Author':
        scopus_id = author_data.get('authid', '')

        if not scopus_id:
            raise ValueError("Invalid scopus_id on author creation")

        try:
            author = cls.nodes.get(scopus_id=scopus_id)
            return author
        except cls.DoesNotExist:
            current_author_data = {
                "scopus_id": scopus_id,
                "first_name": author_data.get("given-name", ""),
                "last_name": author_data.get("surname", ""),
                "initials": author_data.get("initials", ""),
                "auth_name": author_data.get("authname", ""),
            }
            author = cls(**current_author_data).save()
        return author

    @staticmethod
    def validate_scopus_id(scopus_id) -> int or None:
        if scopus_id:
            try:
                scopus_id = int(scopus_id.split(":")[1])
                return scopus_id
            except ValueError:
                return None
        else:
            return None

    @classmethod
    @db.transaction
    def update_from_json(cls, author_data):
        time_0 = time.time()
        coredata = author_data.get('coredata', {})
        scopus_id = cls.validate_scopus_id(coredata.get('dc:identifier', ''))
        citation_count = coredata.get('citation-count', 0)

        if scopus_id is None:
            raise ValueError("Invalid scopus_id on author update")

        try:
            print("Updating author: ", scopus_id)
            author = cls.nodes.get(scopus_id=scopus_id)

            author_profile = author_data.get('author-profile', {})
            current_affiliation_dict = author_profile.get('current-affiliation', {})
            current_affiliation = current_affiliation_dict.get('affiliation', {})
            ip_doc = current_affiliation.get('ip-doc', {})
            parent_preferred_name = ip_doc.get('parent-preferred-name', {})

            if isinstance(parent_preferred_name, dict):
                current_aff = parent_preferred_name.get('$', '')
            else:
                current_aff = ''

            preferred_name = author_profile.get('preferred-name', {})

            author.first_name = preferred_name.get('given-name', '')
            author.last_name = preferred_name.get('surname', '')
            author.auth_name = preferred_name.get('indexed-name', '')
            author.initials = preferred_name.get('initials', '')
            author.citation_count = citation_count
            author.updated = True
            author.current_affiliation = current_aff
            author.save()

            subject_areas = author_data.get('subject-areas', {})
            if not isinstance(subject_areas, dict):
                subject_areas = {}
            keywords = subject_areas.get("subject-area", [])
            keyword_instances = [Topic.from_json(keyword.get('$', '')) for keyword in keywords]
            for keyword_instance in keyword_instances:
                if not author.topics.is_connected(keyword_instance):
                    author.topics.connect(keyword_instance)

            affiliation_history = author_profile.get('affiliation-history', {})
            affiliations = affiliation_history.get('affiliation', [])
            if isinstance(affiliations, dict):
                affiliations = [affiliations]

            affiliation_instances = [
                instance for affiliation_data in affiliations
                if (instance := Affiliation.retrieve_from_json(affiliation_data)) is not None
            ]

            for affiliation_instance in affiliation_instances:
                if not author.affiliations.is_connected(affiliation_instance):
                    author.affiliations.connect(affiliation_instance)

            print("Time spent updating author: ", time.time() - time_0)

            return author
        except cls.DoesNotExist:
            raise ValueError("Author not found")
        except Exception as e:
            raise ValueError("Error updating author from json: " + str(e))
