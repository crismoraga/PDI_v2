# Justificación del Uso de YOLO y SpeciesNet en ZDex

## 1. Introducción
ZDex requiere detección y clasificación de animales en tiempo real, con precisión alta, baja latencia y modelos que funcionen de manera local sin depender de servicios externos. Luego de evaluar diferentes alternativas, se seleccionó YOLO para la detección y SpeciesNet para la clasificación debido a su desempeño, especialización y compatibilidad.

## 2. Por Qué Se Usó YOLO

### 2.1. Rendimiento en Tiempo Real
YOLO (“You Only Look Once”) es uno de los modelos más rápidos en visión computacional. Permite procesar frames a 30–60 FPS, lo que lo hace ideal para aplicaciones con cámara en vivo.

### 2.2. Alta Precisión y Estabilidad
YOLOv12 destaca por:
- Mejor detección de objetos pequeños,
- Bounding boxes más estables,
- Arquitectura optimizada.

### 2.3. Ecosistema y Facilidad de Integración
YOLO ofrece:
- Implementaciones listas en Python,
- Compatibilidad con OpenCV,
- Exportación a ONNX / TensorRT,
- Comunidad activa.

## 3. Alternativas de Detección Descartadas
- SSD: menos preciso en objetos pequeños.
- EfficientDet: más lento y demandante.
- Detectron2: demasiado pesado para tiempo real.
- DETR/ViT: alta demanda computacional.

## 4. Por Qué SpeciesNet

### 4.1. Especialización
Entrenado con 65M de imágenes reales de fauna. Diseñado específicamente para biodiversidad.

### 4.2. Precisión Profesional
- 99.4% detección de animales,
- 98.7% acierto en presencia,
- 94.5% precisión por especie.

### 4.3. Sinergia con YOLO
Pipeline:
YOLO → bounding box → SpeciesNet → especie exacta

## 5. Alternativas de Clasificación Descartadas
- ResNet, Inception, VGG: no especializados en fauna.
- Google Lens / Vision API: requieren internet.
- MegaDetector: solo detecta, no clasifica.

## 6. Conclusión
La combinación YOLO + SpeciesNet entrega
- velocidad,
- precisión,
- funcionamiento offline,
- especialización en fauna.

Fue la elección óptima para los requisitos de ZDex.
