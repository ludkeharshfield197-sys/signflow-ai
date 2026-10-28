from pathlib import Path

from inference.evaluation import presence_metrics


def test_presence_metrics_count_each_expected_label_once_per_asset():
    metrics = presence_metrics(
        [
            {"expected": ["hello"], "predicted": ["hello", "hello"]},
            {"expected": [], "predicted": ["milk"]},
            {"expected": ["water", "please"], "predicted": ["water"]},
        ]
    )

    assert metrics == {
        "truePositives": 2,
        "falsePositives": 1,
        "falseNegatives": 1,
        "precision": 0.666667,
        "recall": 0.666667,
        "f1": 0.666667,
    }


def test_benchmark_never_auto_installs_runtime_dependencies():
    source = (
        Path(__file__).resolve().parents[1] / "scripts" / "benchmark_model_cards.py"
    ).read_text(encoding="utf-8")

    disable_index = source.index('os.environ.setdefault("YOLO_AUTOINSTALL", "false")')
    import_index = source.index("from ultralytics import YOLO")
    assert disable_index < import_index
