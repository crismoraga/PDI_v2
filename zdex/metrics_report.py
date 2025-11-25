"""CLI utility to summarize ZDex evaluation metrics and generate charts."""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Tuple

from . import config

# Matplotlib optional - charts only generated if available
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def _iter_records(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"ADVERTENCIA línea {line_number}: no se pudo parsear JSON ({exc}).")


def _percentile(values: Iterable[float], pct: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return float("nan")
    rank = (len(ordered) - 1) * (pct / 100.0)
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    fraction = rank - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def _format_latency(values: list[float]) -> str:
    if not values:
        return "sin muestras"
    avg = statistics.fmean(values)
    median = statistics.median(values)
    p95 = _percentile(values, 95)
    return f"n={len(values)}, promedio={avg:.1f} ms, mediana={median:.1f} ms, p95={p95:.1f} ms"


def _summarize_captures(records: Iterable[dict[str, Any]], top_n: int) -> None:
    total = 0
    correct = 0
    auto = 0
    latency: list[float] = []
    species_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "correct": 0})
    for record in records:
        if record.get("event") != "capture":
            continue
        total += 1
        if record.get("correct"):
            correct += 1
        if record.get("auto_capture"):
            auto += 1
        latency_value = record.get("latency_ms")
        if isinstance(latency_value, (int, float)):
            latency.append(float(latency_value))
        species_name = record.get("ground_truth_name") or record.get("predicted_name") or "Desconocido"
        species_stats[species_name]["total"] += 1
        if record.get("correct"):
            species_stats[species_name]["correct"] += 1
    if total == 0:
        print("No hay capturas registradas todavía.")
        return
    manual = total - auto
    accuracy = (correct / total) * 100.0
    print("\n== Capturas ==")
    print(f"Total: {total} | Manual: {manual} | Auto: {auto}")
    print(f"Precisión global: {accuracy:.1f}%")
    print(f"Latencia de captura: {_format_latency(latency)}")
    ranked: list[Tuple[str, Dict[str, int]]] = sorted(
        species_stats.items(),
        key=lambda item: item[1]["total"],
        reverse=True,
    )
    if not ranked:
        return
    print("\n-- Top especies (por capturas registradas) --")
    for name, stats in ranked[:top_n]:
        spec_total = stats["total"]
        spec_correct = stats["correct"]
        spec_accuracy = (spec_correct / spec_total) * 100.0 if spec_total else 0.0
        print(f"- {name}: {spec_total} capturas, precisión {spec_accuracy:.1f}%")


