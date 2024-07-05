from django.db import transaction
from neomodel import db

from apps.dashboards.domain.entities.author import Author
from apps.dashboards.domain.entities.author_topics import AuthorTopics
from apps.dashboards.domain.entities.author_topics_year_contribution import AuthorTopicsYearContribution
from apps.dashboards.domain.entities.author_year_contribution import AuthorYearContribution
from apps.dashboards.domain.entities.country_acumulated import CountryAcumulated
from apps.dashboards.domain.entities.country_topics import CountryTopics
from apps.dashboards.domain.entities.country_topics_acumulated import CountryTopicsAcumulated
from apps.dashboards.domain.entities.country_topics_year import CountryTopicsYear
from apps.dashboards.domain.entities.country_year import CountryYear
from apps.dashboards.domain.repositories.populate_repository import PopulateRepository
from apps.dashboards.utils.utils import extract_year, count_articles_per_year_author, count_articles_per_year_country, \
    get_articles_topics_info, get_authors_info, get_affiliations_info, count_articles_per_year_affiliation


class PopulateService(PopulateRepository):

    def populate(self):
        self.populate_country()

    @transaction.atomic
    def populate_author(self):
        query = """
                        MATCH (au:Author)-[w:WROTE]->(ar:Article)
                        OPTIONAL MATCH (ar)-[u:USES]->(t:Topic)
                        RETURN au.scopus_id, ar.scopus_id, ar.publication_date, t.name
                        """
        results, meta = db.cypher_query(query)

        au_scopus_ids = []
        ar_scopus_ids = []
        ar_publication_dates = []
        topics = []

        for result in results:
            au_scopus_ids.append(result[0])
            ar_scopus_ids.append(result[1])
            ar_publication_dates.append(result[2])
            topics.append(result[3] if result[3] is not None else " ")

        years = extract_year(ar_publication_dates)

        authors_data = count_articles_per_year_author(au_scopus_ids, ar_scopus_ids, years, topics)

        for author_data in authors_data:
            author = Author(
                scopus_id=author_data['idScopus'],
                total_articles=author_data['totalArticles']
            )
            author.save()
            for year_info in author_data['years']:
                author_years = AuthorYearContribution(scopus_id=author_data['idScopus'], year=year_info['year'],
                                                      total_articles=year_info['numArticles'])
                author_years.save()
            for topic_data in author_data['topics']:
                author_topics = AuthorTopics(
                    scopus_id=author_data['idScopus'],
                    topic_name=topic_data['topic'],
                    total_articles=topic_data['totalTopicArticles']
                )
                author_topics.save()
                for year_info in topic_data['topic_years']:
                    topics_years = AuthorTopicsYearContribution(
                        scopus_id=author_data['idScopus'],
                        topic_name=topic_data['topic'], year=year_info['year'],
                        total_articles=year_info['numArticles']
                    )
                    topics_years.save()

    def get_articles_topics_dict(self):
        query = """
                MATCH (ar:Article)
                OPTIONAL MATCH (ar)-[u:USES]->(t:Topic)
                RETURN ar.scopus_id, ar.publication_date, t.name
                """
        results, meta = db.cypher_query(query)

        ar_scopus_ids = []
        ar_publication_dates = []
        topics = []

        for result in results:
            ar_scopus_ids.append(result[0])
            ar_publication_dates.append(result[1])
            topics.append(result[2] if result[2] is not None else " ")

        years = extract_year(ar_publication_dates)

        country_data_list = count_articles_per_year_country(ar_scopus_ids, years, topics)

        country_dicts = []  # Utilizar una lista para almacenar los diccionarios de país

        for country_data in country_data_list:
            years_contributions = [{"year": year_info['year'], "num_articles": year_info['numArticles']} for
                                   year_info in country_data['years']]

            topics_list = []
            for topic_data in country_data['topics']:
                num_articles_per_year = [{"year": year_info['year'], "num_articles": year_info['numArticles']}
                                         for year_info in topic_data['topic_years']]
                topic = {
                    "topic_name": topic_data['topic'],
                    "num_articles_per_year": num_articles_per_year,
                    "total_topic_articles": topic_data['totalTopicArticles']
                }
                topics_list.append(topic)

            country_dict = {
                "name": "Ecuador",
                "years": years_contributions,
                "topics": topics_list,
                "total_articles": country_data['totalArticles'],
            }

            country_dicts.append(country_dict)  # Agregar el diccionario a la lista

        return country_dicts

    def get_authors_dict(self):
        query = """
                MATCH (au:Author)-[w:WROTE]->(ar:Article)
                OPTIONAL MATCH (ar)-[u:USES]->(t:Topic)
                RETURN au.scopus_id, ar.scopus_id, ar.publication_date, t.name
                """
        results, meta = db.cypher_query(query)

        au_scopus_ids = []
        ar_scopus_ids = []
        ar_publication_dates = []
        topics = []

        for result in results:
            au_scopus_ids.append(result[0])
            ar_scopus_ids.append(result[1])
            ar_publication_dates.append(result[2])
            topics.append(result[3] if result[3] is not None else " ")

        years = extract_year(ar_publication_dates)

        authors_data = count_articles_per_year_author(au_scopus_ids, ar_scopus_ids, years, topics)

        authors_list = []

        for author_data in authors_data:
            years = [{"year": year_info['year'], "num_articles": year_info['numArticles']} for year_info in
                     author_data['years']]

            topics = []
            for topic_data in author_data['topics']:
                num_articles_per_year = [{"year": year_info['year'], "num_articles": year_info['numArticles']}
                                         for year_info in topic_data['topic_years']]
                topic = {
                    "topic_name": topic_data['topic'],
                    "num_articles_per_year": num_articles_per_year,
                    "total_topic_articles": topic_data['totalTopicArticles']
                }
                topics.append(topic)

            author_dict = {
                "scopus_id": author_data['idScopus'],
                "years": years,
                "topics": topics,
                "total_articles": author_data['totalArticles']
            }

            authors_list.append(author_dict)
        authors = get_authors_info(authors_list)
        return authors

    def get_affiliations_dict(self):
        query = """
                MATCH (ar:Article)-[b:BELONGS_TO]->(af:Affiliation)
                OPTIONAL MATCH (ar)-[u:USES]->(t:Topic)
                RETURN af.scopus_id, af.name, ar.scopus_id, ar.publication_date, t.name
            """
        results, meta = db.cypher_query(query)

        af_scopus_ids = []
        af_names = []
        ar_scopus_ids = []
        ar_publication_dates = []
        topics = []

        for result in results:
            af_scopus_ids.append(result[0])
            af_names.append(result[1])
            ar_scopus_ids.append(result[2])
            ar_publication_dates.append(result[3])
            topics.append(result[4] if result[4] is not None else " ")

        years = extract_year(ar_publication_dates)

        affiliations_data = count_articles_per_year_affiliation(af_scopus_ids, af_names, ar_scopus_ids, years, topics)

        affiliations_list = []

        for affiliation_data in affiliations_data:
            # Crear diccionarios para YearContribution
            years = [{"year": year_info['year'], "num_articles": year_info['numArticles']} for year_info in
                     affiliation_data['years']]

            # Crear diccionarios para Topic
            topics = []
            for topic_data in affiliation_data['topics']:
                num_articles_per_year = [{"year": year_info['year'], "num_articles": year_info['numArticles']}
                                         for year_info in topic_data['topic_years']]
                topic = {
                    "topic_name": topic_data['topic'],
                    "num_articles_per_year": num_articles_per_year,
                    "total_topic_articles": topic_data['totalTopicArticles']
                }
                topics.append(topic)

            # Crear diccionario para Affiliation
            affiliation_dict = {
                "id_affiliation": affiliation_data['idScopus'],
                "name": affiliation_data['name'],  # Asegurarse de incluir el nombre
                "years": years,
                "topics": topics,
                "total_articles": affiliation_data['totalArticles']
            }

            affiliations_list.append(affiliation_dict)

        affiliations = get_affiliations_info(affiliations_list)
        return affiliations

    @transaction.atomic
    def populate_country(self):
        authors = self.get_authors_dict()
        countries = self.get_articles_topics_dict()
        articles_topics = get_articles_topics_info(countries)
        affiliations = self.get_affiliations_dict()
        for year_data in articles_topics["Articles"]["Per_year"]:
            year = int(year_data["name"])
            total_authors = next((item["value"] for item in authors["Per_year"] if int(item["name"]) == year), 0)
            total_affiliations = next((item["value"] for item in affiliations["Per_year"] if int(item["name"]) == year),
                                      0)
            total_topics = next(
                (item["value"] for item in articles_topics["Topics"]["Per_year"] if int(item["name"]) == year), 0)

            country_year = CountryYear(
                year=year,
                total_authors=total_authors,
                total_articles=year_data["value"],
                total_affiliations=total_affiliations,
                total_topics=total_topics
            )
            country_year.save()

            # Mapeo para CountryAcumulated
        for year_data in articles_topics["Articles"]["Acumulative"]:
            year = int(year_data["name"])
            total_authors = next((item["value"] for item in authors["Acumulative"] if int(item["name"]) == year), 0)
            total_affiliations = next(
                (item["value"] for item in affiliations["Acumulative"] if int(item["name"]) == year), 0)
            total_topics = next(
                (item["value"] for item in articles_topics["Topics"]["Acumulative"] if int(item["name"]) == year), 0)

            country_acumulated = CountryAcumulated(
                year=year,
                total_authors=total_authors,
                total_articles=year_data["value"],
                total_affiliations=total_affiliations,
                total_topics=total_topics
            )
            country_acumulated.save()

        for country_data in countries:
            for topic_data in country_data['topics']:
                for year_info in topic_data['num_articles_per_year']:
                    country_topic_year = CountryTopicsYear(
                        topic_name=topic_data['topic_name'],
                        year=year_info['year'],
                        total_articles=year_info['num_articles']
                    )
                    country_topic_year.save()

        for country_data in countries:
            for topic_data in country_data['topics']:
                country_topic = CountryTopics(
                    topic_name=topic_data['topic_name'],
                    total_articles=topic_data['total_topic_articles']
                )
                country_topic.save()

        for country_data in countries:
            for topic_data in country_data['topics']:
                accumulated_articles = 0
                for year_info in sorted(topic_data['num_articles_per_year'], key=lambda x: x['year']):
                    accumulated_articles += year_info['num_articles']
                    country_topic_acumulated = CountryTopicsAcumulated(
                        topic_name=topic_data['topic_name'],
                        year=year_info['year'],
                        total_articles=accumulated_articles
                    )
                    country_topic_acumulated.save()


