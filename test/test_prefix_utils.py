from t2smetrics.core.eval import QueryCase
from t2smetrics.representation.preprocessing import prefix_preprocessor
from t2smetrics.representation.sparql_query import SparqlQuery
from t2smetrics.utils.prefix_utils import add_known_prefixes


def test_default_behavior_of_add_known_prefixes():
    query = "SELECT * WHERE { ?s foaf:name ?name }"

    assert add_known_prefixes(query) == query


def test_add_known_prefixes_can_disable_popular_prefixes():
    query = "SELECT * WHERE { ?s foaf:name ?name }"

    assert add_known_prefixes(query, add_popular_prefixes=False) == query


def test_add_known_prefixes_can_add_popular_prefixes():
    query = "SELECT * WHERE { ?s foaf:name ?name }"
    processed = add_known_prefixes(query, add_popular_prefixes=True)

    assert processed.startswith("PREFIX foaf: <http://xmlns.com/foaf/0.1/>\n")
    assert processed.endswith(query)


def test_add_known_prefixes_adds_custom_prefixes():
    query = "SELECT * WHERE { ?s ex:name ?name }"

    processed = add_known_prefixes(
        query,
        add_custom_prefixes={"ex": "http://example.org/"},
    )

    assert processed.startswith("PREFIX ex: <http://example.org/>\n")
    assert processed.endswith(query)


def test_prefix_preprocessor_applies_to_both_queries():
    case = QueryCase(
        id="1",
        golden=SparqlQuery("SELECT * WHERE { ?s ex:name ?name }"),
        generated=SparqlQuery("SELECT * WHERE { ?s ex:name ?name }"),
        order_matters=False,
    )

    processed = prefix_preprocessor(
        add_custom_prefixes={"ex": "http://example.org/"},
    ).apply(case)

    assert processed.golden.raw.startswith("PREFIX ex: <http://example.org/>\n")
    assert processed.generated.raw.startswith("PREFIX ex: <http://example.org/>\n")