def _generate_charts(records: List[dict[str, Any]], top_n: int) -> None:
    """Generate evaluation charts and save them as PNG files."""
    if not HAS_MATPLOTLIB:
        print("\nmatplotlib no disponible - no se generan gráficos.")
        return
    charts_dir = config.DATA_DIR / "metrics" / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    # Collect latency data
    detection_latency: List[float] = []
    capture_latency: List[float] = []
    species_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "correct": 0})

    for rec in records:
        event = rec.get("event")
        lat = rec.get("latency_ms")
        if event == "detection" and isinstance(lat, (int, float)):
            detection_latency.append(float(lat))
        elif event == "capture":
            if isinstance(lat, (int, float)):
                capture_latency.append(float(lat))
            species_name = rec.get("ground_truth_name") or rec.get("predicted_name") or "Desconocido"
            species_stats[species_name]["total"] += 1
            if rec.get("correct"):
                species_stats[species_name]["correct"] += 1

    # 1. Latency histogram
    if detection_latency or capture_latency:
        fig, ax = plt.subplots(figsize=(8, 5))
        if detection_latency:
            ax.hist(detection_latency, bins=20, alpha=0.7, label="Detección")
        if capture_latency:
            ax.hist(capture_latency, bins=20, alpha=0.7, label="Captura")
        ax.axvline(5000, color="red", linestyle="--", label="Target 5s")
        ax.set_xlabel("Latencia (ms)")
        ax.set_ylabel("Frecuencia")
        ax.set_title("Distribución de Latencia - ZDex")
        ax.legend()
        fig.tight_layout()
        fig.savefig(charts_dir / "latency_histogram.png", dpi=150)
        plt.close(fig)
        print(f"\nGráfico guardado: {charts_dir / 'latency_histogram.png'}")

    # 2. Accuracy by species
    ranked = sorted(species_stats.items(), key=lambda x: x[1]["total"], reverse=True)[:top_n]
    if ranked:
        names = [n for n, _ in ranked]
        accuracies = [(s["correct"] / s["total"] * 100 if s["total"] else 0) for _, s in ranked]
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.barh(names[::-1], accuracies[::-1], color="steelblue")
        ax.axvline(80, color="red", linestyle="--", label="Target 80%")
        ax.set_xlabel("Precisión (%)")
        ax.set_title("Precisión Top-1 por Especie")
        ax.set_xlim(0, 105)
        ax.legend()
        fig.tight_layout()
        fig.savefig(charts_dir / "accuracy_by_species.png", dpi=150)
        plt.close(fig)
        print(f"Gráfico guardado: {charts_dir / 'accuracy_by_species.png'}")

    # 3. Summary card
    total_captures = sum(s["total"] for s in species_stats.values())
    total_correct = sum(s["correct"] for s in species_stats.values())
    overall_accuracy = (total_correct / total_captures * 100) if total_captures else 0
    avg_latency_det = statistics.fmean(detection_latency) if detection_latency else 0
    avg_latency_cap = statistics.fmean(capture_latency) if capture_latency else 0
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axis("off")
    text = (
        f"=== ZDex Evaluation Summary ===\n\n"
        f"Total Capturas: {total_captures}\n"
        f"Precisión Global: {overall_accuracy:.1f}%  {'✓' if overall_accuracy >= 80 else '✗'}\n"
        f"Latencia Detección: {avg_latency_det:.0f} ms  {'✓' if avg_latency_det < 5000 else '✗'}\n"
        f"Latencia Captura: {avg_latency_cap:.0f} ms  {'✓' if avg_latency_cap < 5000 else '✗'}\n\n"
        f"Targets:\n"
        f"  Precisión ≥80%  |  Latencia <5000 ms"
    )
    ax.text(0.5, 0.5, text, ha="center", va="center", fontsize=12, family="monospace", transform=ax.transAxes)
    fig.tight_layout()
    fig.savefig(charts_dir / "summary_card.png", dpi=150)
    plt.close(fig)
    print(f"Gráfico guardado: {charts_dir / 'summary_card.png'}")


def _summarize_detections(records: Iterable[dict[str, Any]]) -> None:
    latency: list[float] = []
    detections = 0
    for record in records:
        if record.get("event") != "detection":
            continue
        detections += 1
        latency_value = record.get("latency_ms")
        if isinstance(latency_value, (int, float)):
            latency.append(float(latency_value))
    if detections == 0:
        print("No hay detecciones registradas todavía.")
        return
    print("\n== Detecciones ==")
    print(f"Eventos: {detections}")
    print(f"Latencia de inferencia: {_format_latency(latency)}")


def main(argv: list[str] | None = None) -> int:
    default_path = config.DATA_DIR / "metrics" / "events.jsonl"
    parser = argparse.ArgumentParser(description="Genera un resumen de las métricas recogidas por ZDex.")
    parser.add_argument(
        "--path",
        type=Path,
        default=default_path,
        help=f"Ruta del archivo JSONL (por defecto {default_path})",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Número de especies a mostrar en el ranking",
    )
    parser.add_argument(
        "--charts",
        action="store_true",
        help="Generar gráficos PNG en data/metrics/charts/",
    )
    args = parser.parse_args(argv)
    path: Path = args.path
    if not path.exists():
        print(f"No existe el archivo de métricas: {path}")
        return 1
    records = list(_iter_records(path))
    if not records:
        print("El archivo de métricas está vacío.")
        return 0
    timestamps = [rec.get("timestamp") for rec in records if isinstance(rec.get("timestamp"), (int, float))]
    if timestamps:
        start = datetime.fromtimestamp(min(timestamps), tz=timezone.utc)
        end = datetime.fromtimestamp(max(timestamps), tz=timezone.utc)
        print("Ventana analizada:")
        print(f"{start.isoformat()} — {end.isoformat()}")
    _summarize_detections(records)
    _summarize_captures(records, top_n=args.top)
    if args.charts:
        _generate_charts(records, top_n=args.top)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
