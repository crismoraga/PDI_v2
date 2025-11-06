# 🎮 ZDex v3.0 - Gamificación & UI Mejorada

## ✨ Nuevas Características Implementadas

### 1. **Captura Automática** ⏱️
- Se captura automáticamente después de **5 segundos** de detección continua
- Contador visual en pantalla
- Animación de cuenta regresiva

### 2. **Geolocalización Automática** 📍
- Ubicación obtenida automáticamente vía IP
- Servicio: ipapi.co (sin API key)
- Muestra: Ciudad, Región, País
- Actualización automática al iniciar app

### 3. **Sistema de Gamificación** 🏆

#### Logros Desbloqueables:
- 🎯 **Primera Captura**: Tu primer animal
- 🗺️ **Explorador**: 10 especies diferentes
- 🔬 **Investigador**: 25 especies diferentes
- 🌿 **Naturalista**: 50 especies diferentes
- ⭐ **Dedicado**: 100 capturas totales
- 👑 **Maestro ZDex**: 500 capturas totales
- 🐕 **Amante de Perros**: 10 perros capturados
- 🐈 **Amante de Gatos**: 10 gatos capturados
- 🦅 **Observador de Aves**: 15 aves capturadas
- 🌍 **Explorador Global**: Animales en 5 ubicaciones diferentes

#### Estadísticas Rastreadas:
- Total de capturas
- Especies únicas descubiertas
- Mejor confianza de detección por especie
- Primera y última vez visto
- Ubicaciones donde fue visto
- Top 5 especies más capturadas

### 4. **Interfaz Mejorada** 🎨

#### Animaciones:
- ✨ Fade-in suave de paneles
- 🌟 Efecto "glow" en detecciones
- 📸 Animación de flash mejorada
- ⏳ Contador de auto-captura animado
- 🏆 Notificaciones de logros desbloqueados

#### Colores & Estilo:
- Paleta modernizada
- Botones con efectos hover/press
- Indicadores de estado animados
- Gradientes sutiles
- Mejor contraste y legibilidad

### 5. **Panel de Avistamientos** 📊

Muestra:
- **Total de capturas**
- **Especies descubiertas**
- **Logros desbloqueados** (X/10)
- **Top 5 especies más vistas**
  - Nombre común
  - Total de avistamientos
  - Última vez visto
  - Ubicaciones visitadas

### 6. **Wikipedia en Español** 🌐
- Prioridad: Español (es) → Inglés (en)
- Información permanece hasta nueva detección
- Traducción de nombres científicos
- Resumen latinoamericano cuando disponible

---

## 📂 Archivos Nuevos

### `zdex/geolocation.py`
```python
"""
Geolocalización automática usando IP.
- Servicio: ipapi.co
- Sin API key requerida
- Cache de ubicación
- Fallback a "Ubicación desconocida"
"""
```

### `zdex/gamification.py`
```python
"""
Sistema completo de gamificación.
- Gestión de logros
- Estadísticas por especie
- Persistencia JSON
- Detección automática de desbloqueos
"""
```

### `data/stats.json` (Auto-generado)
```json
{
  "species": {
    "domestic_dog": {
      "species_name": "domestic_dog",
      "common_name": "domestic dog",
      "total_sightings": 15,
      "first_seen": "2025-11-05T21:00:00",
      "last_seen": "2025-11-05T21:30:00",
      "locations": ["Santiago, Región Metropolitana, Chile"],
      "best_confidence": 0.9465
    }
  },
  "total_captures": 42
}
```

### `data/achievements.json` (Auto-generado)
```json
{
  "first_capture": {
    "id": "first_capture",
    "name": "Primera Captura",
    "unlocked": true,
    "unlock_date": "2025-11-05T21:05:00",
    "progress": 1,
    "target": 1
  }
}
```

---

## 🎯 Flujo de Usuario Mejorado

### 1. **Inicio**
```
1. Abre ZDex
2. Geolocalización detecta: "Santiago, Chile" automáticamente
3. Panel muestra: "0 capturas | 0/10 logros"
4. Click "Iniciar cámara"
```

### 2. **Detección**
```
1. Apunta cámara a perro
2. Recuadro rosa aparece con animación
3. Contador aparece: "Auto-captura en 5s..."
4. Info Wikipedia carga en español
5. Al llegar a 0s → ¡Captura automática!
```

