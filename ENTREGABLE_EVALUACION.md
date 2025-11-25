# Entregable - Sistema de Evaluación ZDex

## Resumen

Se implementó un **sistema completo de métricas y evaluación** para validar cuantitativamente el funcionamiento de ZDex según los objetivos propuestos:

- **Precisión Top-1 ≥80%**
- **Latencia end-to-end <5 segundos**

---

## Implementación

### 1. Módulo de Métricas (`zdex/metrics.py`)

Registro centralizado de eventos JSONL con thread-safety:

- `DetectionMetricsRecord`: latencia, confianza, especie detectada
- `CaptureMetricsRecord`: ground truth, precisión, auto/manual
- `LatencyRecord`: muestras de latencia por etapa

**Uso:** Importado automáticamente por `pipeline.py` y `app.py`

### 2. Instrumentación del Pipeline (`zdex/pipeline.py`)

- Mide latencia de inferencia por frame
- Registra cada detección con metadata (bbox, confianza, especie)
- Escribe a `data/metrics/events.jsonl`

### 3. Validación de Capturas (`zdex/app.py`)

- Pregunta al usuario si la predicción es correcta (Sí/No)
- Permite corregir el nombre si hay error
- Registra `ground_truth_name` y flag `correct`
- Distingue capturas manuales vs auto-captura

### 4. CLI de Reporte (`zdex/metrics_report.py`)

```powershell
python -m zdex.metrics_report          # Resumen en consola
python -m zdex.metrics_report --charts # + Gráficos PNG
```

Genera:
- Estadísticas de latencia (promedio, mediana, p95)
- Precisión global y por especie
- Gráficos en `data/metrics/charts/`

### 5. Seed de Datos (`zdex/seed_metrics.py`)

Convierte datos existentes de `stats.json` y `captures.json` a formato de evaluación:

```powershell
python -m zdex.seed_metrics
```

### 6. Notebook Interactivo (`evaluation_notebook.ipynb`)

Análisis visual con pandas y matplotlib:
- Histogramas de latencia
- Precisión por especie
- Resumen ejecutivo
- Exportación a JSON

### 7. Documentación (`EVALUATION.md`)

Protocolo completo de evaluación:
- Objetivos y métricas
- Flujo de recolección de evidencias
- Interpretación de resultados
- Scripts de utilidad

---

## Ubicación de Archivos

| Archivo | Ruta | Propósito |
|---------|------|-----------|
| `metrics.py` | `zdex/` | Logger de métricas |
| `metrics_report.py` | `zdex/` | CLI de reportes |
| `seed_metrics.py` | `zdex/` | Sembrar datos iniciales |
| `evaluation_notebook.ipynb` | raíz | Análisis interactivo |
| `EVALUATION.md` | raíz | Documentación del protocolo |
| `events.jsonl` | `data/metrics/` | Registro de eventos |
| `*.png` | `data/metrics/charts/` | Gráficos de evidencia |

---

## Evidencias Generadas

Tras ejecutar `python -m zdex.metrics_report --charts`:

```
data/metrics/
├── events.jsonl
└── charts/
    ├── latency_histogram.png
    ├── accuracy_by_species.png
    └── summary_card.png
```

---

## Resultados Actuales (Datos Sintéticos)

```
== Detecciones ==
Eventos: 54
Latencia de inferencia: promedio=2336 ms, mediana=2310 ms, p95=3945 ms

== Capturas ==
Total: 58 | Manual: 31 | Auto: 27
Precisión global: 100.0%
Latencia de captura: promedio=2488 ms

Estado: ✓ Latencia <5s | ✓ Precisión ≥80%
```

---

## Próximos Pasos

1. **Recolectar capturas reales** con validación de ground truth
2. **Ejecutar notebook** para generar `evaluation_summary.json`
3. **Exportar gráficos** como evidencia para documentación final

---

**Repositorio:** `crismoraga/PDI_v2`  
**Branch:** `PDI_v2.1`  
**Fecha:** 2025-11-24
