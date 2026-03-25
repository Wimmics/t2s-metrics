# Dashboard and Exports

## Launch dashboard with auto-discovery

```bash
cli dashboard
```

This loads discovered files from `datasets/*/results/*.json`.

## Load explicit result files

```bash
cli dashboard -f \
  datasets/ck25/results/ck25-20260306-133227.json \
  datasets/db25/results/db25-20260306-132100.json
```

## Create a static snapshot

```bash
cli dashboard --static --output static_dashboard_snapshot
```

Default dashboard URL:

- `http://127.0.0.1:8050`
