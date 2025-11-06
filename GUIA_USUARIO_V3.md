# 🎮 ZDex v3.0 - Guía de Usuario Completa

## 🌟 Bienvenido a tu Pokédex de Animales Reales

ZDex ahora es una experiencia completa tipo Pokédex con gamificación, logros y auto-captura.

---

## 🚀 Inicio Rápido

### 1. Ejecutar la Aplicación

```powershell
python run_zdex.py
```

Verás:
```
INFO - Obteniendo ubicación automática...
INFO - Ubicación detectada: Viña del Mar, Región de Valparaíso, Chile
INFO - ZDex inicializado correctamente. Ventana lista.
```

### 2. Interfaz Principal

La ventana tiene 2 columnas:

**Izquierda: Cámara**
- Vista de cámara (negro hasta iniciar)
- Botón "Iniciar cámara"
- Botón "¡Capturar!" (se activa al detectar)
- Campos: Ubicación (auto-completado), Notas

**Derecha: Información (3 Tabs)**
- 📷 **Detección Actual**: Info del animal detectado
- 📖 **Pokédex**: Todas las especies capturadas
- 🏆 **Logros**: Estadísticas y achievements

---

## 📸 Capturar Animales

### Método 1: Captura Manual
1. Clic en "Iniciar cámara"
2. Apunta a un animal (mascota, foto, pantalla)
3. Espera 2-3 segundos
4. Aparece recuadro rosa con nombre
5. Clic en "¡Capturar!"

### Método 2: Auto-Captura (NUEVO) ⏱️
1. Iniciar cámara
2. Apunta a un animal
3. **Mantén quieto 5 segundos**
4. Verás countdown: "Auto-captura en 5s..."
5. ¡Captura automática!

---

## 🏆 Sistema de Logros

### Ver tus Logros
1. Clic en tab **"🏆 Logros"**
2. Verás:
   - Total de capturas
   - Especies descubiertas
   - Logros desbloqueados (X/10)
   - Top 5 especies

### Logros Disponibles

| Emoji | Logro | Requisito |
|-------|-------|-----------|
| 🎯 | Primera Captura | Captura 1 animal |
| 🗺️ | Explorador | 10 especies diferentes |
| 🔬 | Investigador | 25 especies diferentes |
| 🌿 | Naturalista | 50 especies diferentes |
| ⭐ | Dedicado | 100 capturas totales |
| 👑 | Maestro ZDex | 500 capturas totales |
| 🐕 | Amante de Perros | 10 perros capturados |
| 🐈 | Amante de Gatos | 10 gatos capturados |
| 🦅 | Observador de Aves | 15 aves capturadas |
| 🌍 | Explorador Global | Animales en 5 ubicaciones |

### Notificaciones
Cuando desbloqueas un logro:
- Ventana emergente con emoji grande
- Nombre del logro en verde
- Descripción
- Auto-cierra en 5 segundos

---

## 📖 Pokédex

### Navegación
1. Clic en tab **"📖 Pokédex"**
2. Scroll por la lista
3. Verás tarjetas para cada especie

### Información de Tarjetas

Cada tarjeta muestra:
- **#001** - Número Pokédex
- **🐕** - Emoji de la especie
- **"domestic dog"** - Nombre común
- **_Canis familiaris_** - Nombre científico
- **✕ 5** - Total de capturas
- **⏰ Hace 5 min** - Última vez visto
- **📍 Santiago, Chile** - Ubicación

### Emojis de Especies
- 🐕 Perros
- 🐈 Gatos  
- 🦅 Aves
- 🐴 Caballos
- 🐄 Vacas
- 🐘 Elefantes
- 🐻 Osos
- 🦁 Leones
- 🦓 Cebras
- 🦒 Jirafas
- Y más...

---

## 📊 Estadísticas

### Panel de Stats (Tab Logros)

**Sección 1: Resumen General**
```
🎯 Total de capturas: 25
🦋 Especies descubiertas: 8
🏆 Logros desbloqueados: 4/10
```

