def presence_metrics(samples):
    """Calculate micro label-presence metrics without double-counting video frames."""
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    for sample in samples:
        expected = {str(label) for label in sample.get("expected", []) if str(label)}
        predicted = {str(label) for label in sample.get("predicted", []) if str(label)}
        true_positives += len(expected & predicted)
        false_positives += len(predicted - expected)
        false_negatives += len(expected - predicted)

    precision_denominator = true_positives + false_positives
    recall_denominator = true_positives + false_negatives
    precision = true_positives / precision_denominator if precision_denominator else 1.0
    recall = true_positives / recall_denominator if recall_denominator else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return {
        "truePositives": true_positives,
        "falsePositives": false_positives,
        "falseNegatives": false_negatives,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
    }
