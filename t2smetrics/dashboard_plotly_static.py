"""Static Plotly dashboard generator with native HTML/CSS/JS callbacks."""

import json
from pathlib import Path

from loguru import logger

parent_folder = Path("datasets")

# Metric categories (kept aligned with the Dash dashboard)
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


def _validate_and_resolve_files(available_files):
    """Resolve and validate dashboard input files."""
    if available_files is None:
        available_files = [str(f) for f in parent_folder.glob("*/results/*.json")]
        if not available_files:
            raise FileNotFoundError("No JSON files found in datasets/*/results/.")

    resolved = []
    for file_path in available_files:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(
                f"The path does not exist or is not a file: {file_path}"
            )
        if path.suffix.lower() != ".json":
            raise ValueError(f"Invalid file type (expected .json): {file_path}")
        resolved.append(path.resolve())
    return resolved


def _load_dataset_payload(files):
    """Load all selected files in a compact JSON payload for client-side rendering."""
    datasets_payload = {}

    for path in files:
        with path.open("r", encoding="utf-8") as stream:
            raw_data = json.load(stream)

        valid_data = [
            item
            for item in raw_data
            if isinstance(item, dict)
            and item.get("system_name")
            and isinstance(item.get("metrics"), dict)
            and item.get("metrics")
        ]

        systems = [item["system_name"] for item in valid_data]

        all_metrics = set()
        for item in valid_data:
            all_metrics.update(item["metrics"].keys())
        all_metrics = sorted(all_metrics)

        data_matrix = []
        for item in valid_data:
            data_matrix.append(
                [item["metrics"].get(metric, 0) for metric in all_metrics]
            )

        available_categories = {}
        for category, metrics in metric_categories.items():
            category_metrics = [metric for metric in metrics if metric in all_metrics]
            if category_metrics:
                available_categories[category] = category_metrics

        datasets_payload[str(path)] = {
            "file": str(path),
            "systems": systems,
            "metrics": all_metrics,
            "dataMatrix": data_matrix,
            "availableCategories": available_categories,
        }

    return {
        "metricCategories": metric_categories,
        "datasets": datasets_payload,
    }


