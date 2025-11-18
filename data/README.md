# Directorio de Datos de ZDex

Este directorio almacena todos los datos persistentes generados por el usuario y la aplicación ZDex.

El contenido de esta carpeta **no debe** ser versionado (ignorado por Git) si contiene información sensible del usuario, pero sí debe existir para que la aplicación funcione correctamente.

## Contenido

* **`captures.json`**
    * **Propósito**: La "base de datos" principal del historial de avistamientos.
    * **Gestionado por**: `data_store.py`
    * **Contenido**: Un archivo JSON que contiene un objeto por cada especie detectada, con una lista de todos los `CaptureEvent` (avistamientos) asociados a ella.

* **`stats.json`**
    * **Propósito**: Almacena el progreso de gamificación del usuario.
    * **Gestionado por**: `gamification.py`
    * **Contenido**: Un archivo JSON que guarda las estadísticas generales (ej. "total de capturas") y el estado de los logros (cuáles están desbloqueados, progreso actual).

* **`captures/` (Directorio)**
    * **Propósito**: Almacena las imágenes (fotos) guardadas en cada avistamiento.
    * **Gestionado por**: `app.py` (al llamar a `STORE.record_capture`)
    * **Contenido**: Archivos de imagen (ej. `.jpg`) a los que se hace referencia en `captures.json` (a través del campo `image_path`).
