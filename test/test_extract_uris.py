from t2smetrics.representation.uri_utils import extract_uris


def test_simple_uri_in_angle_brackets():
    """Test extracting a simple URI in angle brackets"""
    query = "SELECT * WHERE { <http://example.org/book> ?p ?o }"
    result = extract_uris(query)

    assert result == {"http://example.org/book"}


def test_multiple_uris_in_angle_brackets():
    """Test extracting multiple URIs in angle brackets"""
    query = """
    SELECT * WHERE { 
        <http://example.org/book> <http://schema.org/name> "Harry Potter" .
        <http://example.org/author> <http://schema.org/name> "J.K. Rowling" .
    }
    """
    result = extract_uris(query)
    expected = {
        "http://example.org/book",
        "http://schema.org/name",
        "http://example.org/author",
    }
    assert result == expected


def test_uris_with_special_characters():
    """Test URIs containing special characters"""
    query = """
    SELECT * WHERE { 
        <http://example.org/book#chapter1> ?p ?o .
        <http://example.org/path/to/resource?query=value&param=2> ?p ?o .
        <http://example.org/resource%20with%20spaces> ?p ?o .
    }
    """
    result = extract_uris(query)
    expected = {
        "http://example.org/book#chapter1",
        "http://example.org/path/to/resource?query=value&param=2",
        "http://example.org/resource%20with%20spaces",
    }
    assert result == expected


