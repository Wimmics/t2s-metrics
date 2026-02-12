import re
from urllib.parse import unquote


def normalize_term(value: str) -> str:
    """
    Normalize a SPARQL result term.
    """
    if value is None:
        return ""

    value = value.strip()

    # Remove angle brackets
    if value.startswith("<") and value.endswith(">"):
        value = value[1:-1]

    # Normalize URI encoding
    value = unquote(value)

    # Lowercase for literals (URIs are case-sensitive but endpoints vary)
    if not value.startswith("http"):
        value = value.lower()

    # Remove datatype/language tags if present
    value = re.sub(r'\^\^.*$', '', value)
    value = re.sub(r'@.*$', '', value)

    return value
