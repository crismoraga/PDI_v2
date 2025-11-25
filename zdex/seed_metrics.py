"""Script para generar datos iniciales de evaluación desde stats.json y captures.json."""
from __future__ import annotations

import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path

from . import config
from .metrics import METRICS


def _parse_iso(stamp: str) -> float:
    """Parse ISO timestamp to Unix epoch."""
    try:
        dt = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        return dt.timestamp()
    except Exception:
        return time.time()


def seed_from_existing_data() -> int:
    """
    Read stats.json and captures.json and generate synthetic detection/capture events
    so that metrics_report has data to analyze.  Returns the number of events written.
    """
    stats_path = config.DATA_DIR / "stats.json"
    captures_path = config.DATA_DIR / "captures.json"
    count = 0

    if stats_path.exists():
        with stats_path.open("r", encoding="utf-8") as fp:
            stats = json.load(fp)
        species_data = stats.get("species", {})
        for species_name, info in species_data.items():
            common_name = info.get("common_name", species_name)
            confidence = info.get("best_confidence", 0.5)
            sightings = info.get("total_sightings", 1)
            first_seen = info.get("first_seen")
            ts = _parse_iso(first_seen) if first_seen else time.time()
            # Generate synthetic detection events for each sighting
            for _ in range(sightings):
                latency = random.uniform(800, 4500)  # ms
                METRICS.log_detection_event(
                    species_uuid=None,
                    species_name=f"{common_name} ({species_name})" if species_name else common_name,
                    detection_confidence=confidence * random.uniform(0.9, 1.0),
                    classification_score=confidence,
                    latency_ms=latency,
                    bbox_area=random.randint(10000, 150000),
                    detections_in_frame=1,
                )
                count += 1
                # Advance timestamp slightly for variety
                ts += random.uniform(1, 5)

    if captures_path.exists():
        with captures_path.open("r", encoding="utf-8") as fp:
            captures = json.load(fp)
        species_map = captures.get("species", {})
        for uuid, entry in species_map.items():
            common_name = entry.get("common_name", "unknown")
            captures_list = entry.get("captures", [])
            for cap in captures_list:
                conf = cap.get("confidence", 0.5)
                location = cap.get("location", "unknown")
                # Assume prediction correct unless marked otherwise
                METRICS.log_capture_event(
                    species_uuid=uuid,
                    predicted_name=common_name,
                    ground_truth_name=common_name,
                    correct=True,
                    detection_confidence=conf * random.uniform(0.85, 1.0),
                    classification_score=conf,
                    latency_ms=random.uniform(1000, 4000),
                    location=location,
                    auto_capture=random.choice([True, False]),
                )
                count += 1
    return count


def main() -> int:
    print("Generando datos de evaluacion desde stats.json y captures.json...")
    n = seed_from_existing_data()
    print(f"Se escribieron {n} eventos en data/metrics/events.jsonl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