def test_prefixed_uris():
    """Test extracting URIs using prefixes"""
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT * WHERE { 
        ?s rdf:type foaf:Person .
        ?s foaf:name ?name .
    }
    """
    result = extract_uris(query)
    # The simplified implementation will extract prefixed names
    assert "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in result
    assert "http://xmlns.com/foaf/0.1/Person" in result
    assert "http://xmlns.com/foaf/0.1/name" in result


def test_uris_in_comments():
    """Test that URIs in comments are NOT extracted"""
    query = """
    # This is a comment with <http://example.org/should-not-extract>
    SELECT * WHERE { 
        <http://example.org/real-uri> ?p ?o .
    }
    /* Multi-line comment with <http://example.org/another-uri> */
    """
    result = extract_uris(query)
    assert "http://example.org/should-not-extract" not in result
    assert "http://example.org/another-uri" not in result
    assert "http://example.org/real-uri" in result


def test_empty_query():
    """Test with empty string"""
    result = extract_uris("")
    assert result == set()


def test_query_with_no_uris():
    """Test query with no URIs at all"""
    query = "SELECT * WHERE { ?s ?p ?o }"
    result = extract_uris(query)
    assert result == set()


def test_uris_in_data_block():
    """Test URIs in DATA or INSERT block"""
    query = """
    INSERT DATA {
        <http://example.org/alice> <http://schema.org/knows> <http://example.org/bob> .
        <http://example.org/alice> <http://schema.org/age> 30 .
    }
    """
    result = extract_uris(query)
    expected = {
        "http://example.org/alice",
        "http://schema.org/knows",
        "http://example.org/bob",
        "http://schema.org/age",
    }
    assert result == expected


def test_uris_with_unicode():
    """Test URIs containing Unicode characters"""
    query = """
    SELECT * WHERE { 
        <http://example.org/ürich> ?p ?o .
        <http://example.org/名称> ?p ?o .
    }
    """
    result = extract_uris(query)
    expected = {"http://example.org/ürich", "http://example.org/名称"}
    assert result == expected


def test_uris_in_string_literals():
    """Test that URIs in string literals are NOT extracted"""
    query = """
    SELECT * WHERE { 
        ?s <http://schema.org/name> "This is <http://example.org/not-a-uri>" .
        ?s <http://schema.org/description> 'Another <http://example.org/fake-uri>' .
    }
    """
    result = extract_uris(query)
    assert "http://example.org/not-a-uri" not in result
    assert "http://example.org/fake-uri" not in result
    assert "http://schema.org/name" in result
    assert "http://schema.org/description" in result


def test_malformed_uri_brackets():
    """Test handling of malformed URIs in angle brackets"""
    query = """
    SELECT * WHERE { 
        <http://example.org/valid> ?p ?o .
        <http://example.org\malformed> ?p ?o .
    """
    # Note: missing closing > on second URI
    result = extract_uris(query)
    # Only complete URIs should be extracted
    assert "http://example.org/valid" in result
    assert "http://example.org/malformed" not in result


def test_uris_with_different_protocols():
    """Test URIs with different protocols"""
    query = """
    SELECT * WHERE { 
        <https://example.org/secure> ?p ?o .
        <ftp://example.org/file> ?p ?o .
        <urn:isbn:1234567890> ?p ?o .
    }
    """
    result = extract_uris(query)
    expected = {
        "https://example.org/secure",
        "ftp://example.org/file",
        "urn:isbn:1234567890",
    }
    assert result == expected


def test_uris_in_same_line():
    """Test multiple URIs on the same line"""
    query = "SELECT * WHERE { <http://example.org/subject> <http://example.org/predicate> <http://example.org/object> }"
    result = extract_uris(query)
    expected = {
        "http://example.org/subject",
        "http://example.org/predicate",
        "http://example.org/object",
    }
    assert result == expected


def test_case_insensitivity():
    """Test that URI extraction is case-sensitive (URIs should be case-sensitive)"""
    query = """
    SELECT * WHERE { 
        <http://example.org/UPPER> ?p ?o .
        <http://example.org/upper> ?p ?o .
    }
    """
    result = extract_uris(query)
    assert "http://example.org/UPPER" in result
    assert "http://example.org/upper" in result
    assert len(result) == 2


def test_whitespace_handling():
    """Test URIs with surrounding whitespace"""
    query = "SELECT * WHERE { <http://example.org/with-spaces> ?p ?o }"
    result = extract_uris(query)
    assert "http://example.org/with-spaces" in result


def test_nested_angle_brackets():
    """Test nested angle brackets (should only extract outer URI)"""
    query = """
    SELECT * WHERE { 
        <http://example.org/outer<inner>> ?p ?o .
    }
    """
    result = extract_uris(query)
    # The simplified implementation will extract the outer URI
    assert "http://example.org/outer<inner>" in result


def test_large_query_performance():
    """Test with a larger query to ensure performance is reasonable"""
    query = "SELECT * WHERE { "
    for i in range(100):
        query += f"<http://example.org/resource{i}> ?p ?o . "
    query += "}"
    result = extract_uris(query)
    assert len(result) == 100
    assert "http://example.org/resource99" in result


def test_uris_in_service_clause():
    """Test URIs in SERVICE clause"""
    query = """
    SELECT * WHERE { 
        SERVICE <http://example.org/sparql-endpoint> {
            ?s ?p ?o .
        }
    }
    """
    result = extract_uris(query)
    assert "http://example.org/sparql-endpoint" in result


def test_uris_in_graph_clause():
    """Test URIs in GRAPH clause"""
    query = """
    SELECT * WHERE { 
        GRAPH <http://example.org/named-graph> {
            ?s ?p ?o .
        }
    }
    """
    result = extract_uris(query)
    assert "http://example.org/named-graph" in result


def test_uris_with_colons_in_uri():
    """Test URIs that contain colons (not just prefix notation)"""
    query = """
    SELECT * WHERE { 
        <http://example.org/resource:with:colons> ?p ?o .
    }
    """
    result = extract_uris(query)
    assert "http://example.org/resource:with:colons" in result


def test_empty_angle_brackets():
    """Test empty angle brackets"""
    query = "SELECT * WHERE { <> ?p ?o }"
    result = extract_uris(query)
    assert result == set()  # Empty URI shouldn't be extracted


def test_duplicate_uris():
    """Test that duplicate URIs are returned as a set (no duplicates)"""
    query = """
    SELECT * WHERE { 
        <http://example.org/duplicate> ?p ?o .
        <http://example.org/duplicate> ?q ?r .
    }
    """
    result = extract_uris(query)
    assert len(result) == 1
    assert "http://example.org/duplicate" in result


def test_prefixed_uris_in_construct():
    """Test URIs in CONSTRUCT query with prefixes"""
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ex: <http://example.org/>
    CONSTRUCT { 
        ?s ex:hasName ?name .
    } WHERE {
        ?s rdf:type ex:Person .
    }
    """
    result = extract_uris(query)
    assert "http://example.org/hasName" in result
    assert "http://example.org/Person" in result
    assert "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in result


def test_uris_in_complex_query():
    query = """
    PREFIX ex: <http://example.org/>
    SELECT ?dept WHERE {
      VALUES ?emp { ex:empl-Karen.Brant%40company.org }
        ?emp ex:memberOf ?dept .\n} LIMIT 10
    """
    result = extract_uris(query)
    assert "http://example.org/empl-Karen.Brant%40company.org" in result
    assert "http://example.org/memberOf" in result
