# -*- coding: utf-8 -*-
"""
Created on Mon May 23 2021

@author: Nicolas
"""
from urllib.parse import quote_plus as url_encode
from urllib.parse import unquote
import numpy as np


def encodeFacets(url, facets):
    '''Codifica las "facets" de la URL a percent-encoding
    para que pueda ser utilizada en las peticiones a las APIs'''

    if facets:
        return url.replace(unquote(facets), facets)
    else:
        return url


def recastDfAffiliations(dfAffiliations):
    '''Reestructura el dataframe de afiliaciones para que tenga
    los campos adecuados y una estructura de datos más útil'''

    # Elimina la columna @_fa
    dfAffiliations.pop("@_fa")

    # Elimina la columna prism:url
    dfAffiliations.pop("prism:url")

    # Renombra las columnas
    dfAffiliations.rename(columns={
        'dc:identifier': 'identifier',
        'affiliation-name': 'affiliation_name',
        'document-count': 'document_count'}, inplace=True)

    # Modifica el valor de la columna identifier. Ej. AFFILIATION_ID:60072059 -> 60072059
    dfAffiliations['identifier'] = dfAffiliations['identifier'].apply(lambda x: x.split(":")[1])


def rewriteArticleAffilList(articleAffilList):
    '''Reestructura el diccionario de afiliaciones de los artículos para
    que tenga los campos adecuados y una estructura de datos más útil'''

    for articleAffildict in articleAffilList:
        articleAffildict.pop('@_fa')
        articleAffildict.pop('affiliation-url')
    return articleAffilList


def rewriteArticleAuthors(articleAuthorsList):
    '''Reestructura el diccionario de autores de los artículos para
    que tenga los campos adecuados y una estructura de datos más útil'''

    for articleAuthorsdict in articleAuthorsList:
        articleAuthorsdict.pop('@_fa')
        articleAuthorsdict.pop('author-url')
        newAfid = []
        if 'afid' in articleAuthorsdict:
            for item in articleAuthorsdict['afid']:
                newAfid.append(item['$'])
            articleAuthorsdict['afid'] = newAfid
        else:
            articleAuthorsdict['afid'] = newAfid
    return articleAuthorsList


def recastDfArticles(dfArticles):
    '''Reestructura el dataframe de artículos para que tenga
    los campos adecuados y una estructura de datos más útil'''

    # Elimina los registros con affiliations igual a NaN
    dfArticles.dropna(subset=['affiliation'], inplace=True)

    # Reinicia los índices del dataframe
    dfArticles.reset_index(drop=True, inplace=True)

    # Elimina la columna @_fa
    dfArticles.pop("@_fa")

    # Elimina la columna prism:url
    dfArticles.pop("prism:url")

    # Renombra las sigueintes columnas
    dfArticles.rename(
        columns={'dc:identifier': 'identifier',
                 'dc:title': 'title',
                 'prism:coverDate': 'publication_date',
                 'dc:description': 'abstract',
                 'dc:title': 'title',
                 'author': 'authors',
                 'affiliation': 'affiliations',
                 'authkeywords': 'author_keywords'}, inplace=True)

    # Modifica el valor de la columna affiliations.
    dfArticles['affiliations'] = dfArticles['affiliations'].apply(lambda x: rewriteArticleAffilList(x))

    # Modifica el valor de la columna authors.
    dfArticles['authors'] = dfArticles['authors'].apply(lambda x: rewriteArticleAuthors(x))

    # Modifica el valor de la columna identifier.
    dfArticles['identifier'] = dfArticles['identifier'].apply(lambda x: x.split(':')[1])

    # Agrega la columna author_count que contiene el número de autores de un artículo.
    dfArticles['author_count'] = dfArticles['authors'].apply(lambda x: len(x))

    # Agrega la columna affiliation_count que contiene el número de afiliaciones de un artículo.
    dfArticles['affiliation_count'] = dfArticles['affiliations'].apply(lambda x: len(x))


def chunker(seq, size):
    '''Divide una lista en sublistas con un tamaño máximo'''

    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def recastDfAuthors(dfAuthors):
    '''Reestructura el dataframe de autores para que tenga
    los campos adecuados y una estructura de datos más útil'''

    # Agrega la columna identifier que contiene el identificador de SCOPUS de un autor.
    dfAuthors['identifier'] = dfAuthors['coredata'].apply(lambda x: x["dc:identifier"].split(':')[1]
    if "dc:identifier" in x else np.nan)

    # Agrega la columna identifier que contiene el electronic identifier de un autor.
    dfAuthors['eid'] = dfAuthors['coredata'].apply(lambda x: x["eid"] if "eid" in x else np.nan)

    # Agrega la columna identifier que contiene el ORCID de un autor.
    dfAuthors['orcid'] = dfAuthors['coredata'].apply(lambda x: x["orcid"] if "orcid" in x else np.nan)

    # Agrega la columna identifier que contiene el número de documentos de un autor.
    dfAuthors['document_count'] = dfAuthors['coredata'].apply(lambda x: x["document-count"]
    if "document-count" in x else np.nan)

    # Agrega la columna identifier que contiene el nombre de un autor.
    dfAuthors['first_name'] = dfAuthors['preferred-name'].apply(
        lambda x: x['given-name'] if type(x) is dict else np.nan)

    # Agrega la columna identifier que contiene el apellido de un autor.
    dfAuthors['last_name'] = dfAuthors['preferred-name'].apply(lambda x: x['surname'] if type(x) is dict else np.nan)

    # Elimina la columna @status
    dfAuthors.pop("@status")

    # Elimina la columna @_fa
    dfAuthors.pop("@_fa")

    # Elimina la columna coredata
    dfAuthors.pop("coredata")

    # Elimina la columna preferred-name
    dfAuthors.pop("preferred-name")


