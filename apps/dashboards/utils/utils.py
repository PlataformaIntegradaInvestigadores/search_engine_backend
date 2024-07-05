from collections import defaultdict

from neomodel import db


def extract_year(years_column):
    years = []
    for date in years_column:
        year = date[:4]
        years.append(year)
    return years


def count_articles_per_year_author(entity_id_column, articles_id_column, years_column, topics):
    author_data = defaultdict(lambda: {
        "years": defaultdict(set),
        "topics": defaultdict(lambda: defaultdict(int))
    })

    for entity_id, article_id, year, topic in zip(entity_id_column, articles_id_column, years_column, topics):
        author_data[entity_id]["years"][year].add(article_id)
        author_data[entity_id]["topics"][topic][year] += 1

    processed_data = []
    for entity_id, data in author_data.items():
        total_articles = sum(len(articles) for articles in data["years"].values())
        year_data = [{"year": year, "numArticles": len(articles)} for year, articles in data["years"].items()]

        topic_data = []
        for topic, years in data["topics"].items():
            total_topic_articles = sum(years.values())
            topic_years_data = [{"year": year, "numArticles": count} for year, count in years.items()]
            topic_data.append({
                "topic": topic,
                "topic_years": topic_years_data,
                "totalTopicArticles": total_topic_articles
            })

        processed_data.append({
            "idScopus": entity_id,
            "years": year_data,
            "totalArticles": total_articles,
            "topics": topic_data
        })
    return processed_data


def count_articles_per_year_country(articles_id, years, topics):
    data = {
        "years": defaultdict(set),
        "topics": defaultdict(lambda: defaultdict(int))
    }

    for article_id, year, topic in zip(articles_id, years, topics):
        data["years"][year].add(article_id)
        data["topics"][topic][year] += 1

    total_articles = sum(len(articles) for articles in data["years"].values())
    year_data = [{"year": year, "numArticles": len(articles)} for year, articles in data["years"].items()]

    topic_data = []
    for topic, years in data["topics"].items():
        total_topic_articles = sum(years.values())
        topic_years_data = [{"year": year, "numArticles": count} for year, count in years.items()]
        topic_data.append({
            "topic": topic,
            "topic_years": topic_years_data,
            "totalTopicArticles": total_topic_articles
        })

    processed_data = [{
        "years": year_data,
        "totalArticles": total_articles,
        "topics": topic_data
    }]

    return processed_data


def get_articles_topics_info(countries):
    articles_per_year = defaultdict(int)
    articles_acumulative = defaultdict(int)
    topics_per_year = defaultdict(set)

    for country in countries:  # countries debe ser una lista de diccionarios
        for year_contrib in country['years']:
            year = year_contrib['year']
            articles_per_year[year] += year_contrib['num_articles']

        for topic in country['topics']:
            for year_contrib in topic['num_articles_per_year']:
                year = year_contrib['year']
                topics_per_year[year].add(topic['topic_name'])

    sorted_article_years = sorted(articles_per_year.keys())
    sorted_topic_years = sorted(topics_per_year.keys())

    articles_acumulated_count = 0
    for year in sorted_article_years:
        articles_acumulated_count += articles_per_year[year]
        articles_acumulative[year] = articles_acumulated_count

    acumulated_topics = set()
    topics_per_year_list = []
    topics_acumulative_list = []

    for year in sorted_topic_years:
        new_topics = topics_per_year[year] - acumulated_topics
        num_new_topics = len(new_topics)
        topics_per_year_list.append({"name": str(year), "value": num_new_topics})
        acumulated_topics.update(new_topics)
        topics_acumulative_list.append({"name": str(year), "value": len(acumulated_topics)})

    # Invertir las listas para el orden descendente de los años
    articles_per_year_list = [{"name": str(year), "value": articles_per_year[year]} for year in sorted_article_years]
    articles_acumulative_list = [{"name": str(year), "value": articles_acumulative[year]} for year in sorted_article_years]
    articles_per_year_list.reverse()
    articles_acumulative_list.reverse()
    topics_per_year_list.reverse()
    topics_acumulative_list.reverse()

    response_data = {
        "Articles": {
            "Per_year": articles_per_year_list,
            "Acumulative": articles_acumulative_list
        },
        "Topics": {
            "Per_year": topics_per_year_list,
            "Acumulative": topics_acumulative_list
        }
    }
    return response_data