def _build_html(data_payload):
    """Create the static dashboard HTML shell."""
    data_json = json.dumps(data_payload, ensure_ascii=True).replace("</", "<\\/")

    return f"""<!doctype html>
<html lang=\"en\">
<head>
	<meta charset=\"utf-8\" />
	<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
	<title>Text2SPARQL Metrics Evaluation Dashboard</title>
	<script src=\"https://cdn.plot.ly/plotly-2.35.2.min.js\"></script>
	<style>
		:root {{
			--bg: #f4f7fb;
			--panel: #ffffff;
			--ink: #10223b;
			--muted: #54657d;
			--accent: #0866c6;
			--accent-soft: #deecff;
			--border: #dce5f0;
			--radius: 12px;
			--shadow: 0 8px 22px rgba(16, 34, 59, 0.08);
		}}

		* {{ box-sizing: border-box; }}

		body {{
			margin: 0;
			font-family: "Segoe UI", "Noto Sans", sans-serif;
			color: var(--ink);
			background:
				radial-gradient(circle at 90% 0%, #d8e9ff 0, transparent 48%),
				linear-gradient(180deg, #fbfdff 0%, var(--bg) 100%);
			min-height: 100vh;
		}}

		.container {{
			width: min(1320px, 95vw);
			margin: 24px auto 40px;
		}}

		h1 {{
			margin: 0 0 14px;
			text-align: center;
			letter-spacing: 0.2px;
			font-size: clamp(1.35rem, 2vw, 2rem);
		}}

		.toolbar {{
			display: grid;
			grid-template-columns: repeat(12, 1fr);
			gap: 14px;
			background: var(--panel);
			border: 1px solid var(--border);
			border-radius: var(--radius);
			padding: 14px;
			box-shadow: var(--shadow);
			margin-bottom: 14px;
		}}

		.control {{
			display: flex;
			flex-direction: column;
			gap: 6px;
		}}

		.control.file {{ grid-column: span 4; }}
		.control.info {{ grid-column: span 8; }}

		label {{
			font-size: 0.86rem;
			color: var(--muted);
			font-weight: 600;
			letter-spacing: 0.2px;
		}}

		select {{
			border: 1px solid var(--border);
			border-radius: 10px;
			padding: 8px 10px;
			min-height: 40px;
			background: #fff;
			color: var(--ink);
		}}

		select[multiple] {{ min-height: 132px; }}

		.checkbox-list {{
			border: 1px solid var(--border);
			border-radius: 10px;
			padding: 8px 10px;
			background: #fff;
			min-height: 132px;
			max-height: 240px;
			overflow: auto;
			display: grid;
			grid-template-columns: 1fr;
			gap: 6px;
		}}

		.checkbox-item {{
			display: flex;
			align-items: center;
			gap: 8px;
			font-size: 0.92rem;
			line-height: 1.2;
		}}

		.checkbox-item input {{
			margin: 0;
			accent-color: var(--accent);
		}}

		.list-actions {{
			display: flex;
			gap: 8px;
			margin: 2px 0 6px;
		}}

		.action-btn {{
			border: 1px solid var(--border);
			background: #fff;
			color: var(--ink);
			border-radius: 999px;
			padding: 4px 10px;
			font-size: 0.78rem;
			font-weight: 600;
			cursor: pointer;
		}}

		.action-btn:hover {{
			background: var(--accent-soft);
			border-color: #b9d5fb;
			color: var(--accent);
		}}

		.action-btn:disabled {{
			opacity: 0.45;
			cursor: not-allowed;
		}}

		.info-text {{
			min-height: 40px;
			display: flex;
			align-items: center;
			border: 1px dashed var(--border);
			border-radius: 10px;
			padding: 8px 10px;
			color: var(--muted);
			background: #fbfdff;
			font-size: 0.92rem;
		}}

		.selectors {{
			display: grid;
			grid-template-columns: repeat(12, 1fr);
			gap: 14px;
			background: var(--panel);
			border: 1px solid var(--border);
			border-radius: var(--radius);
			box-shadow: var(--shadow);
			padding: 14px;
			margin-bottom: 14px;
		}}

		.selectors .control {{ grid-column: span 6; }}

		.tabs {{
			display: flex;
			gap: 8px;
			flex-wrap: wrap;
			margin-bottom: 10px;
		}}

		.tab-button {{
			border: 1px solid var(--border);
			background: #fff;
			color: var(--ink);
			border-radius: 999px;
			padding: 8px 14px;
			font-weight: 600;
			cursor: pointer;
			transition: all 0.18s ease;
		}}

		.tab-button.active {{
			background: var(--accent-soft);
			border-color: #b9d5fb;
			color: var(--accent);
		}}

		.tab-button:disabled {{
			opacity: 0.45;
			cursor: not-allowed;
		}}

		.tab-content {{
			display: none;
			background: var(--panel);
			border: 1px solid var(--border);
			border-radius: var(--radius);
			box-shadow: var(--shadow);
			padding: 10px;
		}}

		.tab-content.active {{ display: block; }}

		.sub-controls {{
			padding: 8px;
			margin-bottom: 8px;
		}}

		.chart {{ width: 100%; min-height: 620px; }}

		@media (max-width: 960px) {{
			.control.file, .control.info, .selectors .control {{
				grid-column: span 12;
			}}

			.chart {{ min-height: 500px; }}
		}}
	</style>
</head>
<body>
	<div class=\"container\">
		<h1>Text2SPARQL Metrics Evaluation Dashboard</h1>

		<section class=\"toolbar\">
			<div class=\"control file\">
				<label for=\"file-selector\">Select JSON File</label>
				<select id=\"file-selector\"></select>
			</div>
			<div class=\"control info\">
				<label>File Info</label>
				<div id=\"file-info\" class=\"info-text\">No file selected</div>
			</div>
		</section>

		<section class=\"selectors\">
			<div class=\"control\">
				<label for=\"system-selector\">Select Systems</label>
				<div class=\"list-actions\">
					<button id=\"systems-select-all\" type=\"button\" class=\"action-btn\">Select all</button>
					<button id=\"systems-clear\" type=\"button\" class=\"action-btn\">Clear all</button>
				</div>
				<div id=\"system-selector\" class=\"checkbox-list\"></div>
			</div>
			<div class=\"control\">
				<label for=\"category-selector\">Select Metric Category</label>
				<select id=\"category-selector\"></select>
			</div>
		</section>

		<div class=\"tabs\">
			<button class=\"tab-button active\" data-tab=\"radar\">Radar Chart</button>
			<button class=\"tab-button\" data-tab=\"bar\">Bar Chart</button>
			<button class=\"tab-button\" data-tab=\"heatmap\">Correlation Heatmap</button>
			<button class=\"tab-button\" data-tab=\"parallel\">Parallel Coordinates</button>
			<button class=\"tab-button\" data-tab=\"scatter\">Scatter Matrix</button>
		</div>

		<section id=\"tab-radar\" class=\"tab-content active\">
			<div id=\"radar-chart\" class=\"chart\"></div>
		</section>

		<section id=\"tab-bar\" class=\"tab-content\">
			<div id=\"bar-chart\" class=\"chart\"></div>
		</section>

		<section id=\"tab-heatmap\" class=\"tab-content\">
			<div class=\"sub-controls control\">
				<label for=\"heatmap-metrics\">Select Metrics for Correlation Heatmap</label>
				<div class=\"list-actions\">
					<button id=\"heatmap-select-all\" type=\"button\" class=\"action-btn\">Select all</button>
					<button id=\"heatmap-clear\" type=\"button\" class=\"action-btn\">Clear all</button>
				</div>
				<div id=\"heatmap-metrics\" class=\"checkbox-list\"></div>
			</div>
			<div id=\"correlation-heatmap\" class=\"chart\"></div>
		</section>

		<section id=\"tab-parallel\" class=\"tab-content\">
			<div class=\"sub-controls control\">
				<label for=\"parallel-metrics\">Select Metrics for Parallel Coordinates</label>
				<div class=\"list-actions\">
					<button id=\"parallel-select-all\" type=\"button\" class=\"action-btn\">Select all</button>
					<button id=\"parallel-clear\" type=\"button\" class=\"action-btn\">Clear all</button>
				</div>
				<div id=\"parallel-metrics\" class=\"checkbox-list\"></div>
			</div>
			<div id=\"parallel-coords\" class=\"chart\"></div>
		</section>

		<section id=\"tab-scatter\" class=\"tab-content\">
			<div class=\"sub-controls control\">
				<label for=\"scatter-metrics\">Select Metrics for Scatter Matrix</label>
				<div class=\"list-actions\">
					<button id=\"scatter-select-all\" type=\"button\" class=\"action-btn\">Select all</button>
					<button id=\"scatter-clear\" type=\"button\" class=\"action-btn\">Clear all</button>
				</div>
				<div id=\"scatter-metrics\" class=\"checkbox-list\"></div>
			</div>
			<div id=\"scatter-matrix\" class=\"chart\"></div>
		</section>
	</div>

	<script>
		window.__T2S_DASHBOARD_DATA__ = {data_json};
	</script>
	<script src=\"dashboard.js\"></script>
</body>
</html>
"""


