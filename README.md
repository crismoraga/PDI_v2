# ZDex — Pokédex de Animales en Tiempo Real

[![Licencia](https://img.shields.io/badge/licencia-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Demo](https://img.shields.io/badge/demo-YouTube-red.svg)](https://youtu.be/MNIEpdeGOdA)
[![YOLOv12](https://img.shields.io/badge/YOLOv12--sunsmarterjie-orange.svg)](https://github.com/sunsmarterjie/yolov12)
[![SpeciesNet](https://img.shields.io/badge/SpeciesNet-Kaggle-blue.svg)](https://www.kaggle.com/models/google/speciesnet/keras/v4.0.0b)
[![Evaluación](https://img.shields.io/badge/evaluaci%C3%B3n-ready-success)](#evaluacion-y-metricas)

> ZDex es una aplicación para detectar y clasificar animales en tiempo real, registrar capturas verificadas y generar métricas para evaluación científica y empresarial.

---

## Índice

- [ZDex — Pokédex de Animales en Tiempo Real](#zdex--pokédex-de-animales-en-tiempo-real)
  - [Índice](#índice)
  - [Resumen](#resumen)
  - [Características](#caracteristicas)
  - [Arquitectura \& Componentes](#arquitectura--componentes)
  - [Instalación y Ejecución Rápida](#instalacion-y-ejecucion-rapida)
  - [Evaluación y Métricas](#evaluacion-y-metricas)
  - [Evidencias \& Gráficos](#evidencias-y-graficos)
  - [Benchmark \& Resultados (muestra)](#benchmark--resultados-muestra)
  - [Proyecto — Estructura y Archivos Clave](#estructura-del-proyecto)
  - [Desarrollo, Pruebas y CI](#desarrollo-pruebas-y-ci)
  - [Cómo contribuir](#cómo-contribuir)
  - [Citas y Agradecimientos](#citas-y-agradecimientos)
  - [Contacto / Mantenedor](#contacto-y-mantenedor)

---

## Resumen

ZDex combina YOLOv12 y SpeciesNet para ofrecer:

- Detección de animales (frames de cámara) con YOLOv12.
- Clasificación por especie con SpeciesNet.
- Interfaz de captura (manual y auto-captura), histórial y gamificación.
- Registro de métricas en `data/metrics/events.jsonl` y herramientas para generar informes reproducibles.

Permite generar evidencia cuantitativa para validar objetivos: precisión (Top-1) y latencia end-to-end.

---

## Caracteristicas

- Soporte de detección en tiempo real con YOLOv12 (clases COCO enfocadas a fauna).
- Clasificador SpeciesNet (modelo base incluido o descargable desde Kaggle).
- UI (Tkinter) con pokédex, panel de especie, contador y auto-captura (configurable).
- Registro persistente de captures y estadísticas (`data/captures.json`, `data/stats.json`).
- Logging de métricas (JSONL) y análisis reproducible (`metrics_report.py`, `seed_metrics.py`).

---

## Arquitectura & Componentes

Arquitectura de alto nivel:

```mermaid
graph LR
  Camera[Camera/Frame] --> Pipeline[Detection Pipeline]
  Pipeline --> Detector[YOLOv12]
  Detector --> Classifier[SpeciesNet]
  Classifier --> UI[App (Tkinter)]
  Pipeline --> Metrics[Metrics Logger -> data/metrics/events.jsonl]
  UI --> Store[Capture Store]
```

Archivos clave:

- `zdex/` — código fuente principal: `app.py`, `pipeline.py`, `detector.py`, `metrics.py`.
- `data/` — capturas, estadísticas y métricas.
- `yolov12/` — repo / utilidades del detector (referencia: [YOLOv12](https://github.com/sunsmarterjie/yolov12)).
- Modelos: `models/` y descargables automáticos (Detector: YOLOv12, Classifier: SpeciesNet).

---

## Instalacion y Ejecucion Rapida

```pwsh
git clone https://github.com/crismoraga/PDI_v2.git
cd PDI_v2
pip install -r yolov12/requirements.txt
pip install -r zdex/requirements.txt  # si existe
```

Para ejecutar la aplicación:

```pwsh
python run_zdex.py
```

Probar el detector sin cámara:

```bash
python test_detection.py
```

---

## Evaluacion y metricas

ZDex soporta un flujo de evaluación reproducible:

- Guardar eventos de detección/captura en `data/metrics/events.jsonl`.
- Generar gráficos y resumen con `zdex/metrics_report.py`.
- Analizar en detalle con `evaluation_notebook.ipynb`.

Tipos de eventos:

- `detection`: latencia de inferencia, número de detecciones, bounding boxes, scores
- `capture`: captura, predicted_name, ground_truth_name, correct, detection_confidence, classification_score, latency_ms, location, auto_capture
- `latency`: muestras puntuales por etapa

Comandos de ayuda:

```pwsh
python -m zdex.seed_metrics            # Poblar métricas con datos de ejemplo (demo/CI)
python -m zdex.metrics_report --charts # Resumen y gráficos PNG en data/metrics/charts/
```

Para exportar resultados y evidencia a JSON/PNG ver `evaluation_notebook.ipynb`.

---

## Evidencias y Graficos

Se generan PNG con `--charts` en `data/metrics/charts/`. Ejemplos:

- `latency_histogram.png` — histograma latencias
- `accuracy_by_species.png` — barras de precisión por especie
- `summary_card.png` — resumen ejecutivo visual

Si existen, se renderizan más arriba en la sección; ejecute el script para regenerarlos con datos reales.

---

## Benchmark & Resultados (muestra)

Los números mostrados en las pruebas iniciales con datos semilla resultaron en:

| Métrica | Valor (sample) | Target |
|---|---:|:---|
| Latencia inferencia (promedio) | ~2.3 s | < 5 s |
| Latencia captura (promedio) | ~2.5 s | < 5 s |
| Precisión Top-1 (global) | 100% (seeded) | ≥ 80% |

> Notas: Estos son datos de ejemplo generados por `seed_metrics.py`. Recomendamos recolectar evidencias reales para un informe definitivo.

---

## Estructura del proyecto

```text
PDI_v2/
├── zdex/                   # App (pipeline, UI, metrics, tools)
├── data/                   # captures, stats, metrics
├── models/                 # models (detector/classifier)
├── yolov12/                # detector helper / requirements
├── evaluation_notebook.ipynb
├── EVALUATION.md
├── ENTREGABLE_EVALUACION.md
└── README.md
```

---

## Desarrollo, Pruebas y CI

Pautas: Añada tests unitarios, use entornos reproducibles y genere artefactos de CI.

Ejemplos de QA:

```pwsh
python -m zdex.seed_metrics
python -m zdex.metrics_report --charts
```

Sugerencia para CI: generar `data/metrics/charts` y publicar como artefactos.

---

## Cómo contribuir

1. Fork & branch
2. Añadir tests y documentación
3. Abrir PR con descripción y métricas de rendimiento (si aplica)

---

## Citas y Agradecimientos

Este proyecto se basa en:

- YOLOv12 (sunsmarterjie): [https://github.com/sunsmarterjie/yolov12](https://github.com/sunsmarterjie/yolov12)
- SpeciesNet (Google / Kaggle): [https://www.kaggle.com/models/google/speciesnet/keras/v4.0.0b](https://www.kaggle.com/models/google/speciesnet/keras/v4.0.0b)

Por favor cite ambos proyectos si utiliza ZDex para trabajo académico.

---

## Contacto y Mantenedor

Para preguntas o soporte: abra un Issue en el repo o contacte al mantenedor @crismoraga.

---
