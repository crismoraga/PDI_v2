# 🚀 ZDex - Inicio Rápido

## ▶️ Ejecutar la aplicación

```powershell
python run_zdex.py
```

O alternativamente:

```powershell
python -m zdex.app
```

---

## 📝 Pasos para usar ZDex

### 1️⃣ Abrir aplicación
- Ejecuta `python run_zdex.py`
- Espera 5-10 segundos mientras cargan los modelos
- Verás la ventana de ZDex

### 2️⃣ Iniciar cámara
- Click en **"Iniciar cámara"**
- Permite acceso a webcam si el sistema lo solicita
- Espera 2-3 segundos

### 3️⃣ Detectar animal
- Apunta la cámara a un animal (mascota, foto, video)
- Verás un **recuadro verde** alrededor del animal
- El nombre aparece encima (ej: "Dog 89.5%")

### 4️⃣ Capturar
- El botón **"¡Capturar!"** se activa cuando hay detección
- (Opcional) Edita **Ubicación** y **Notas**
- Click en **"¡Capturar!"**
- Verás animación de flash ✨
- La info aparece en el panel derecho

### 5️⃣ Ver historial
- Panel inferior derecho muestra todos los animales capturados
- Contador de avistamientos por especie

---

## 🐛 Problemas comunes

### ❌ Cámara no abre
**Solución**: Cierra Zoom/Teams y permite acceso en Configuración de Windows

### ❌ No detecta mi animal
**Solución**: Solo detecta: perros, gatos, pájaros, caballos, ovejas, vacas, elefantes, osos, cebras, jirafas

### ❌ Muy lento
**Solución**: Cierra otras apps, reduce resolución en `config.py`

---

## ⚙️ Requisitos mínimos

- ✅ Python 3.10+
- ✅ Webcam (integrada o USB)
- ✅ 8 GB RAM
- ✅ GPU AMD (con DirectML) o CPU

---

## 📖 Documentación completa

Ver **README_ES.md** para:
- Instalación detallada
- Configuración avanzada
- Arquitectura del sistema
- Créditos y licencias

---

<div align="center">

**¡Empieza a capturar animales ahora!** 🦁🔍

</div>
