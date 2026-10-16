import json
import re
from pathlib import Path


def add_known_prefixes(
    query: str,
    add_popular_prefixes: bool = False,
    add_custom_prefixes: dict = None,
) -> str:
    """Adds known prefixes to the query string.

    Args:
        query (str): The input query string.
        add_popular_prefixes (bool): Whether to add prefixes from prefix.cc.
        add_custom_prefixes (dict): A dictionary of custom prefixes to add.

    Returns:
        str: The query string with known prefixes added.
    """
    if add_custom_prefixes is None:
        add_custom_prefixes = {}

    popular_prefixes = {}
    if add_popular_prefixes:
        popular_prefixes_path = (
            Path(__file__).parent.parent / "data" / "popular_prefixes.json"
        )
        with open(popular_prefixes_path) as f:
            popular_prefixes = json.load(f)

    known_prefixes: dict = {**popular_prefixes, **add_custom_prefixes}

    prefix_declaration_pattern = re.compile(
        r"^\s*prefix\s+([A-Za-z_][\w.-]*):", re.IGNORECASE | re.MULTILINE
    )
    prefixed_name_pattern = re.compile(r"(?<![<\w.-])([A-Za-z_][\w.-]*):")

    declared_prefixes = {
        match.group(1) for match in prefix_declaration_pattern.finditer(query)
    }
    used_prefixes = {match.group(1) for match in prefixed_name_pattern.finditer(query)}

    prefixes_to_add = [
        f"PREFIX {prefix}: <{namespace}>"
        for prefix, namespace in known_prefixes.items()
        if prefix in used_prefixes and prefix not in declared_prefixes
    ]

    if not prefixes_to_add:
        return query

    return "\n".join(prefixes_to_add) + "\n" + query
