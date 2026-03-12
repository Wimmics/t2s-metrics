import json
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px


parent_folder = Path("datasets")

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


def _build_layout(available_files):
    """Build the app layout with the given list of available JSON files."""
    return dbc.Container(
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
                                options=[
                                    {"label": f, "value": f} for f in available_files
                                ],
                                # value=available_files[0],  # Default to first file
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
                    # Tab 1: Radar Chart
                    dcc.Tab(
                        label="Radar Chart",
                        children=[
                            dbc.Row([dbc.Col(dcc.Graph(id="radar-chart"), width=12)])
                        ],
                    ),
                    # Tab 2: Bar Chart Comparison
                    dcc.Tab(
                        label="Bar Chart",
                        children=[
                            dbc.Row([dbc.Col(dcc.Graph(id="bar-chart"), width=12)])
                        ],
                    ),
                    # Tab 3: Heatmap
                    dcc.Tab(
                        label="Correlation Heatmap",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Label(
                                            "Select Metrics for Correlation Heatmap:"
                                        )
                                    )
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Dropdown(id="heatmap-metrics", multi=True),
                                        width=12,
                                    )
                                ]
                            ),
                            dbc.Row(
                                [dbc.Col(dcc.Graph(id="correlation-heatmap"), width=12)]
                            ),
                        ],
                    ),
                    # Tab 4: Parallel Coordinates
                    dcc.Tab(
                        label="Parallel Coordinates",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Label(
                                            "Select Metrics for Parallel Coordinates:"
                                        )
                                    )
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id="parallel-coords-metrics", multi=True
                                        ),
                                        width=12,
                                    )
                                ]
                            ),
                            dbc.Row(
                                [dbc.Col(dcc.Graph(id="parallel-coords"), width=12)]
                            ),
                        ],
                    ),
                    # Tab 5: Scatter Matrix
                    dcc.Tab(
                        label="Scatter Matrix",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Label("Select Metrics for Scatter Matrix:")
                                    )
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Dropdown(id="scatter-metrics", multi=True),
                                        width=12,
                                    )
                                ]
                            ),
                            dbc.Row(
                                [dbc.Col(dcc.Graph(id="scatter-matrix"), width=12)]
                            ),
                        ],
                    ),
                ]
            ),
        ],
        fluid=True,
    )


app.layout = _build_layout([])


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
    with open(selected_file, "r") as f:
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


# Callback to update parallel coordinates metrics dropdown
@app.callback(
    Output("parallel-coords-metrics", "options"), [Input("metrics-store", "data")]
)
def update_parallel_coords_metrics(metrics):
    if not metrics:
        return []
    return [{"label": m, "value": m} for m in metrics]


# Callback to update parallel coordinates metrics dropdown
@app.callback(Output("scatter-metrics", "options"), [Input("metrics-store", "data")])
def update_scatter_metrics(metrics):
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


@app.callback(
    Output("correlation-heatmap", "figure"),
    [
        Input("data-store", "data"),
        Input("heatmap-metrics", "value"),
        Input("system-selector", "value"),
    ],
)
def update_heatmap(stored_data, selected_metrics, selected_systems):
    if not stored_data or not selected_systems:
        return go.Figure(), go.Figure()

    # Convert to DataFrame
    df = stored_data_to_df(stored_data)
    filtered_df = df[df["system_name"].isin(selected_systems)]

    if not selected_metrics or len(selected_metrics) < 2:
        return go.Figure()

    try:
        # Calculate correlation matrix
        corr_matrix = filtered_df[selected_metrics].corr().round(2)
        corr_matrix = corr_matrix.fillna(0)

        fig = go.Figure(
            data=go.Heatmap(
                z=corr_matrix.values,
                x=selected_metrics,
                y=selected_metrics,
                colorscale="turbo",
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

    except Exception as e:
        print("Error generating heatmap:", e)
        return go.Figure()


@app.callback(
    Output("parallel-coords", "figure"),
    [
        Input("data-store", "data"),
        Input("parallel-coords-metrics", "value"),
        Input("system-selector", "value"),
    ],
)
def update_parallel(stored_data, selected_metrics, selected_systems):
    if not stored_data or not selected_systems:
        return go.Figure(), go.Figure()

    # Convert to DataFrame
    df = stored_data_to_df(stored_data)
    filtered_df = df[df["system_name"].isin(selected_systems)]

    if not selected_metrics or len(selected_metrics) < 2:
        return go.Figure()

    try:

        dimensions = []
        for metric in selected_metrics:
            dimensions.append(
                dict(
                    label=metric,
                    values=filtered_df[metric],
                    range=[filtered_df[metric].min(), filtered_df[metric].max()],
                )
            )

        fig = go.Figure(
            data=go.Parcoords(
                line=dict(color=filtered_df.index, colorscale="Viridis"),
                dimensions=dimensions,
            )
        )

        fig.update_layout(title="Parallel Coordinates Plot", height=600)

        return fig

    except Exception as e:
        print("Error generating heatmap:", e)
        return go.Figure()


@app.callback(
    Output("scatter-matrix", "figure"),
    [
        Input("data-store", "data"),
        Input("scatter-metrics", "value"),
        Input("system-selector", "value"),
    ],
)
def update_scatter_matrix(stored_data, selected_metrics, selected_systems):
    if not stored_data or not selected_systems:
        return go.Figure(), go.Figure()

    # Convert to DataFrame
    df = stored_data_to_df(stored_data)
    filtered_df = df[df["system_name"].isin(selected_systems)]

    if not selected_metrics or len(selected_metrics) < 2:
        return go.Figure()

    try:
        filtered_df = df[df["system_name"].isin(selected_systems)]

        if len(selected_metrics) < 2:
            return go.Figure()

        fig = px.scatter_matrix(
            filtered_df,
            dimensions=selected_metrics,
            color="system_name",
            title="Scatter Matrix",
        )

        fig.update_layout(height=800)
        fig.update_traces(diagonal_visible=False)

        return fig
    except Exception as e:
        print("Error generating heatmap:", e)
        return go.Figure()


def run(available_files=None):
    if available_files is None:
        available_files = [str(f) for f in parent_folder.glob("*/results/*.json")]
        if not available_files:
            raise FileNotFoundError("No JSON files found in the results folder.")
    for f in available_files:
        if not Path(f).is_file():
            raise FileNotFoundError(f"The path does not exist or is not a file: {f}")
        elif not f.endswith(".json"):
            raise ValueError(f"Invalid file type (expected .json): {f}")
    app.layout = _build_layout(available_files)
    app.run(debug=True, port=8050)


if __name__ == "__main__":
    run()
