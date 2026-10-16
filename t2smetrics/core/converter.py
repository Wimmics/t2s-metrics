"""This module provides functions to convert SPARQL answer set JSON and JSON-LD data into HTML tables and Label Studio JSON format, respectively."""

import json
from datetime import datetime

# Inline CSS style constants mirroring your TypeScript definitions
STYLES = {
    "tableBase": (
        "width: 100%; border-collapse: collapse; font-family: system-ui, -apple-system, "
        "sans-serif; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); "
        "background-color: #ffffff;"
    ),
    "generatedBorder": "border: 1px solid #e2e8f0;",
    "goldenBorder": "border: 1px solid #bbf7d0;",
    "generatedHeaderTr": "background-color: #f8fafc;",
    "goldenHeaderTr": "background-color: #f0fdf4;",
    "generatedTh": (
        "padding: 10px 14px; text-align: left; font-size: 12px; font-weight: 600; "
        "color: #475569; text-transform: uppercase; border-bottom: 2px solid #e2e8f0;"
    ),
    "goldenTh": (
        "padding: 10px 14px; text-align: left; font-size: 12px; font-weight: 600; "
        "color: #166534; text-transform: uppercase; border-bottom: 2px solid #bbf7d0;"
    ),
    "td": (
        "padding: 10px 14px; font-size: 13px; color: #1e293b; "
        "border-bottom: 1px solid #f1f5f9; word-break: break-all;"
    ),
}

LABEL_STUDIO_TEMPLATE = """
<View>
  <Style>
 .sparql-code-block-gold {
        border-left: 4px solid #166534;
    }
    .sparql-code-block-generated {
        border-left: 4px solid #475569;
    }

    .sparql-code-block {
        width: 100%;
        padding: 8px 8px;
        border-radius: 12px;
        font-family: "Courier New", Courier, monospace;
        font-size: 14px;
        line-height: 1.5;
        overflow-x: auto;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        white-space: pre-wrap;
        word-break: break-word;
    }
  </Style>
  <Header value="🔍 Text2SPARQL Benchmark Flagged Case Verification"/>
  <View>
    <Header value="Question ID"/>
    <Text name="question_id" value=" $question_id" />
    <Header value="Dataset"/>
    <Text name="dataset" value=" $dataset" />
    <Header value="System"/>
    <Text name="system" value="$system" />
    <Header value="Natural Language Question"/>
    <Text name="question" value="$question" />
    <Header value="Metrics"/>
    <Table name="metrics" value="$metrics"/>
  </View>
 
  <View style="display: flex; gap: 16px; margin:8px">
      <View className="sparql-code-block sparql-code-block-gold">
        <Header value="Expected SPARQL Query"/>
        <Text name="golden_sparql" value="$golden_sparql" />
      </View>
      <View className="sparql-code-block sparql-code-block-generated">        <Header value="Generated SPARQL Query"/>
        <Text name="generated_sparql" value="$generated_sparql" />
      </View>
  </View>
  
  <View style="display: flex; gap: 16px; margin:8px">
    <View style="width: 50%">
      <Header value="Expected ResultSet"/>
      <HyperText name="generated_answerset" value="$golden_answerset_html" />  
    </View>
    <View style="width: 50%">
      <Header value="Generated ResultSet "/>
      <HyperText name="golden_answerset" value="$generated_answerset_html" />
    </View>
  </View>
  
  
  <View style="margin-top: 20px; border-top: 2px solid #ccc; padding-top: 16px;">
    <Header value="Human Evaluator Decision"/>
    <Choices name="human_verification" toName="question" required="true">
      <Choice value="1" html="The golden query is wrong (it is completely incorrect)."/>
      <Choice value="2" html="The pair consisting of the NL question and the golden query is ambiguous."/>
      <Choice value="3" html="The F1 metric is unsuitable: it does not reflect the quality of the generated query."/>
      <Choice value="4" html="The golden query is taking a short cut e.g. using directly a URI instead of a additional triples."/>
      <Choice value="5" html="The error profiling tool should not have flagged this case."/>
      <Choice value="6" html="Ambiguous case (needs discussion)"/>
    </Choices>
  </View>
  
  
</View>
"""


def render_sparql_table(data: dict, is_golden: bool = False) -> str:
    """Renders SPARQL answer set JSON into an inline HTML table string."""
    if not data:
        return ""

    headers = data.get("head", {}).get("vars", [])
    bindings = data.get("results", {}).get("bindings", [])
    boolean_result = data.get("boolean")

    table_border = STYLES["goldenBorder"] if is_golden else STYLES["generatedBorder"]
    table_style = f"{STYLES['tableBase']} {table_border}"
    header_tr_style = (
        STYLES["goldenHeaderTr"] if is_golden else STYLES["generatedHeaderTr"]
    )
    th_style = STYLES["goldenTh"] if is_golden else STYLES["generatedTh"]

    if boolean_result is not None:
        # If the result is boolean, display it in a single cell
        return f'<table style="{table_style}"><thead><tr style="{header_tr_style}"><th style="{th_style}">Result</th></tr></thead><tbody><tr><td style="{STYLES["td"]}">{boolean_result}</td></tr></tbody></table>'

    # Build <thead>
    headers_html = "".join([f'<th style="{th_style}">{var}</th>' for var in headers])

    # Build <tbody>
    rows_list = []
    for row in bindings:
        cells = []
        for var in headers:
            val = row.get(var, {}).get("value", "")
            cells.append(f'<td style="{STYLES["td"]}">{val}</td>')
        rows_list.append(f"<tr>{''.join(cells)}</tr>")

    rows_html = "".join(rows_list)

    return f'<table style="{table_style}"><thead><tr style="{header_tr_style}">{headers_html}</tr></thead><tbody>{rows_html}</tbody></table>'


def transform_jsonld_to_labelstudio(jsonld_str: str) -> str:
    """Transforms JSON-LD string content to a Label Studio JSON string."""
    input_data = json.loads(jsonld_str)
    output_items = []

    # Get current timestamp in ISO format similar to sample
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    # Extract items array from JSON-LD
    items = input_data.get("items", []) if isinstance(input_data, dict) else input_data

    for item in items:
        target = item.get("target", {})
        body = item.get("body", {})

        # Extract question ID from target ID (urn:t2s:query:ck25:ck25:47-en -> ck25:47-en)
        # full_id = target.get("id", "")
        # question_id = full_id.split(":")[-2] if full_id else ""

        # Render HTML tables for SPARQL answer sets
        golden_html = render_sparql_table(
            target.get("golden_answerset"), is_golden=True
        )
        generated_html = render_sparql_table(
            target.get("generated_answerset"), is_golden=False
        )

        # Build Label Studio record object
        record = {
            "data": {
                "question_id": target.get("id", ""),
                "dataset": target.get("dataset", ""),
                "system": target.get("system", ""),
                "golden_sparql": target.get("golden_sparql", ""),
                "generated_sparql": target.get("generated_sparql", ""),
                "question": target.get("question", ""),
                "generated_answerset_html": generated_html,
                "golden_answerset_html": golden_html,
                "metrics": body.get("metrics", {}),
                "timestamp": timestamp,
            }
        }
        output_items.append(record)

    return json.dumps(output_items, indent=2)
