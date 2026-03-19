def normalize_answer_set_basic(result):
    """
    Normalize execution results to a set of tuples.
    Handles ASK and SELECT queries.
    """
    if isinstance(result, bool):
        return {("ASK_TRUE",)} if result else set()

    # SELECT results
    return set(tuple(row) for row in result)


def normalize_answer_set_list(result):
    """
    Normalize execution results to a set of strings.
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