**Sección 2: Top 5 Especies**
```
🥇 domestic dog
   Avistamientos: 10 • Última vez: Hace 5 min
   Ubicaciones: Santiago, Viña del Mar

🥈 domestic cat
   Avistamientos: 7 • Última vez: Hace 1 hora
   Ubicaciones: Santiago

🥉 bird
   Avistamientos: 5 • Última vez: Hace 2 días
```

**Sección 3: Logros Desbloqueados**
```
🎯 Primera Captura
   Captura tu primer animal
   Desbloqueado: 2025-11-06T00:10:00Z
```

**Sección 4: Logros Por Desbloquear**
```
🐕 Amante de Perros
   Captura 10 perros diferentes
   Progreso: 5/10 (50%)
```

---

## 🌍 Geolocalización Automática

### Cómo Funciona
- Al iniciar la app, obtiene tu ubicación por IP
- Servicio: **ipapi.co** (gratis, sin registro)
- Formato: "Ciudad, Región, País"
- Se auto-completa en campo "Ubicación"

### Ejemplo de Log
```
INFO - Obteniendo ubicación automática...
INFO - Ubicación detectada: Viña del Mar, Región de Valparaíso, Chile
```

### Puedes Editarla
Si quieres cambiar la ubicación:
1. Edita el campo "Ubicación" antes de capturar
2. Escribe lo que quieras
3. Captura

---

## ⏱️ Auto-Captura Detallada

### Funcionamiento
1. **Detección Continua**: Detecta un animal
2. **Timer Inicia**: Comienza contador de 5 segundos
3. **Mismo Animal**: Si sigue siendo la misma especie
4. **Countdown Visual**: Muestra "Auto-captura en Xs..."
5. **Captura**: Al llegar a 0, captura automáticamente

### Reinicio del Timer
- **Nueva especie detectada**: Timer se resetea
- **Animal sale de cuadro**: Timer se resetea
- **Después de captura**: Timer se resetea

### Indicadores Visuales
- **Dot verde pulsante**: Detectando
- **Dot gris**: No detecta
- **Texto grande verde**: Countdown

---

## 🎨 Personalizaciones

### Colores Principales
```css
Header:    #1f84a3 (Azul)
Accent:    #b03a7e (Rosa)
Detection: #22c55e (Verde)
Panel:     #f9fbff (Gris claro)
```

### Tabs
- **📷 Detección Actual**: Info en tiempo real
- **📖 Pokédex**: Colección completa
- **🏆 Logros**: Progresión

### Animaciones
- **Flash de captura**: Gradiente blanco
- **Countdown**: Texto pulsante
- **Logros**: Ventana emergente animada
- **Tabs**: Transiciones suaves

---

## 💾 Datos Guardados

### Ubicación de Archivos
```
data/
├── captures.json          # Historial de capturas
├── stats.json            # Estadísticas de especies
└── achievements.json     # Progreso de logros
```

### Formato stats.json
```json
{
  "species_stats": {
    "canis": {
      "common_name": "domestic dog",
      "total_sightings": 10,
      "last_seen": "2025-11-06T00:15:00Z",
      "locations": ["Santiago", "Viña del Mar"],
      "best_confidence": 0.95
    }
  },
  "total_captures": 10
}
```

### Respaldo Manual
Copia la carpeta `data/` para hacer backup.

---

## 🔍 Tips y Trucos

### Maximizar Detecciones
✅ **Buena iluminación**: Apunta a luz natural
✅ **Animal quieto**: 2-3 segundos sin moverse
✅ **Distancia media**: Ni muy cerca ni muy lejos
✅ **Animal completo**: Que se vea todo el cuerpo

### Desbloquear Logros Rápido
1. **Primera Captura**: ¡Captura cualquier animal!
2. **Explorador**: Busca 10 especies diferentes
3. **Amante de Perros**: Enfócate en perros
4. **Explorador Global**: Viaja o usa fotos de diferentes lugares

