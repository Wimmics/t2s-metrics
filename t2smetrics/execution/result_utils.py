import re


def normalize_answer_set_basic(result):
    """Normalize execution results to a set of tuples.
    Handles ASK and SELECT queries.
    """
    if isinstance(result, bool):
        return {("ASK_TRUE",)} if result else set()

    # SELECT results
    return set(tuple(row) for row in result)


def normalize_answer_set_list(result):
    """Normalize execution results to a set of strings.
    Handles ASK and SELECT queries.
    """
    if isinstance(result, bool):
        return ["ASK_TRUE"] if result else ["ASK_FALSE"]

    elif not result:
        return list()

    # SELECT results
    return [x for subset in result for x in subset]


def normalize_query_response(response, return_type="tuples"):

    if response is None:
        return []

    if return_type not in {"tuples", "json"}:
        raise ValueError(f"Invalid return_type: {return_type}")

    # ASK queries
    if "boolean" in response:
        return bool(response["boolean"])

    # SELECT queries
    vars_ = response["head"]["vars"]
    rows = []

    if return_type == "json":
        # Some SPARQL endpoints e.g. Qlever return [None] for empty results.
        bindings = response["results"]["bindings"]
        return [] if bindings == [None] else bindings

    else:
        for binding in response["results"]["bindings"]:
            # Some SPARQL endpoints e.g. Qlever return [None] for empty results.
            if binding is None or len(binding) == 0:
                continue
            row = tuple(
                binding[var]["value"] if var in binding else None for var in vars_
            )
            rows.append(row)

        return rows


def safe_append_limit(query, limit_value=25000) -> str:
    """Safely append LIMIT to a SPARQL query if it doesn't already have one.

    Args:
        query (str): SPARQL query string
        limit_value (int): LIMIT value to append (default: 25000)

    Returns:
        str: SPARQL query string with LIMIT appended if it was not already present
    """
    # Don't add LIMIT to ASK queries
    if re.match(r"^\s*ASK\b", query, re.IGNORECASE):
        return query

    # Check if LIMIT already exists (case insensitive)
    if re.search(r"\bLIMIT\s+\d+", query, re.IGNORECASE):
        return query

    # Remove trailing whitespace and add LIMIT
    query = query.rstrip()

    # Add semicolon if needed (some SPARQL endpoints require it before LIMIT)
    if not query.endswith(";") and not query.endswith("}"):
        query += " "

    query += f" LIMIT {limit_value}"
    return query
