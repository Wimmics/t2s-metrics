import re

from regex import Pattern

TOKEN_PATTERN_V1 = re.compile(
    r"""
    [A-Za-z_][A-Za-z0-9_]*   # identifiers
  | \?[A-Za-z_][A-Za-z0-9_]* # variables
  | <[^>]*>                 # IRIs
  | "[^"]*"                 # strings
  | [{}();.,]               # punctuation
""",
    re.VERBOSE,
)

TOKEN_PATTERN_V2 = re.compile(
    r"""
    \?[A-Za-z_][A-Za-z0-9_]*                      # variables
  | <[^>]*>                                        # IRIs
  | "(?:\\.|[^"\\])*"                              # strings with escapes
  | [-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?            # numbers
  | [A-Za-z_][A-Za-z0-9_]*:[A-Za-z0-9_]+           # prefixed names
  | !=|<=|>=|&&|\|\||[=<>+\-*/]                    # operators
  | [{}\[\]();.,]                                  # punctuation
  | [A-Za-z_][A-Za-z0-9_]*                         # identifiers / keywords
""",
    re.VERBOSE,
)


def tokenize(sparql: str, pattern: Pattern[str] = TOKEN_PATTERN_V2) -> list[str]:
    return pattern.findall(sparql)