def _build_js():
    """Create client-side callback logic using native JS + Plotly.js."""
    return """(function () {
	const appData = window.__T2S_DASHBOARD_DATA__ || { datasets: {} };

	const refs = {
		fileSelector: document.getElementById('file-selector'),
		fileInfo: document.getElementById('file-info'),
		systemSelector: document.getElementById('system-selector'),
		systemsSelectAll: document.getElementById('systems-select-all'),
		systemsClear: document.getElementById('systems-clear'),
		categorySelector: document.getElementById('category-selector'),
		heatmapMetrics: document.getElementById('heatmap-metrics'),
		heatmapSelectAll: document.getElementById('heatmap-select-all'),
		heatmapClear: document.getElementById('heatmap-clear'),
		parallelMetrics: document.getElementById('parallel-metrics'),
		parallelSelectAll: document.getElementById('parallel-select-all'),
		parallelClear: document.getElementById('parallel-clear'),
		scatterMetrics: document.getElementById('scatter-metrics'),
		scatterSelectAll: document.getElementById('scatter-select-all'),
		scatterClear: document.getElementById('scatter-clear'),
		radarChart: document.getElementById('radar-chart'),
		barChart: document.getElementById('bar-chart'),
		heatmapChart: document.getElementById('correlation-heatmap'),
		parallelChart: document.getElementById('parallel-coords'),
		scatterChart: document.getElementById('scatter-matrix'),
		tabButtons: Array.from(document.querySelectorAll('.tab-button')),
		tabPanels: Array.from(document.querySelectorAll('.tab-content')),
	};

	const state = {
		file: null,
		selectedSystems: [],
		selectedCategory: null,
		selectedHeatmapMetrics: [],
		selectedParallelMetrics: [],
		selectedScatterMetrics: [],
	};

	const plotConfig = { responsive: true, displaylogo: false };

	function checkedValues(containerEl) {
		return Array.from(containerEl.querySelectorAll('input[type="checkbox"]:checked')).map((input) => input.value);
	}

	function setSelectOptions(selectEl, values, selected) {
		const selectedSet = new Set(selected || []);
		selectEl.innerHTML = '';

		values.forEach((value) => {
			const option = document.createElement('option');
			option.value = value;
			option.textContent = value;
			option.selected = selectedSet.has(value);
			selectEl.appendChild(option);
		});
	}

	function setCheckboxOptions(containerEl, values, selected, groupName) {
		const selectedSet = new Set(selected || []);
		containerEl.innerHTML = '';

		values.forEach((value, idx) => {
			const label = document.createElement('label');
			label.className = 'checkbox-item';

			const checkbox = document.createElement('input');
			checkbox.type = 'checkbox';
			checkbox.name = groupName;
			checkbox.id = `${groupName}-${idx}`;
			checkbox.value = value;
			checkbox.checked = selectedSet.has(value);

			const text = document.createElement('span');
			text.textContent = value;

			label.appendChild(checkbox);
			label.appendChild(text);
			containerEl.appendChild(label);
		});
	}

	function setAllChecked(containerEl, checked) {
		containerEl.querySelectorAll('input[type="checkbox"]').forEach((input) => {
			input.checked = checked;
		});
	}

	function msgFigure(message) {
		return {
			data: [],
			layout: {
				annotations: [{
					text: message,
					x: 0.5,
					y: 0.5,
					xref: 'paper',
					yref: 'paper',
					showarrow: false,
					font: { size: 16 },
				}],
				xaxis: { visible: false },
				yaxis: { visible: false },
			},
		};
	}

	function currentDataset() {
		return appData.datasets[state.file] || null;
	}

	function rowsForSelection(data) {
		const metricIndex = new Map(data.metrics.map((metric, idx) => [metric, idx]));
		const systemsSet = new Set(state.selectedSystems);
		const rows = [];

		data.systems.forEach((systemName, rowIndex) => {
			if (!systemsSet.has(systemName)) {
				return;
			}
			const vector = data.dataMatrix[rowIndex];
			const row = { system_name: systemName };
			data.metrics.forEach((metric) => {
				row[metric] = Number(vector[metricIndex.get(metric)] || 0);
			});
			rows.push(row);
		});
		return rows;
	}

	function ensureRange(minVal, maxVal) {
		if (!Number.isFinite(minVal) || !Number.isFinite(maxVal)) {
			return [0, 1];
		}
		if (minVal === maxVal) {
			const delta = minVal === 0 ? 0.5 : Math.abs(minVal) * 0.1;
			return [minVal - delta, maxVal + delta];
		}
		return [minVal, maxVal];
	}

	function pearson(xs, ys) {
		const n = Math.min(xs.length, ys.length);
		if (n < 2) {
			return 0;
		}

		let sx = 0;
		let sy = 0;
		for (let i = 0; i < n; i += 1) {
			sx += xs[i];
			sy += ys[i];
		}
		const mx = sx / n;
		const my = sy / n;

		let num = 0;
		let dx2 = 0;
		let dy2 = 0;

		for (let i = 0; i < n; i += 1) {
			const dx = xs[i] - mx;
			const dy = ys[i] - my;
			num += dx * dy;
			dx2 += dx * dx;
			dy2 += dy * dy;
		}

		const den = Math.sqrt(dx2 * dy2);
		if (den === 0) {
			return 0;
		}
		return num / den;
	}

	function renderRadarAndBar() {
		const data = currentDataset();
		if (!data || !state.selectedCategory || state.selectedSystems.length === 0) {
			Plotly.react(refs.radarChart, msgFigure('No data selected').data, msgFigure('No data selected').layout, plotConfig);
			Plotly.react(refs.barChart, msgFigure('No data selected').data, msgFigure('No data selected').layout, plotConfig);
			return;
		}

		const categoryMetrics = data.availableCategories[state.selectedCategory] || [];
		const rows = rowsForSelection(data);

		if (categoryMetrics.length === 0 || rows.length === 0) {
			Plotly.react(refs.radarChart, msgFigure('No matching metrics found').data, msgFigure('No matching metrics found').layout, plotConfig);
			Plotly.react(refs.barChart, msgFigure('No matching metrics found').data, msgFigure('No matching metrics found').layout, plotConfig);
			return;
		}

		const radarData = rows.map((row) => ({
			type: 'scatterpolar',
			r: categoryMetrics.map((metric) => row[metric]),
			theta: categoryMetrics,
			fill: 'toself',
			name: row.system_name,
		}));

		Plotly.react(
			refs.radarChart,
			radarData,
			{
				title: `Radar Chart - ${state.selectedCategory}`,
				height: 600,
				polar: { radialaxis: { visible: true, range: [0, 1] } },
			},
			plotConfig,
		);

		const barData = categoryMetrics.map((metric) => ({
			type: 'bar',
			name: metric,
			x: rows.map((row) => row.system_name),
			y: rows.map((row) => row[metric]),
			text: rows.map((row) => Number(row[metric] || 0).toFixed(3)),
			textposition: 'auto',
		}));

		Plotly.react(
			refs.barChart,
			barData,
			{
				title: `Bar Chart Comparison - ${state.selectedCategory}`,
				barmode: 'group',
				height: 600,
				xaxis: { tickangle: -45 },
			},
			plotConfig,
		);
	}

	function renderHeatmap() {
		const data = currentDataset();
		if (!data) {
			Plotly.react(refs.heatmapChart, msgFigure('No data selected').data, msgFigure('No data selected').layout, plotConfig);
			return;
		}

		if (state.selectedSystems.length < 2 || state.selectedHeatmapMetrics.length < 2) {
			Plotly.react(refs.heatmapChart, msgFigure('Select at least 2 systems and 2 metrics').data, msgFigure('Select at least 2 systems and 2 metrics').layout, plotConfig);
			return;
		}

		const rows = rowsForSelection(data);
		const metrics = state.selectedHeatmapMetrics;

		const columns = metrics.map((metric) => rows.map((row) => Number(row[metric] || 0)));
		const corr = metrics.map((_, i) => metrics.map((__, j) => {
			const value = pearson(columns[i], columns[j]);
			return Number(value.toFixed(2));
		}));

		Plotly.react(
			refs.heatmapChart,
			[{
				type: 'heatmap',
				z: corr,
				x: metrics,
				y: metrics,
				colorscale: 'Turbo',
				zmin: -1,
				zmax: 1,
				text: corr,
				texttemplate: '%{text}',
				textfont: { size: 10 },
			}],
			{
				title: 'Metric Correlation Heatmap',
				height: 700,
				xaxis: { tickangle: -45 },
			},
			plotConfig,
		);
	}

	function renderParallel() {
		const data = currentDataset();
		if (!data) {
			Plotly.react(refs.parallelChart, msgFigure('No data selected').data, msgFigure('No data selected').layout, plotConfig);
			return;
		}

		if (state.selectedSystems.length < 2 || state.selectedParallelMetrics.length < 2) {
			Plotly.react(refs.parallelChart, msgFigure('Select at least 2 systems and 2 metrics').data, msgFigure('Select at least 2 systems and 2 metrics').layout, plotConfig);
			return;
		}

		const rows = rowsForSelection(data);
		const metrics = state.selectedParallelMetrics;
		const dimensions = metrics.map((metric) => {
			const vals = rows.map((row) => Number(row[metric] || 0));
			return {
				label: metric,
				values: vals,
				range: ensureRange(Math.min(...vals), Math.max(...vals)),
			};
		});

		Plotly.react(
			refs.parallelChart,
			[{
				type: 'parcoords',
				line: { color: rows.map((_, idx) => idx), colorscale: 'Viridis' },
				dimensions,
			}],
			{
				title: 'Parallel Coordinates Plot',
				height: 600,
			},
			plotConfig,
		);
	}

	function renderScatterMatrix() {
		const data = currentDataset();
		if (!data) {
			Plotly.react(refs.scatterChart, msgFigure('No data selected').data, msgFigure('No data selected').layout, plotConfig);
			return;
		}

		if (
			state.selectedSystems.length < 2 ||
			state.selectedScatterMetrics.length < 2 ||
			state.selectedScatterMetrics.length > 5
		) {
			Plotly.react(refs.scatterChart, msgFigure('Select at least 2 systems and 2 metrics (max 5 for readability)').data, msgFigure('Select at least 2 systems and 2 metrics (max 5 for readability)').layout, plotConfig);
			return;
		}

		const rows = rowsForSelection(data);
		const metrics = state.selectedScatterMetrics;

		const trace = {
			type: 'splom',
			dimensions: metrics.map((metric) => ({
				label: metric,
				values: rows.map((row) => Number(row[metric] || 0)),
			})),
			text: rows.map((row) => row.system_name),
			marker: {
				color: rows.map((_, idx) => idx),
				colorscale: 'Viridis',
				size: 8,
				opacity: 0.8,
			},
			diagonal: { visible: false },
			hovertemplate: '%{text}<extra></extra>',
		};

		Plotly.react(
			refs.scatterChart,
			[trace],
			{
				title: 'Scatter Matrix',
				height: 800,
			},
			plotConfig,
		);
	}

	function renderAll() {
		renderRadarAndBar();
		renderHeatmap();
		renderParallel();
		renderScatterMatrix();
	}

	function setAdvancedTabState(disabled) {
		refs.tabButtons.forEach((button) => {
			const tab = button.dataset.tab;
			if (tab === 'heatmap' || tab === 'parallel' || tab === 'scatter') {
				button.disabled = disabled;
			}
		});
	}

	function switchTab(tabName) {
		refs.tabButtons.forEach((button) => {
			button.classList.toggle('active', button.dataset.tab === tabName);
		});

		refs.tabPanels.forEach((panel) => {
			panel.classList.toggle('active', panel.id === `tab-${tabName}`);
		});
	}

	function onFileChanged() {
		state.file = refs.fileSelector.value;
		const data = currentDataset();

		if (!data) {
			refs.fileInfo.textContent = 'No file selected';
			return;
		}

		refs.fileInfo.textContent = `File: ${data.file} | Systems: ${data.systems.length} | Metrics: ${data.metrics.length}`;

		setCheckboxOptions(refs.systemSelector, data.systems, data.systems, 'systems');
		state.selectedSystems = [...data.systems];

		const categories = Object.keys(data.availableCategories);
		setSelectOptions(refs.categorySelector, categories, categories.length ? [categories[0]] : []);
		state.selectedCategory = categories.length ? categories[0] : null;

		setCheckboxOptions(refs.heatmapMetrics, data.metrics, [], 'heatmap-metrics');
		state.selectedHeatmapMetrics = [];
		setCheckboxOptions(refs.parallelMetrics, data.metrics, [], 'parallel-metrics');
		state.selectedParallelMetrics = [];
		setCheckboxOptions(refs.scatterMetrics, data.metrics, [], 'scatter-metrics');
		state.selectedScatterMetrics = [];

		setAdvancedTabState(data.systems.length < 2);
		renderAll();
	}

	function init() {
		const files = Object.keys(appData.datasets || {});

		if (!files.length) {
			refs.fileInfo.textContent = 'No datasets found';
			renderAll();
			return;
		}

		setSelectOptions(refs.fileSelector, files, [files[0]]);
		state.file = files[0];

		refs.fileSelector.addEventListener('change', onFileChanged);
		refs.systemSelector.addEventListener('change', () => {
			state.selectedSystems = checkedValues(refs.systemSelector);
			renderAll();
		});
		refs.systemsSelectAll.addEventListener('click', () => {
			setAllChecked(refs.systemSelector, true);
			state.selectedSystems = checkedValues(refs.systemSelector);
			renderAll();
		});
		refs.systemsClear.addEventListener('click', () => {
			setAllChecked(refs.systemSelector, false);
			state.selectedSystems = checkedValues(refs.systemSelector);
			renderAll();
		});
		refs.categorySelector.addEventListener('change', () => {
			state.selectedCategory = refs.categorySelector.value || null;
			renderRadarAndBar();
		});
		refs.heatmapMetrics.addEventListener('change', () => {
			state.selectedHeatmapMetrics = checkedValues(refs.heatmapMetrics);
			renderHeatmap();
		});
		refs.heatmapSelectAll.addEventListener('click', () => {
			setAllChecked(refs.heatmapMetrics, true);
			state.selectedHeatmapMetrics = checkedValues(refs.heatmapMetrics);
			renderHeatmap();
		});
		refs.heatmapClear.addEventListener('click', () => {
			setAllChecked(refs.heatmapMetrics, false);
			state.selectedHeatmapMetrics = checkedValues(refs.heatmapMetrics);
			renderHeatmap();
		});
		refs.parallelMetrics.addEventListener('change', () => {
			state.selectedParallelMetrics = checkedValues(refs.parallelMetrics);
			renderParallel();
		});
		refs.parallelSelectAll.addEventListener('click', () => {
			setAllChecked(refs.parallelMetrics, true);
			state.selectedParallelMetrics = checkedValues(refs.parallelMetrics);
			renderParallel();
		});
		refs.parallelClear.addEventListener('click', () => {
			setAllChecked(refs.parallelMetrics, false);
			state.selectedParallelMetrics = checkedValues(refs.parallelMetrics);
			renderParallel();
		});
		refs.scatterMetrics.addEventListener('change', () => {
			state.selectedScatterMetrics = checkedValues(refs.scatterMetrics);
			renderScatterMatrix();
		});
		refs.scatterSelectAll.addEventListener('click', () => {
			setAllChecked(refs.scatterMetrics, true);
			state.selectedScatterMetrics = checkedValues(refs.scatterMetrics);
			renderScatterMatrix();
		});
		refs.scatterClear.addEventListener('click', () => {
			setAllChecked(refs.scatterMetrics, false);
			state.selectedScatterMetrics = checkedValues(refs.scatterMetrics);
			renderScatterMatrix();
		});

		refs.tabButtons.forEach((button) => {
			button.addEventListener('click', () => {
				if (button.disabled) {
					return;
				}
				switchTab(button.dataset.tab);
			});
		});

		onFileChanged();
		switchTab('radar');
	}

	init();
})();
"""


def run(available_files=None, output_dir="static_dashboard_snapshot"):
    """Generate a static dashboard folder with index.html and dashboard.js."""
    files = _validate_and_resolve_files(available_files)
    payload = _load_dataset_payload(files)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    html_path = output_path / "index.html"
    js_path = output_path / "dashboard.js"

    html_path.write_text(_build_html(payload), encoding="utf-8")
    js_path.write_text(_build_js(), encoding="utf-8")

    logger.info(f"Static dashboard generated at {html_path.resolve().parent}")
    return html_path


if __name__ == "__main__":
    run()