### Usar Auto-Captura
- Ideal para animales quietos (mascotas durmiendo)
- No funciona si animal se mueve
- Perfecto para fotos en pantalla
- Útil cuando no puedes soltar la cámara

---

## 🐛 Solución de Problemas

### Auto-Captura No Funciona
**Problema**: No activa después de 5 segundos
**Solución**:
- Verifica que sea la **misma especie**
- Mantén animal **completamente quieto**
- Asegura **detección continua** (recuadro rosa)

### Ubicación Incorrecta
**Problema**: Muestra ciudad equivocada
**Solución**:
- Edita manualmente el campo
- Está basado en IP (puede variar)
- Sin conexión = "Ubicación desconocida"

### Logro No Se Desbloquea
**Problema**: Cumplí requisito pero no aparece
**Solución**:
- Cierra y abre tab "🏆 Logros"
- Verifica progreso en sección "Por Desbloquear"
- Revisa `data/achievements.json`

### Tab No Cambia
**Problema**: Clic en tab no funciona
**Solución**:
- Espera a que cargue contenido
- Cierra y abre aplicación
- Verifica logs en terminal

---

## 📱 Atajos y Shortcuts

| Acción | Atajo/Método |
|--------|--------------|
| Captura manual | Clic "¡Capturar!" |
| Auto-captura | Mantener 5s quieto |
| Ver logros | Tab "🏆 Logros" |
| Ver Pokédex | Tab "📖 Pokédex" |
| Info actual | Tab "📷 Detección" |
| Editar ubicación | Campo antes de capturar |
| Ver stats | Scroll en tab Logros |

---

## 🎯 Metas Sugeridas

### Corto Plazo (1 día)
- [ ] Desbloquear "Primera Captura" 🎯
- [ ] Capturar 5 especies diferentes
- [ ] Probar auto-captura
- [ ] Ver ubicación automática

### Medio Plazo (1 semana)
- [ ] Desbloquear "Explorador" 🗺️ (10 especies)
- [ ] Lograr 50 capturas totales
- [ ] Capturar en 3 ubicaciones
- [ ] Completar 5 logros

### Largo Plazo (1 mes)
- [ ] Desbloquear "Naturalista" 🌿 (50 especies)
- [ ] Lograr 500 capturas (Maestro ZDex 👑)
- [ ] Completar los 10 logros
- [ ] Top 5 especies con 20+ cada una

---

## 🔮 Próximas Funcionalidades

Ideas para futuras versiones:
- 🔊 Efectos de sonido
- 🌙 Modo oscuro
- 🔍 Búsqueda en Pokédex
- 📈 Gráficos de progreso
- 🎯 Desafíos diarios
- 📤 Exportar a PDF
- 🎨 Temas personalizados

---

## ❓ FAQ

**P: ¿Cuántas especies puede detectar?**
R: Miles. YOLOv12 detecta animales, SpeciesNet clasifica en +2000 especies.

**P: ¿Funciona sin internet?**
R: Parcialmente. Detección sí, pero no habrá Wikipedia ni geolocalización.

**P: ¿Los datos se guardan?**
R: Sí, en `data/` como JSON. Persisten entre sesiones.

**P: ¿Puedo resetear logros?**
R: Sí, elimina `data/achievements.json` y `data/stats.json`.

**P: ¿Auto-captura siempre es 5 segundos?**
R: Sí, configurado en `config.py` (AUTO_CAPTURE_THRESHOLD_SECONDS).

---

## 📞 Soporte

Si tienes problemas:
1. Revisa logs en terminal
2. Verifica archivos en `data/`
3. Lee secciones de Troubleshooting
4. Cierra y reabre la app

---

## 🎉 ¡Disfruta tu Pokédex!

**"Gotta catch 'em all!"** 🦁🐯🦅

Pero esta vez... **¡con animales reales!** 🌍

---

**Versión**: 3.0.0  
**Fecha**: Noviembre 6, 2025  
**Creado con**: 💚 para amantes de animales y fans de Pokémon
