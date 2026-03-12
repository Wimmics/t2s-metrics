import re
from urllib.parse import urljoin


def extract_uris(sparql: str) -> set[str]:
    base = None
    prefixes = {}

    # Normalize whitespace
    q = sparql.strip()

    # --- Extract BASE ---
    base_match = re.search(r"BASE\s*<([^>]+)>", q, re.IGNORECASE)
    if base_match:
        base = base_match.group(1)

    # --- Extract PREFIX declarations ---
    for pfx, uri in re.findall(r"PREFIX\s+(\w+):\s*<([^>]+)>", q, re.IGNORECASE):
        prefixes[pfx] = uri

    uris = set()

    # --- Extract <IRI> tokens ---
    for iri in re.findall(r"<([^>]+)>", q):
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", iri):
            # Already absolute
            uris.add(iri)
        elif base:
            # Relative IRI
            uris.add(urljoin(base, iri))

    # --- Extract prefixed names ---
    for pfx, local in re.findall(r"\b(\w+):([A-Za-z_][\w\-]*)", q):
        if pfx in prefixes and pfx != "xsd":  # Exclude xsd prefix
            uris.add(prefixes[pfx] + local)

    # --- Remove base and prefix declarations from consideration ---
    uris_cleaned = set()
    for uri in uris:
        if base and uri == base:
            continue
        if uri in prefixes.values():
            continue
        uris_cleaned.add(uri)

    return uris_cleaned
