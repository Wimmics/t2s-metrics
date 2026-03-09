import json
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import os

# Get all json files in the results folder
available_files = [f for f in os.listdir("./res/results/") if f.endswith(".json")]

if not available_files:
    raise FileNotFoundError("No JSON files found in the results folder.")

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Metric categories (defined globally)
metric_categories = {
    "Answer Similarity": [
        "answerset_precision",
        "answerset_recall",
        "answerset_f1",
        "f1_qald",
        "precision_qald",
        "recall_qald",
    ],
    "Text Similarity": [
        "bleu",
        "codebleu",
        "meteor",
        "rouge_4",
        "sp-bleu",
        "qcan-bleu",
    ],
    "Ranking Metrics": ["p@1", "Hit@1", "mrr", "ndcg"],
    "Structural Metrics": [
        "sp-f1",
        "token_f1",
        "token_precision",
        "token_recall",
        "jaccard",
    ],
    "Distance Metrics": ["cosine_sim", "euclidean", "levenshtein"],
    "Execution Metrics": ["query_execution", "query_exact_match", "uri_hallucination"],
}

# App layout
app.layout = dbc.Container(
    [
        html.H1("QA System Evaluation Dashboard", className="text-center mb-4"),
        # File selector row
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Select JSON File:"),
                        dcc.Dropdown(
                            id="file-selector",
                            options=[{"label": f, "value": f} for f in available_files],
                            value=available_files[0],  # Default to first file
                            clearable=False,
                        ),
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        html.Label("File Info:"),
                        html.Div(id="file-info", className="text-muted"),
                    ],
                    width=8,
                ),
            ],
            className="mb-4",
        ),
        # Store components for the current data
        dcc.Store(id="systems-store"),
        dcc.Store(id="metrics-store"),
        dcc.Store(id="data-store"),
        # System and metric selectors
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Select Systems:"),
                        dcc.Dropdown(id="system-selector", multi=True),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        html.Label("Select Metric Category:"),
                        dcc.Dropdown(id="category-selector"),
                    ],
                    width=6,
                ),
            ],
            className="mb-4",
        ),
        # Tabs for different visualizations
        dcc.Tabs(
            [
                dcc.Tab(
                    label="Radar Chart",
                    children=[
                        dbc.Row([dbc.Col(dcc.Graph(id="radar-chart"), width=12)])
                    ],
                ),
                dcc.Tab(
                    label="Bar Chart",
                    children=[dbc.Row([dbc.Col(dcc.Graph(id="bar-chart"), width=12)])],
                ),
                dcc.Tab(
                    label="Heatmap",
                    children=[
                        dbc.Row([dbc.Col(html.Label("Select Metrics for Heatmap:"))]),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Dropdown(id="heatmap-metrics", multi=True),
                                    width=12,
                                )
                            ]
                        ),
                        dbc.Row([dbc.Col(dcc.Graph(id="heatmap"), width=12)]),
                    ],
                ),
            ]
        ),
    ],
    fluid=True,
)


# Callback to load data when file is selected
@app.callback(
    [
        Output("data-store", "data"),
        Output("systems-store", "data"),
        Output("metrics-store", "data"),
        Output("file-info", "children"),
        Output("system-selector", "options"),
        Output("system-selector", "value"),
        Output("category-selector", "options"),
        Output("category-selector", "value"),
    ],
    [Input("file-selector", "value")],
)
def load_data(selected_file):
    if not selected_file:
        return {}, {}, {}, "No file selected", [], [], [], None

    # Load the selected file
    file_path = f"./res/results/{selected_file}"
    with open(file_path, "r") as f:
        data = json.load(f)

    # Filter out empty metrics
    valid_data = [item for item in data if item.get("metrics")]

    if not valid_data:
        return {}, {}, {}, "No valid data in file", [], [], [], None

    # Extract system names and metrics
    systems = [item["system_name"] for item in valid_data]

    # Get all unique metrics
    all_metrics = set()
    for item in valid_data:
        all_metrics.update(item["metrics"].keys())
    all_metrics = sorted(list(all_metrics))

    # Create data matrix
    data_matrix = []
    for item in valid_data:
        row = []
        for metric in all_metrics:
            row.append(item["metrics"].get(metric, 0))
        data_matrix.append(row)

    # Store the data
    stored_data = {
        "systems": systems,
        "metrics": all_metrics,
        "data_matrix": data_matrix,
    }

    # Get available metrics for categories
    available_categories = {}
    for category, metrics_list in metric_categories.items():
        available_metrics = [m for m in metrics_list if m in all_metrics]
        if available_metrics:
            available_categories[category] = available_metrics

    # File info
    file_info = (
        f"File: {selected_file} | Systems: {len(systems)} | Metrics: {len(all_metrics)}"
    )

    # System options
    system_options = [{"label": sys, "value": sys} for sys in systems]

    # Category options
    category_options = [
        {"label": cat, "value": cat} for cat in available_categories.keys()
    ]

    return (
        stored_data,
        systems,
        all_metrics,
        file_info,
        system_options,
        systems,
        category_options,
        list(available_categories.keys())[0] if available_categories else None,
    )


