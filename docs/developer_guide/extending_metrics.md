# Extending Metrics

## 1. Implement a metric class

Create a class inheriting from `Metric` and implement `compute`.

```python
from t2smetrics.metrics.base import Metric
from t2smetrics.core.result import EvaluationResult


class MyMetric(Metric):
    name = "my_metric"
    requires_execution = False
    requires_llm = False

    def compute(self, case, context=None) -> EvaluationResult:
        value = 1.0
        return EvaluationResult(
            dataset="unknown",
            system_name="unknown",
            query_id=case.id,
            metric=self.name,
            score=value,
        )
```

## 2. Register it

Add it to the list returned by `get_metric_mapping()` in `t2smetrics/metrics/metrics_utils.py`.

## 3. Test it

Add focused tests under `test/` and run:

```bash
uv run pytest
```

## 4. Expose from package (optional)

If you want public import support, add your class to `t2smetrics/metrics/__init__.py`.
