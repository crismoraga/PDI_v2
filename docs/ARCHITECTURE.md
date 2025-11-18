# ZDex Architecture (Detailed)

This document provides a deeper look into the architectural choices for ZDex.

## Diagram

- Camera -> YOLOv12 Detector -> SpeciesNet classifier
- Python (Tkinter) UI handles rendering and state
- Wikipedia + Wikidata for enrichment
- Gamification backed by JSON persistence `data/stats.json`

## Event flow

1. Camera capture thread collects frames and enqueues them
2. Detection pipeline consumes frames and performs YOLO infer + SpeciesNet classification
3. Results are published on a queue; UI thread polls and renders
4. If a species is recognized with classification confidence >= `config.FREEZE_CONFIDENCE_THRESHOLD`, UI freezes and shows a focused detail view
5. Captures recorded to `data/captures/` and gamification stats updated in `zdex/gamification.py`
6. Wikipedia lookup is performed in background (threadpool) and, if available, Wikidata is used to extract structured fields via SPARQL for more precise data

## Benefits
- Decoupled threads allow stable UI despite long running inference
- Caching Wikipedia and Wikidata calls reduces network overhead
- Modular components (detector, classifier, pipeline, UI) enable easy extension - e.g., add another detector or a new model

## Next steps
- Add monitoring and observability integration (e.g., send key events to logs or instrumentation)
- Add offline fallback for Wikipedia - local fallback DB
