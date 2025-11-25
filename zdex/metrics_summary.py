"""
Simple script to compute metrics summary from data/metrics/events.jsonl
Outputs a JSON summary used by README and automated reporting.
"""
import json
import statistics
from pathlib import Path


def read_events(path):
    events = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            events.append(json.loads(line))
    return events


def compute_summary(events):
    detection_latencies = [e["latency_ms"] for e in events if e["event"] == "detection" and "latency_ms" in e]
    capture_latencies = [e["latency_ms"] for e in events if e["event"] == "capture" and "latency_ms" in e]
    captures = [e for e in events if e["event"] == "capture"]
    detections = [e for e in events if e["event"] == "detection"]

    def stats(arr):
        if not arr:
            return {"n": 0}
        return {
            "n": len(arr),
            "mean": statistics.mean(arr),
            "median": statistics.median(arr),
            "p95": statistics.quantiles(arr, n=100)[94],
            "min": min(arr),
            "max": max(arr),
        }

    detection_stats = stats(detection_latencies)
    capture_stats = stats(capture_latencies)

    # precision (Top-1) from captures
    if captures:
        correct = sum(1 for e in captures if e.get("correct") in (True, 1))
        precision = correct / len(captures) * 100.0
    else:
        precision = None

    # accuracy by species
    species_counts = {}
    species_correct = {}
    for e in captures:
        species = e.get("ground_truth_name") or e.get("predicted_name") or "unknown"
        species_counts[species] = species_counts.get(species, 0) + 1
        if e.get("correct"):
            species_correct[species] = species_correct.get(species, 0) + 1

    species_accuracy = {
        s: {"count": species_counts[s], "correct": species_correct.get(s, 0), "accuracy": (species_correct.get(s, 0) / species_counts[s] * 100.0)}
        for s in species_counts
    }

    summary = {
        "detection_count": len(detections),
        "capture_count": len(captures),
        "detection_latency": detection_stats,
        "capture_latency": capture_stats,
        "precision_top1": precision,
        "species_accuracy": species_accuracy,
    }

    return summary


def main():
    root = Path(__file__).resolve().parents[1]
    events_file = root / "data" / "metrics" / "events.jsonl"
    if not events_file.exists():
        print("No existe data/metrics/events.jsonl. Ejecute zdex.seed_metrics para generar datos de ejemplo.")
        return 1

    events = read_events(events_file)
    summary = compute_summary(events)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
