# ZDex - Enciclopedia Animal en Tiempo Real

<div align="center">

**Una Pokédex para animales reales** 🦁🐯🦅

Identificación de animales en tiempo real usando YOLOv12 y SpeciesNet

</div>

---

## 🚀 Características

- ✅ **Detección en tiempo real** con YOLOv12-turbo (estado del arte)
- ✅ **Clasificación precisa** con SpeciesNet (94.5% precisión en especies)
- ✅ **Soporte para AMD GPU** vía DirectML (RX 6700 XT)
- ✅ **Interfaz gráfica moderna** con Tkinter
- ✅ **Información enriquecida** desde Wikipedia (español/inglés)
- ✅ **Historial de capturas** con ubicación y notas
- ✅ **Animación de captura** con efecto flash

---

## 📋 Requisitos

### Hardware
- **GPU**: AMD Radeon RX 6700 XT (o cualquier GPU con DirectML)
- **Webcam**: Cámara integrada o externa
- **RAM**: Mínimo 8 GB

### Software
- **Python**: 3.10 o superior
- **Sistema Operativo**: Windows 10/11 (por DirectML)

---

## 🔧 Instalación


### 1. Clonar el repositorio YOLOv12

```powershell
# Si no existe ya
git clone https://github.com/sunsmarterjie/yolov12.git
cd yolov12
pip install -e .
cd ..
```

### 2. Instalar dependencias


```powershell
pip install torch torchvision
pip install torch-directml  # Soporte AMD GPU
pip install opencv-python
pip install pillow
pip install requests
pip install Wikipedia-API
pip install ultralytics
```

### 3. Descargar modelos

Los modelos se descargan automáticamente en el primer uso:
- **YOLOv12-m**: Detector de animales (~50 MB)
- **SpeciesNet**: Clasificador incluido (88M parámetros)

---

## 🎮 Uso

### Opción 1: Script launcher (recomendado)

```powershell
python run_zdex.py
```
## ✨ Generar activos de UI

Si quieres el GIF de celebración o el GIF de demostración (útil para documentación y demos), corre:

```powershell
python tools/generate_celebration_gif.py
python tools/generate_demo_gif.py
python tools/generate_demo_video.py  # Requires ffmpeg; on Windows uses gdigrab
python tools/generate_assets_pack.py  # Generate placeholder branding assets (icon, splash)
```

Esto generará `assets/ui/celebration.gif` y `assets/ui/demo_gif.gif`. Los GIFs son opcionales; ZDex mostrará una versión programática si no existen.


### Opción 2: Módulo directo

```powershell
python -m zdex.app
```

---

## 📖 Guía de usuario

### 1. Iniciar la aplicación

```powershell
python run_zdex.py
```

Verás la ventana principal de ZDex con:

- **Panel izquierdo**: Vista de cámara (negro hasta que inicies)
- **Panel derecho superior**: Información de especies detectadas
- **Panel derecho inferior**: Historial de capturas

### 2. Activar la cámara


1. Haz clic en el botón **"Iniciar cámara"**
2. Permite el acceso a la webcam si el sistema lo solicita
3. Espera unos segundos mientras se inicializa la detección

### 3. Detectar un animal

1. Apunta la cámara hacia un animal (puede ser una mascota, foto, o video)
2. El sistema dibujará un **recuadro verde** alrededor del animal detectado
3. Verás el nombre y confianza sobre el recuadro (ej: "Dog 89.5%")

### 4. Capturar un animal

1. Cuando veas un animal detectado, el botón **"¡Capturar!"** se activará
2. **Opcional**: Edita la **Ubicación** (por defecto: Santiago, Chile)
3. **Opcional**: Añade **Notas** (ej: "En el parque", "Mi perro Max")
4. Haz clic en **"¡Capturar!"**
5. Verás una animación de flash en la cámara
6. Se guardará la imagen en `data/captures/`
7. La información de Wikipedia aparecerá en el panel derecho

### 5. Ver información detallada

El panel superior derecho muestra:

- **Nombre común** del animal
- **Nombre científico**
- **Resumen de Wikipedia** (español o inglés)
- **Imagen de referencia** de Wikipedia
- **Historial de avistamientos**: cuántas veces has visto este animal
- **Última ubicación** donde lo viste
- **Última fecha** de avistamiento

