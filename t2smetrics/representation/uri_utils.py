import re


def extract_uris(sparql: str) -> set[str]:
    """Extract URIs and resolved prefixed names from a SPARQL query."""
    if not sparql:
        return set()

    # 1. Map PREFIX declarations
    prefixes = dict(
        re.findall(r"PREFIX\s+([a-zA-Z_][\w-]*):\s*<([^>]+)>", sparql, re.IGNORECASE)
    )

    # 2. Tokenize SPARQL to ignore comments (#..., /*...*/) and strings ('...', "...")
    # Matches strings or comments as single tokens, or a single '<' character
    token_pattern = r'#.*|/\*[\s\S]*?\*/|\'(?:\\.|[^\'])*\'|"(?:\\.|[^"])*"|<'

    raw_uris = []
    clean_parts = []
    i = 0

    while i < len(sparql):
        match = re.search(token_pattern, sparql[i:])
        if not match:
            clean_parts.append(sparql[i:])
            break

        start_pos = i + match.start()
        clean_parts.append(sparql[i:start_pos])

        # If we hit an unquoted/uncommented '<', scan forward for balanced closing '>'
        if match.group(0) == "<":
            depth = 1
            j = start_pos + 1
            while j < len(sparql) and depth > 0:
                if sparql[j] == "\n":  # Malformed URI break
                    break
                if sparql[j] == "<":
                    depth += 1
                elif sparql[j] == ">":
                    depth -= 1
                j += 1

            if depth == 0:
                uri = sparql[start_pos + 1 : j - 1]
                raw_uris.append(uri)
                clean_parts.append(sparql[start_pos:j])
                i = j
                continue

        # Skip over matched comment or string
        i = i + match.end()

    clean = "".join(clean_parts)

    # 3. Filter out prefix target declarations
    decl_uris = set(prefixes.values()) | {u.rstrip("/") for u in prefixes.values()}
    uris = {u.strip() for u in raw_uris if u.strip() and u.strip() not in decl_uris}

    # 4. Extract and resolve prefixed names
    keywords = {
        "prefix",
        "select",
        "where",
        "from",
        "limit",
        "offset",
        "order",
        "by",
        "group",
        "having",
        "values",
        "union",
        "optional",
        "filter",
        "bind",
        "http",
        "https",
        "ftp",
        "urn",
        "mailto",
    }

    for prefix, local in re.findall(r"\b([a-zA-Z_][\w-]*):([\w\-\.%]+)\b", clean):
        if prefix.lower() in keywords:
            continue

        full_prefixed = f"{prefix}:{local}"
        if any(full_prefixed in u for u in uris):
            continue

        uris.add(f"{prefixes[prefix]}{local}" if prefix in prefixes else full_prefixed)

    return uris