def get_authors_info(authors):
    authors_per_year = defaultdict(set)

    for author in authors:
        for year_contrib in author['years']:
            year = year_contrib['year']
            authors_per_year[year].add(author['scopus_id'])

    sorted_years = sorted(authors_per_year.keys())

    acumulated_authors = set()
    per_year_list = []
    acumulated_list = []

    for year in sorted_years:
        new_authors = authors_per_year[year] - acumulated_authors
        num_new_authors = len(new_authors)
        per_year_list.append({"name": str(year), "value": num_new_authors})
        acumulated_authors.update(new_authors)
        acumulated_list.append({"name": str(year), "value": len(acumulated_authors)})

    per_year_list.reverse()
    acumulated_list.reverse()

    response_data = {
        "Per_year": per_year_list,
        "Acumulative": acumulated_list
    }
    return response_data


def get_affiliations_info(affiliations):
    per_year = defaultdict(int)
    acumulated = defaultdict(int)
    affiliations_per_year = defaultdict(set)

    for affiliation in affiliations:
        for year_contrib in affiliation['years']:
            year = year_contrib['year']
            affiliations_per_year[year].add(affiliation['id_affiliation'])

    sorted_years = sorted(affiliations_per_year.keys())

    acumulated_affiliations = set()
    per_year_list = []
    acumulated_list = []

    for year in sorted_years:
        new_affiliations = affiliations_per_year[year] - acumulated_affiliations
        num_new_affiliations = len(new_affiliations)
        per_year_list.append({"name": str(year), "value": num_new_affiliations})
        acumulated_affiliations.update(new_affiliations)
        acumulated_list.append({"name": str(year), "value": len(acumulated_affiliations)})

    # Invertir las listas para el orden descendente de los años
    per_year_list.reverse()
    acumulated_list.reverse()

    response_data = {
        "Per_year": per_year_list,
        "Acumulative": acumulated_list
    }
    print(response_data)
    return response_data


def count_articles_per_year_affiliation(af_scopus_ids, af_names, ar_scopus_ids, years, topics):
    affiliation_data = defaultdict(lambda: {
        "name": None,
        "years": defaultdict(set),  # Usamos un set para evitar duplicados
        "topics": defaultdict(lambda: defaultdict(set))
    })

    for af_scopus_id, af_name, ar_scopus_id, year, topic in zip(af_scopus_ids, af_names, ar_scopus_ids, years, topics):
        if affiliation_data[af_scopus_id]["name"] is None:
            affiliation_data[af_scopus_id]["name"] = af_name
        affiliation_data[af_scopus_id]["years"][year].add(ar_scopus_id)
        affiliation_data[af_scopus_id]["topics"][topic][year].add(ar_scopus_id)

    processed_data = []
    for af_scopus_id, data in affiliation_data.items():
        total_articles = sum(len(articles) for articles in data["years"].values())
        year_data = [{"year": year, "numArticles": len(articles)} for year, articles in data["years"].items()]

        topic_data = []
        for topic, years in data["topics"].items():
            total_topic_articles = sum(len(articles) for articles in years.values())
            topic_years_data = [{"year": year, "numArticles": len(articles)} for year, articles in years.items()]
            topic_data.append({
                "topic": topic,
                "topic_years": topic_years_data,
                "totalTopicArticles": total_topic_articles
            })

        processed_data.append({
            "idScopus": af_scopus_id,
            "name": data["name"],  # Asegurarse de incluir el nombre
            "years": year_data,
            "totalArticles": total_articles,
            "topics": topic_data
        })

    return processed_data
