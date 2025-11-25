# Protocolo de Evaluación — ZDex

Este documento define el protocolo de evaluación cuantitativa para validar el funcionamiento de ZDex.

---

## Objetivos de Evaluación

| Métrica | Target | Descripción |
|---------|--------|-------------|
| **Precisión Top-1** | ≥80% | Porcentaje de capturas donde la especie predicha coincide con la real |
| **Latencia end-to-end** | <5 s | Tiempo desde captura del frame hasta resultado de clasificación |

---

## Métricas Recolectadas

El sistema registra automáticamente eventos en `data/metrics/events.jsonl`:

### Eventos de Detección (`event: "detection"`)
- `timestamp`: Momento Unix de la detección
- `species_uuid`: UUID de la especie detectada
- `species_name`: Nombre de la especie
- `detection_confidence`: Confianza del detector YOLO
- `classification_score`: Score del clasificador SpeciesNet
- `latency_ms`: Latencia de inferencia (ms)
- `bbox_area`: Área del bounding box (px²)
- `detections_in_frame`: Número de detecciones en el frame

### Eventos de Captura (`event: "capture"`)
- `timestamp`: Momento de la captura
- `species_uuid`: UUID de la especie
- `predicted_name`: Nombre predicho por el modelo
- `ground_truth_name`: Nombre real (validado por usuario)
- `correct`: `true` si predicción = ground truth
- `detection_confidence`: Confianza del detector
- `classification_score`: Score del clasificador
- `latency_ms`: Latencia total hasta captura (ms)
- `location`: Ubicación geográfica
- `auto_capture`: `true` si fue captura automática

---

## Cómo Generar Evidencias

### 1. Ejecutar la Aplicación y Capturar

```powershell
python run_zdex.py
```

1. Iniciar cámara
2. Apuntar a animales (mascotas, fotos, videos)
3. Al capturar, confirmar si la predicción es correcta
4. Si es incorrecta, ingresar el nombre real

### 2. Generar Reporte de Métricas

```powershell
# Reporte en consola
python -m zdex.metrics_report

# Reporte con gráficos PNG
python -m zdex.metrics_report --charts
```

### 3. Usar el Notebook de Evaluación

Abrir `evaluation_notebook.ipynb` en Jupyter/VS Code para análisis interactivo.

---

## Archivos de Evidencia

| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| `events.jsonl` | `data/metrics/` | Registro crudo de todos los eventos |
| `latency_histogram.png` | `data/metrics/charts/` | Distribución de latencias |
| `accuracy_by_species.png` | `data/metrics/charts/` | Precisión por especie |
| `summary_card.png` | `data/metrics/charts/` | Resumen visual de métricas |
| `evaluation_summary.json` | `data/metrics/` | Resumen en JSON (generado por notebook) |

---

## Interpretación de Resultados

### Precisión
- **≥80%**: Objetivo cumplido ✓
- **60-80%**: Aceptable, pero mejorable
- **<60%**: Requiere revisión del modelo

### Latencia
- **<5000 ms**: Objetivo cumplido ✓ (tiempo real)
- **5000-10000 ms**: Aceptable para uso interactivo
- **>10000 ms**: Demasiado lento para uso práctico

---

## Scripts de Utilidad

### Sembrar datos iniciales (desde capturas existentes)
```powershell
python -m zdex.seed_metrics
```

### Limpiar métricas (empezar de cero)
```powershell
Remove-Item data/metrics/events.jsonl
New-Item data/metrics/events.jsonl -ItemType File
```

---

## Flujo de Evaluación Completo

```
┌─────────────────┐
│  Ejecutar ZDex  │
│  (run_zdex.py)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Capturar animales│
│  (manual/auto)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Validar especie │
│  (Sí/No/Corregir)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Registro en     │
│ events.jsonl    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ metrics_report  │
│  --charts       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Gráficos PNG    │
│ + Resumen       │
└─────────────────┘
```

---

## Contacto

Repositorio: `crismoraga/PDI_v2`  
Branch: `PDI_v2.1`
