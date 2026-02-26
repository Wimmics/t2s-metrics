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
