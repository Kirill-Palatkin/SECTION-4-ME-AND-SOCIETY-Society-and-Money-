from SPARQLWrapper import SPARQLWrapper, JSON
import json


def run_query():
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = """
    SELECT ?childRight ?childRightLabel ?countryLabel ?legalText WHERE {
      ?childRight wdt:P31 wd:Q131412.       
      ?childRight wdt:P17 ?country.            # страна
      OPTIONAL { ?childRight wdt:P1001 ?legalText. }  
      SERVICE wikibase:label { bd:serviceParam wikibase:language "ru". }
    }
    LIMIT 10
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results


if name == "__main__":
    data = run_query()
    with open("../data/wikidata_export.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
print("Данные сохранены в wikidata_export.json")