### 3. **Captura Automática**
```
1. Flash animado (blanco brillante)
2. Notificación: "🏆 ¡Logro desbloqueado! Primera Captura"
3. Stats actualizadas: "1 captura | 1/10 logros"
4. Panel avistamientos muestra: "Perro doméstico (1)"
5. Ubicación guardada: "Santiago, Chile"
```

### 4. **Avistamientos**
```
Panel inferior derecho muestra:

📊 ESTADÍSTICAS
Total de capturas: 42
Especies descubiertas: 7
Logros desbloqueados: 3/10

🏆 LOGROS RECIENTES
✅ Primera Captura
✅ Explorador
⏳ Investigador (7/25)

🐾 TOP ESPECIES
1. 🐕 Perro doméstico - 15 avistamientos
   Última vez: Hace 2 minutos
   Ubicaciones: Santiago

2. 🐈 Gato doméstico - 8 avistamientos
   Última vez: Hace 10 minutos
   Ubicaciones: Santiago

...
```

---

## 🚀 Cómo Usar las Nuevas Características

### Captura Automática
```python
# config.py
AUTO_CAPTURE_THRESHOLD_SECONDS = 5.0  # Cambiar a 3.0 para 3 segundos
```

### Geolocalización Manual
```python
from zdex.geolocation import GEOLOCATOR

# Refrescar ubicación
location = GEOLOCATOR.refresh_location()
print(location.display_name)  # "Santiago, Región Metropolitana, Chile"
```

### Estadísticas Programáticas
```python
from zdex.gamification import GAMIFICATION

# Ver resumen
summary = GAMIFICATION.get_stats_summary()
print(f"Total: {summary['total_captures']}")
print(f"Especies: {summary['unique_species']}")

# Ver logros
unlocked = GAMIFICATION.get_unlocked_achievements()
for achievement in unlocked:
    print(f"{achievement.icon} {achievement.name}")
```

---

## ⚙️ Configuración Avanzada

### Ajustar Tiempo de Auto-Captura
```python
# zdex/config.py
AUTO_CAPTURE_THRESHOLD_SECONDS = 3.0  # Más rápido
AUTO_CAPTURE_THRESHOLD_SECONDS = 10.0  # Más lento
```

### Deshabilitar Auto-Captura
```python
# zdex/config.py
AUTO_CAPTURE_THRESHOLD_SECONDS = float('inf')  # Nunca auto-captura
```

### Cambiar Prioridad de Idioma Wikipedia
```python
# zdex/config.py
WIKIPEDIA_LANG_PRIORITY = ("es", "pt", "en")  # Español → Portugués → Inglés
```

---

## 🐛 Solución de Problemas

### Geolocalización no funciona
```
Error: "No se pudo obtener ubicación"
Solución: Verifica conexión a internet o usa ubicación manual:
```
```python
# En config.py
DEFAULT_LOCATION = "Tu Ciudad, Tu País"
```

### Logros no se desbloquean
```
1. Verifica data/achievements.json existe
2. Revisa logs: "🏆 ¡Logro desbloqueado!"
3. Borra achievements.json para reiniciar
```

### Auto-captura muy rápida/lenta
```python
# Ajustar en config.py
AUTO_CAPTURE_THRESHOLD_SECONDS = 7.0  # Tu preferencia
```

---

## 📊 Formato de Datos

### stats.json
```json
{
  "species": {
    "<species_key>": {
      "species_name": "scientific_name",
      "common_name": "Nombre común",
      "total_sightings": 10,
      "first_seen": "ISO-8601 timestamp",
      "last_seen": "ISO-8601 timestamp",
      "locations": ["Ubicación 1", "Ubicación 2"],
      "best_confidence": 0.95
    }
  },
  "total_captures": 100
}
```

### achievements.json
```json
{
  "<achievement_id>": {
    "id": "achievement_id",
    "name": "Nombre del Logro",
    "description": "Descripción",
    "icon": "🏆",
    "unlocked": true,
    "unlock_date": "ISO-8601 timestamp",
    "progress": 10,
    "target": 10
  }
}
```

---

<div align="center">

**🎮 ¡Gamificación completa implementada!**

*Captura automática • Geolocalización • Logros • Estadísticas • UI Mejorada*

</div>
