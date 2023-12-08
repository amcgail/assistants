from modularity import *
from urllib.error import HTTPError

from time import sleep

import sys
sys.path.append( str(Path(BASE_DIR, 'scihub.py/scihub') ) )
from scihub import SciHub
sh = SciHub()

sys.path.append( '..' )

prefix = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX magc: <https://makg.org/class/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX fabio: <http://purl.org/spar/fabio/>
PREFIX prism: <http://prismstandard.org/namespaces/basic/2.0/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

class evaluate_MAKG(Module):
    name = "evaluate_MAKG"
    goal = "evaluate the Microsoft Academic Knowledge Graph results"
    format = "text"

class MAKG(Module):
    name = "formulate_makg_query"
    goal = "formulate a query for the Microsoft Academic Knowledge Graph"
    format = "text"
    params = """
SELECT distinct ?paperTitle ?paperPubDate
WHERE {
    paper rdf:type magc:Paper .
    ... your query here ...
    ... for example: ...
    ?field rdf:type <https://makg.org/class/FieldOfStudy> .
    ?field foaf:name "Medicine"^^xsd:string .
    ... or ...
    ?paper dcterms:title ?paperTitle .
    ?paperTitle bif:contains "collective" .
}
LIMIT 10"""
    detailed_instructions = """
    Please only return the query, without an explanation.
    You may use the prism:publicationDate, fabio:hasDiscipline, and dcterms:title attributes of a paper.
    Ideally express all of your constraints in terms of these attributes.
    """

    def execute_it(self, args):
        from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions

        sparql = SPARQLWrapper("https://makg.org/sparql")
        sparql.setQuery(prefix + args)
        sparql.setReturnFormat(JSON)

        try:
            results = sparql.query().convert()
        except (
            SPARQLExceptions.EndPointInternalError,
            SPARQLExceptions.QueryBadFormed,
            HTTPError
        ) as e:
            self.add_message("system", "Error! ")
            # add the content of the exception
            self.add_message("system", str(e))
            return self.contemplate()
        
        results = results['results']['bindings']
        results = [f"{r['paperTitle']['value']} ({r['paperPubDate']['value']})" for r in results]
        results = "\n\n".join(results)

        return results

class FindPotentialPapers(Module):
    name = "find_potential_papers"
    goal = "to find potential papers to read, by breaking the given goal into a set of keyword searches."
    params = """{ 'searches': ['search 1', 'search 2', ...] }"""

    detailed_instructions = """
        This module takes a goal and breaks it down into a set of keyword searches.
        It will returns a list of potential papers to read, from Google Scholar searches.
    """

    def execute_it(self, args):
        import requests
        from bs4 import BeautifulSoup
        keywords = args['searches']

        result_list = []

        for kw in keywords:
            sleep(3)
            results = MAKG(meta_goal=f"You are to translate this query into a SPARQL query: '{kw}'")
            results = results.contemplate()
            result_list.append(results)

        return "\n\n".join(result_list)

class ResearchOutline(Module):
    description = "This module outlines a plan for researching a topic."
    name = "research_outline"
    goal = "outline a plan for researching a topic by specifying the various individual goals"
    params = """{ 'goals': ['goal 1', 'goal 2', ...] }"""

    def execute_it(self, args):

        for goal in args['goals']:

            # then find potential papers for each keyword
            fpp = FindPotentialPapers(meta_goal=goal)
            potential_papers = fpp.contemplate()

            print(potential_papers)


papers = ResearchOutline(meta_goal="recent research on collectivity, individuality, and naming practices, how they are intertwined, and how they are related to the concept of the self. I am especially interested in large-N analyses ")
papers = papers.contemplate()