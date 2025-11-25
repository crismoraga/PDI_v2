"""CLI utility to summarize ZDex evaluation metrics and generate charts."""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
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
    confusion_pairs: List[Tuple[str, str]] = []
    latency_by_hour: List[List[float]] = [[] for _ in range(24)]
    species_latency: Dict[str, List[float]] = defaultdict(list)

    for rec in records:
        event = rec.get("event")
        lat = rec.get("latency_ms")
        if event == "detection" and isinstance(lat, (int, float)):
            detection_latency.append(float(lat))
            ts = rec.get("timestamp")
            if isinstance(ts, (int, float)):
                hour = datetime.fromtimestamp(ts, tz=timezone.utc).hour
                latency_by_hour[hour].append(float(lat))
        elif event == "capture":
            if isinstance(lat, (int, float)):
                capture_latency.append(float(lat))
            species_name = rec.get("ground_truth_name") or rec.get("predicted_name") or "Desconocido"
            species_stats[species_name]["total"] += 1
            if rec.get("correct"):
                species_stats[species_name]["correct"] += 1
            if isinstance(lat, (int, float)):
                species_latency[species_name].append(float(lat))
            gt_name = species_name
            pred_name = rec.get("predicted_name") or species_name
            confusion_pairs.append((gt_name, pred_name))

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
    fig.savefig(charts_dir / "summary_card.jpg", dpi=150)  # JPEG support
    plt.close(fig)
    print(f"Gráfico guardado: {charts_dir / 'summary_card.png'}")

    # 4. Confusion matrix for top species
    if confusion_pairs:
        gt_counter = Counter(gt for gt, _ in confusion_pairs)
        top_species = [name for name, _ in gt_counter.most_common(min(top_n, len(gt_counter)))]
        if top_species:
            idx = {name: i for i, name in enumerate(top_species)}
            matrix = [[0 for _ in top_species] for _ in top_species]
            for gt, pred in confusion_pairs:
                if gt in idx and pred in idx:
                    matrix[idx[gt]][idx[pred]] += 1
            fig, ax = plt.subplots(figsize=(8, 6))
            cax = ax.imshow(matrix, cmap="viridis")
            ax.set_xticks(range(len(top_species)))
            ax.set_yticks(range(len(top_species)))
            ax.set_xticklabels(top_species, rotation=45, ha="right", fontsize=8)
            ax.set_yticklabels(top_species, fontsize=8)
            ax.set_xlabel("Predicción")
            ax.set_ylabel("Ground Truth")
            ax.set_title("Matriz de Confusión (Top especies)")
            max_cell = max((val for row in matrix for val in row), default=0)
            threshold = max_cell / 2 if max_cell else 0
            for i in range(len(top_species)):
                for j in range(len(top_species)):
                    value = matrix[i][j]
                    text_color = "white" if threshold and value > threshold else "black"
                    ax.text(j, i, str(value), ha="center", va="center", color=text_color, fontsize=7)
            fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04)
            fig.tight_layout()
            fig.savefig(charts_dir / "confusion_matrix.png", dpi=200)
            fig.savefig(charts_dir / "confusion_matrix.jpg", dpi=200)
            plt.close(fig)
            print(f"Gráfico guardado: {charts_dir / 'confusion_matrix.png'}")

    # 5. Latency heatmap by hour
    avg_latency_hour = [statistics.fmean(bucket) if bucket else 0 for bucket in latency_by_hour]
    if any(avg_latency_hour):
        fig, ax = plt.subplots(figsize=(10, 2.5))
        heat = ax.imshow([avg_latency_hour], aspect="auto", cmap="inferno")
        ax.set_xticks(range(24))
        ax.set_xticklabels(range(24))
        ax.set_yticks([])
        ax.set_xlabel("Hora del día (UTC)")
        ax.set_title("Latencia promedio por hora")
        fig.colorbar(heat, ax=ax, orientation="vertical", label="Latencia (ms)")
        fig.tight_layout()
        fig.savefig(charts_dir / "latency_heatmap.png", dpi=200)
        fig.savefig(charts_dir / "latency_heatmap.jpg", dpi=200)
        plt.close(fig)
        print(f"Gráfico guardado: {charts_dir / 'latency_heatmap.png'}")

    # 6. Species latency heatmap (top N)
    if species_latency:
        latency_stats = {
            name: {
                "avg": statistics.fmean(values),
                "count": len(values)
            }
            for name, values in species_latency.items() if values
        }
        ordered_species = sorted(latency_stats.items(), key=lambda item: item[1]["count"], reverse=True)[:top_n]
        if ordered_species:
            labels = [name for name, _ in ordered_species]
            data = [[latency_stats[name]["avg"], latency_stats[name]["count"]] for name in labels]
            max_avg = max(row[0] for row in data)
            max_count = max(row[1] for row in data)
            normalized = [[row[0] / max_avg if max_avg else 0, row[1] / max_count if max_count else 0] for row in data]
            fig, ax = plt.subplots(figsize=(6, max(4, len(labels) * 0.4)))
            heat = ax.imshow(normalized, aspect="auto", cmap="plasma")
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(labels, fontsize=8)
            ax.set_xticks([0, 1])
            ax.set_xticklabels(["Latencia avg", "Muestras"])
            ax.set_title("Heatmap especie vs latencia")
            for i, row in enumerate(data):
                ax.text(0, i, f"{row[0]:.0f} ms", va="center", ha="center", color="white", fontsize=7)
                ax.text(1, i, str(row[1]), va="center", ha="center", color="white", fontsize=7)
            fig.colorbar(heat, ax=ax, fraction=0.046, pad=0.04)
            fig.tight_layout()
            fig.savefig(charts_dir / "species_latency_heatmap.png", dpi=200)
            fig.savefig(charts_dir / "species_latency_heatmap.jpg", dpi=200)
            plt.close(fig)
            print(f"Gráfico guardado: {charts_dir / 'species_latency_heatmap.png'}")

    # 4. Time Series Evolution (Accuracy & Latency)
    timestamps = []
    accuracies = []
    latencies = []
    
    # Sort records by timestamp
    sorted_records = sorted(records, key=lambda x: x.get("timestamp", 0))
    
    running_correct = 0
    running_total = 0
    
    for rec in sorted_records:
        ts = rec.get("timestamp")
        if not ts: continue
        
        if rec.get("event") == "capture":
            running_total += 1
            if rec.get("correct"):
                running_correct += 1
            # Calculate running accuracy every 50 captures to avoid noise
            if running_total % 10 == 0:
                timestamps.append(datetime.fromtimestamp(ts))
                accuracies.append((running_correct / running_total) * 100)
        
        if rec.get("event") == "detection" and rec.get("latency_ms"):
            # Sample latency every ~10s to keep chart readable
            if len(latencies) == 0 or (ts - latencies[-1][0].timestamp() > 10):
                latencies.append((datetime.fromtimestamp(ts), rec.get("latency_ms")))

    if timestamps and accuracies:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        
        # Accuracy Evolution
        ax1.plot(timestamps, accuracies, color="green", linewidth=2)
        ax1.axhline(80, color="red", linestyle="--", label="Target 80%")
        ax1.set_ylabel("Precisión Acumulada (%)")
        ax1.set_title("Evolución de Precisión en el Tiempo")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Latency Evolution
        if latencies:
            lat_ts, lat_vals = zip(*latencies)
            ax2.plot(lat_ts, lat_vals, color="orange", alpha=0.7)
            ax2.axhline(5000, color="red", linestyle="--", label="Target 5s")
            ax2.set_ylabel("Latencia (ms)")
            ax2.set_xlabel("Tiempo")
            ax2.set_title("Evolución de Latencia")
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
        fig.tight_layout()
        fig.savefig(charts_dir / "evolution_metrics.png", dpi=150)
        fig.savefig(charts_dir / "evolution_metrics.jpg", dpi=150)
        plt.close(fig)
        print(f"Gráfico de evolución guardado: {charts_dir / 'evolution_metrics.png'}")

    # 5. Generate GIF (Simple Animation of Accuracy)
    try:
        import matplotlib.animation as animation
        if timestamps and accuracies:
            fig, ax = plt.subplots(figsize=(8, 5))
            line, = ax.plot([], [], color="green", lw=2)
            ax.set_xlim(min(timestamps), max(timestamps))
            ax.set_ylim(0, 105)
            ax.axhline(80, color="red", linestyle="--")
            ax.set_title("Evolución de Precisión (Animación)")
            ax.set_ylabel("Precisión (%)")
            ax.set_xlabel("Tiempo")
            
            def init():
                line.set_data([], [])
                return line,
            
            def animate(i):
                # Show up to i-th point
                idx = int((i / 100) * len(timestamps))
                if idx < 1: idx = 1
                x = timestamps[:idx]
                y = accuracies[:idx]
                line.set_data(x, y)
                return line,
            
            ani = animation.FuncAnimation(fig, animate, frames=100, init_func=init, blit=True)
            gif_path = charts_dir / "accuracy_evolution.gif"
            # Requires pillow or imagemagick
            try:
                ani.save(gif_path, writer='pillow', fps=15)
                print(f"GIF guardado: {gif_path}")
            except Exception as e:
                print(f"No se pudo guardar GIF (falta writer?): {e}")
            plt.close(fig)
    except ImportError:
        pass



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