def authorkeywordsToScopusSearch(authorkeywords):
    newAuthorKeywords = ''
    for item in authorkeywords:
        if '$' in item:
            newAuthorKeywords = newAuthorKeywords + item['$'] + ' | '
    return newAuthorKeywords[:-3]


def affiliationToScopusSearch(affiliation):
    newAffiliation = []
    for item in affiliation:
        newAffiliation.append({
            '@_fa': 'true',
            'affiliation-url': item['@href'],
            'afid': item['@id'],
            'affilname': item['affilname'] if "affilname" in item else np.nan,
            'affiliation-city': item['affiliation-city'] if "affiliation-city" in item else np.nan,
            'affiliation-country': item['affiliation-country'],
        })
    return newAffiliation


def authorToScopusSearch(author):
    newAuthor = []
    for item in author:
        newAuthorDict = {}
        newAuthorDict['@_fa'] = 'true'
        newAuthorDict['author-url'] = item['author-url']
        newAuthorDict['authid'] = item['@auid']
        newAuthorDict['authname'] = item['ce:indexed-name'] if "ce:indexed-name" in item else np.nan,
        newAuthorDict['surname'] = item['ce:surname'] if "ce:surname" in item else np.nan,
        newAuthorDict['given-name'] = item['ce:given-name'] if "ce:given-name" in item else np.nan,
        newAuthorDict['initials'] = item['ce:initials'] if "ce:initials" in item else np.nan,
        if 'affiliation' in item:
            if type(item['affiliation']) == list:
                newAuthorDict['afid'] = [{'@_fa': 'true', '$': afil['@id']} for afil in item['affiliation']]
            else:
                newAuthorDict['afid'] = [{'@_fa': 'true', '$': item['affiliation']['@id']}]
        else:
            newAuthorDict['afid'] = []
        newAuthor.append(newAuthorDict)

    return newAuthor


def articleRetrievalToScopusSearch(articleRetrieval):
    '''Reestructura un artículo obtenido a través de la API abstract
    retrieval a la estructura de la API scopus search'''

    scopusSearch = {}
    """
    #@_fa
    scopusSearch['@_fa'] = 'true'
    #prism:url
    if 'prism:url' in articleRetrieval['coredata']:
        scopusSearch['prism:url'] = articleRetrieval['coredata']['prism:url']
    else:
        scopusSearch['prism:url'] = np.nan
    """
    # dc:identifier
    if 'dc:identifier' in articleRetrieval['coredata']:
        scopusSearch['dc:identifier'] = articleRetrieval['coredata']['dc:identifier']
    else:
        scopusSearch['dc:identifier'] = np.nan
    """
    #prism:doi
    if 'eid' in articleRetrieval['coredata']:
        scopusSearch['eid'] = articleRetrieval['coredata']['eid']
    else:
        scopusSearch['eid'] = np.nan
    #dc:title
    if 'dc:title' in articleRetrieval['coredata']:
        scopusSearch['dc:title'] = articleRetrieval['coredata']['dc:title']
    else:
        scopusSearch['dc:title'] = np.nan
    #prism:coverDate
    if 'prism:coverDate' in articleRetrieval['coredata']:
        scopusSearch['prism:coverDate'] = articleRetrieval['coredata']['prism:coverDate']
    else:
        scopusSearch['prism:coverDate'] = np.nan
    #dc:description
    if 'dc:description' in articleRetrieval['coredata']:
        scopusSearch['dc:description'] = articleRetrieval['coredata']['dc:description']
    else:
        scopusSearch['dc:description'] = np.nan
    """
    # affiliation
    if 'affiliation' in articleRetrieval:
        if type(articleRetrieval['affiliation']) == list:
            scopusSearch['affiliation'] = affiliationToScopusSearch(articleRetrieval['affiliation'])
        else:
            scopusSearch['affiliation'] = affiliationToScopusSearch([articleRetrieval['affiliation']])
    else:
        scopusSearch['affiliation'] = np.nan
    # author
    if 'authors' in articleRetrieval:
        scopusSearch['author'] = authorToScopusSearch(articleRetrieval['authors']['author'])
    else:
        scopusSearch['author'] = np.nan
    """
    #authkeywords
    if 'authkeywords' in articleRetrieval:
        if articleRetrieval['authkeywords'] is not None:
            scopusSearch['authkeywords'] = authorkeywordsToScopusSearch(
                articleRetrieval['authkeywords']['author-keyword'])
        else:
            scopusSearch['authkeywords'] = np.nan
    else:
        scopusSearch['authkeywords'] = np.nan
    """

    return scopusSearch