### 6. Revisar historial

El panel inferior derecho muestra:

- Lista de todos los animales capturados
- Número de avistamientos por especie
- Última fecha y ubicación

---

## 🎯 Ejemplos de uso

### Caso 1: Mascota en casa

```text
1. Iniciar cámara
2. Apuntar a tu perro/gato
3. Esperar detección (recuadro verde)
4. Escribir ubicación: "Casa - Sala"
5. Añadir nota: "Mi perro Max jugando"
6. Click en ¡Capturar!
```

### Caso 2: Video de National Geographic

```text
1. Reproducir video de animal salvaje en pantalla
2. Apuntar cámara a la pantalla
3. Esperar detección
4. Escribir ubicación: "Documental - África"
5. Click en ¡Capturar!
```

### Caso 3: Fotos impresas

```text
1. Tener foto impresa de animal
2. Apuntar cámara a la foto
3. Esperar detección
4. Capturar
```


---

## 🗂️ Estructura del proyecto

```
PDI_v2/
├── zdex/                              # Paquete principal
│   ├── __init__.py
│   ├── app.py                         # Aplicación Tkinter principal
│   ├── camera.py                      # Control de webcam
│   ├── config.py                      # Configuración global
│   ├── data_store.py                  # Persistencia JSON
│   ├── detector.py                    # YOLOv12 + SpeciesNet
│   ├── pipeline.py                    # Pipeline de detección async
│   ├── species.py                     # Índice de especies
│   ├── wikipedia_client.py            # Cliente Wikipedia
│   └── ui/
│       ├── camera_canvas.py           # Canvas de video con overlays
│       ├── panels.py                  # Paneles de información
│       └── styles.py                  # Estilos ttk
├── data/
│   ├── captures/                      # Imágenes capturadas
│   └── captures.json                  # Historial persistente
├── models/
│   └── yolov12m.pt                    # Detector YOLOv12 (auto-descarga)
├── yolov12/                           # Repo YOLOv12 clonado
├── full_image_*.pt                    # Modelo SpeciesNet
├── full_image_*.labels.txt            # Labels SpeciesNet
├── run_zdex.py                        # Launcher script
└── README.md                          # Este archivo
```

---

## 🔬 Tecnologías utilizadas

### Detección de objetos
- **YOLOv12-turbo**: Última versión de YOLO (2025)
- **Arquitectura**: Attention-centric real-time detection
- **Clases COCO filtradas**: bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe

### Clasificación de especies
- **SpeciesNet v4.0.1b**: Modelo de Google para conservación animal
- **Arquitectura**: EfficientNetV2-M backbone + 22x8 classifier
- **Dataset**: 65M imágenes de cámaras trampa (Wildlife Insights + LILA + iWildcam)
- **Precisión**: 94.5% en predicción de especie, 99.4% detección de animales

### Aceleración de hardware
- **DirectML**: Soporte para GPUs AMD en Windows
- **Fallback inteligente**: CUDA → MPS → DirectML → CPU

### Interfaz
- **Tkinter**: GUI nativa de Python
- **ttk**: Widgets con estilos modernos
- **PIL/Pillow**: Procesamiento de imágenes

### Enriquecimiento de datos
- **Wikipedia-API**: Información de especies en múltiples idiomas
- **Wikimedia REST API**: Imágenes de referencia

---

## ⚙️ Configuración avanzada

### Cambiar umbral de confianza

Edita `zdex/config.py`:

```python
DETECTION_CONFIDENCE_THRESHOLD = 0.35  # Valor por defecto
# Aumentar para menos falsos positivos (0.5-0.7)
# Disminuir para más detecciones (0.2-0.3)
```

### Cambiar cámara

Si tienes múltiples cámaras:

```python
# En config.py
CAMERA_DEVICE_ID = 0  # Primera cámara
# CAMERA_DEVICE_ID = 1  # Segunda cámara, etc.
```

### Cambiar idioma de Wikipedia

```python
# En config.py
WIKIPEDIA_LANG_PRIORITY = ("es", "en")  # Español primero, inglés fallback
# WIKIPEDIA_LANG_PRIORITY = ("en", "es")  # Inglés primero
```

### Cambiar ubicación por defecto

