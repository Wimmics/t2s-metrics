from rdflib.plugins.sparql.parser import parseQuery


def syntax_score(query: str) -> float:
    try:
        parseQuery(query)
        return 1.0
    except Exception:
        return 0.0
