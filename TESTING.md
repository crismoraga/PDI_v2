# 🧪 Guía de Prueba Rápida - ZDex v2.1

## ✅ DETECCIÓN CONFIRMADA FUNCIONANDO

### Test realizado:
```
✓ Imagen: Perro de Unsplash (640x427)
✓ Detección: 94.65% confianza
✓ Clasificación: "domestic dog" (48.18%)
✓ Bbox: (230, 59, 639, 422)
✓ Sin errores de warmup
```

---

## 🚀 Cómo Probar la Aplicación

### Método 1: Script de Test Automático

```powershell
python test_detection.py
```

**Resultado esperado**:
```
=== TEST DE DETECCIÓN YOLO ===

1. Descargando imagen de prueba...
   ✓ Imagen descargada: (427, 640, 3)

2. Ejecutando detección...
   Animal detectado! Clase COCO 16, confianza 94.65%

3. Resultados:
   Total detecciones: 1
   [1] domestic dog
       Confianza: 94.65%
       Bbox: (230, 59, 639, 422)
       Clasificación: 48.18%
```

---

### Método 2: Aplicación Completa con Webcam

#### Paso 1: Abrir imagen de perro en otra ventana

**Opción A**: Google Images
1. Abre Chrome/Edge
2. Busca "golden retriever"
3. Abre imagen grande (F11 pantalla completa)

**Opción B**: Descargar y abrir
```powershell
# Descargar imagen de prueba
Invoke-WebRequest -Uri "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=800" -OutFile "test_dog.jpg"

# Abrir con visor de fotos
start test_dog.jpg
```

#### Paso 2: Ejecutar ZDex

```powershell
python run_zdex.py
```

#### Paso 3: Iniciar Cámara

1. Click en **"Iniciar cámara"**
2. Espera 2-3 segundos (carga modelos)

Logs esperados:
```
INFO - Iniciando captura de cámara (device_id=0)...
INFO - Cámara abierta correctamente
INFO - Loop de detección iniciado
```

#### Paso 4: Apuntar Webcam a Imagen

1. Apunta tu webcam a la pantalla donde está la imagen del perro
2. Mantén estable 2-3 segundos
3. **Verás**:
   - Recuadro rosa alrededor del perro
   - Label: "Dog (XX%)"
   - Punto verde arriba a la izquierda
   - Botón "¡Capturar!" se activa

Logs esperados:
```
INFO - Animal detectado! Clase COCO 16, confianza 0.XX
INFO - ¡Animal detectado! 1 detección(es): ['domestic dog']
```

---

## 🐾 Animales Soportados (10 clases COCO)

| ID | Nombre Inglés | Nombre Español |
|----|---------------|----------------|
| 16 | dog | perro |
| 17 | cat | gato |
| 14 | bird | pájaro |
| 18 | horse | caballo |
| 19 | sheep | oveja |
| 20 | cow | vaca |
| 21 | elephant | elefante |
| 22 | bear | oso |
| 23 | zebra | cebra |
| 24 | giraffe | jirafa |

**Recomendación**: Usa fotos de **perros** o **gatos** para testing, son las más fáciles de detectar.

---

## ⚙️ Parámetros Actuales

```python
DETECTION_CONFIDENCE_THRESHOLD = 0.25  # 25% mínimo
DETECTION_INTERVAL_MS = 300            # Cada 300ms
POLL_INTERVAL_MS = 33                  # ~30 FPS UI

# YOLO predict()
imgsz = 640              # Tamaño óptimo
conf = 0.25              # Umbral confianza
iou = 0.45               # NMS threshold
max_det = 10             # Máximo 10 detecciones
```

---

## 🔧 Ajustes Opcionales

### Si detecta demasiado (falsos positivos):

```python
# En config.py
DETECTION_CONFIDENCE_THRESHOLD = 0.40  # Subir a 40%
```

### Si no detecta nada (poca sensibilidad):

```python
# En config.py
DETECTION_CONFIDENCE_THRESHOLD = 0.15  # Bajar a 15%
```

### Si va muy lento:

```python
# En config.py
DETECTION_INTERVAL_MS = 500  # Detectar cada 500ms en lugar de 300ms
```

---

## 📊 Rendimiento Esperado (RX 6700 XT + DirectML)

| Métrica | Valor |
|---------|-------|
| Primera inferencia | 800-1500ms |
| Inferencias subsecuentes | 200-500ms |
| FPS UI | ~30 |
| Detecciones por segundo | ~3 |
| Uso de VRAM | ~2-3 GB |
| Uso de RAM | ~4-6 GB |

---

## ✅ Verificación Final

### Checklist completo:

- [ ] `python test_detection.py` detecta perro (>90% confianza)
- [ ] `python run_zdex.py` abre ventana sin errores
- [ ] Click "Iniciar cámara" muestra feed de webcam
- [ ] Apuntar a foto de perro muestra recuadro rosa
- [ ] Logs muestran "Animal detectado! Clase COCO 16"
- [ ] Botón "¡Capturar!" se activa
- [ ] Click en "¡Capturar!" guarda imagen en `data/captures/`
- [ ] Panel derecho muestra info de Wikipedia
- [ ] Historial muestra contador de capturas

---

## 🆘 Problemas Comunes

### ❌ No detecta nada

**Diagnóstico**:
```powershell
# Revisa logs
python run_zdex.py 2>&1 | Select-String "Animal detectado"

# Si no aparece nada, baja el umbral
# config.py: DETECTION_CONFIDENCE_THRESHOLD = 0.15
```

### ❌ "Error en predicción YOLO"

**Solución**: Ya corregido en v2.1. Si ves este error, actualiza:
```powershell
git pull  # Si usas git
# O descarga última versión
```

### ❌ Webcam no abre

```powershell
# Verifica que no esté en uso
Stop-Process -Name "Teams", "Zoom", "Skype" -Force

# Prueba con otra cámara
# config.py: CAMERA_DEVICE_ID = 1
```

---

<div align="center">

**¡La detección está confirmada funcionando!** 🎉

*Última prueba: 2025-11-05 21:02:18*
*Test: Perro detectado con 94.65% confianza*

</div>