# Helper function to convert stored data to DataFrame
def stored_data_to_df(stored_data):
    if not stored_data:
        return pd.DataFrame()

    df = pd.DataFrame(stored_data["data_matrix"], columns=stored_data["metrics"])
    df["system_name"] = stored_data["systems"]
    return df


# Callback to update heatmap metrics dropdown
@app.callback(Output("heatmap-metrics", "options"), [Input("metrics-store", "data")])
def update_heatmap_metrics(metrics):
    if not metrics:
        return []
    return [{"label": m, "value": m} for m in metrics]


# Callback to update radar and bar charts
@app.callback(
    [Output("radar-chart", "figure"), Output("bar-chart", "figure")],
    [
        Input("data-store", "data"),
        Input("system-selector", "value"),
        Input("category-selector", "value"),
    ],
)
def update_radar_and_bar(stored_data, selected_systems, selected_category):
    if not stored_data or not selected_systems or not selected_category:
        return go.Figure(), go.Figure()

    # Convert to DataFrame
    df = stored_data_to_df(stored_data)
    filtered_df = df[df["system_name"].isin(selected_systems)]

    # Get metrics for this category
    category_metrics = metric_categories.get(selected_category, [])
    # Filter to only metrics that exist in the data
    available_metrics = [m for m in category_metrics if m in filtered_df.columns]

    if not available_metrics:
        return go.Figure(), go.Figure()

    # Radar Chart
    fig_radar = go.Figure()
    for _, row in filtered_df.iterrows():
        fig_radar.add_trace(
            go.Scatterpolar(
                r=[row[m] for m in available_metrics],
                theta=available_metrics,
                fill="toself",
                name=row["system_name"],
            )
        )

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title=f"Radar Chart - {selected_category}",
        height=600,
    )

    # Bar Chart
    fig_bar = go.Figure()
    for metric in available_metrics:
        fig_bar.add_trace(
            go.Bar(
                name=metric,
                x=filtered_df["system_name"],
                y=filtered_df[metric],
                text=filtered_df[metric].round(3),
                textposition="auto",
            )
        )

    fig_bar.update_layout(
        title=f"Bar Chart Comparison - {selected_category}",
        barmode="group",
        height=600,
        xaxis_tickangle=-45,
    )

    return fig_radar, fig_bar


# Callback for heatmap
@app.callback(
    Output("heatmap", "figure"),
    [
        Input("data-store", "data"),
        Input("system-selector", "value"),
        Input("heatmap-metrics", "value"),
    ],
)
def update_heatmap(stored_data, selected_systems, selected_metrics):
    if (
        not stored_data
        or not selected_systems
        or not selected_metrics
        or len(selected_metrics) < 2
    ):
        return go.Figure()

    # Convert to DataFrame
    df = stored_data_to_df(stored_data)
    filtered_df = df[df["system_name"].isin(selected_systems)]

    # Calculate correlation matrix
    corr_matrix = filtered_df[selected_metrics].corr().round(2)

    fig = go.Figure(
        data=go.Heatmap(
            z=corr_matrix.values,
            x=selected_metrics,
            y=selected_metrics,
            colorscale="RdBu",
            zmin=-1,
            zmax=1,
            text=corr_matrix.values,
            texttemplate="%{text}",
            textfont={"size": 10},
        )
    )

    fig.update_layout(
        title="Metric Correlation Heatmap", height=700, xaxis_tickangle=-45
    )

    return fig


if __name__ == "__main__":
    app.run(debug=True, port=8050)