```python
# En config.py
DEFAULT_LOCATION = "Santiago, Chile"  # Cambiar a tu ciudad
```

---

## 🐛 Solución de problemas

### La cámara no se abre

**Error**: `No se pudo abrir la cámara (device_id=0)`

**Soluciones**:

1. Verifica que otra app no esté usando la cámara (Zoom, Teams, etc.)
2. Permite acceso a la cámara en Windows:
   - Configuración → Privacidad → Cámara → Permitir apps de escritorio
3. Prueba con otra cámara ID en `config.py` (`CAMERA_DEVICE_ID = 1`)

### La detección es muy lenta

**Problema**: FPS bajo, detecciones retrasadas

**Soluciones**:

1. Cierra otras aplicaciones pesadas
2. Reduce resolución de cámara en `config.py`:

   ```python
   FRAME_DISPLAY_MAX_WIDTH = 640
   FRAME_DISPLAY_MAX_HEIGHT = 480
   ```

3. Aumenta intervalo de detección:

   ```python
   DETECTION_INTERVAL_MS = 500  # Detectar cada 500ms
   ```

### No detecta mi animal

**Problema**: El recuadro verde no aparece

**Causas posibles**:

1. **Animal no está en clases COCO**: YOLOv12 solo detecta: perros, gatos, pájaros, caballos, ovejas, vacas, elefantes, osos, cebras, jirafas
2. **Confianza muy baja**: Reduce `DETECTION_CONFIDENCE_THRESHOLD` en config.py
3. **Iluminación mala**: Mejora la luz de la escena
4. **Animal muy pequeño**: Acércate más o usa zoom

### Error de DirectML

**Error**: `TypeError: '>=' not supported between instances of 'torch.device' and 'int'`

**Solución**: Ya corregido en `detector.py`. Si persiste:

```powershell
pip uninstall torch-directml
pip install torch-directml --upgrade
```

### Wikipedia no carga imágenes

**Problema**: Panel derecho sin imagen de referencia

**Soluciones**:

1. Verifica conexión a internet
2. Algunos animales no tienen imagen en Wikipedia
3. Revisa logs para ver errores de red


---

## 📊 Rendimiento esperado

### Tiempos de respuesta (AMD RX 6700 XT)

| Tarea | Tiempo esperado |
|-------|-----------------|
| Inicio de app | 5-10 s (carga de modelos) |
| Apertura de cámara | 1-2 s |
| Detección YOLO | 200-400 ms/frame |
| Clasificación SpeciesNet | 300-500 ms |
| Total por frame | < 1 s |

### Uso de recursos

| Recurso | Consumo típico |
|---------|----------------|
| RAM | 4-6 GB |
| VRAM (GPU) | 2-4 GB |
| CPU | 20-40% |
| GPU | 40-60% |

---

## 🤝 Créditos

### Modelos y datasets

- **YOLOv12**: [sunsmarterjie/yolov12](https://github.com/sunsmarterjie/yolov12)
- **SpeciesNet**: [Google CameraTrapAI](https://github.com/google/cameratrapai)
- **Wildlife Insights**: Dataset de cámaras trampa
- **COCO Dataset**: Clases de animales

### Bibliotecas

- **PyTorch**: Framework de deep learning
- **DirectML**: Aceleración AMD GPU
- **OpenCV**: Procesamiento de video
- **Wikipedia-API**: Enriquecimiento de información

---

## 📝 Licencia

Este proyecto es académico, desarrollado para el curso de Procesamiento Digital de Imágenes.

**Uso de modelos pre-entrenados**:

- YOLOv12: GPL-3.0 License
- SpeciesNet: Apache-2.0 License

---

## 👥 Autores

**Grupo PDI v2**:

- Clemente Mujica
- Cristóbal Moraga
- Felipe Tapia
- Iván Weber
- Camilo Troncoso


**Universidad**: [Tu Universidad]  
**Curso**: Procesamiento Digital de Imágenes  
**Fecha**: Noviembre 2025

---

## 📧 Soporte

Si encuentras problemas:

1. Revisa la sección **Solución de problemas**
2. Verifica los logs en terminal
3. Asegúrate de tener todas las dependencias instaladas
4. Contacta al equipo de desarrollo

---

<div align="center">

**¡Disfruta identificando animales con ZDex!** 🦁🔍

</div>
