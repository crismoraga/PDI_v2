#!/usr/bin/env python3
"""
Script de prueba para verificar detección YOLO directamente.
Descarga una imagen de prueba y ejecuta la detección.
"""

import logging
import cv2
import numpy as np
from zdex import config
from zdex.detector import ENGINE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("\n=== TEST DE DETECCIÓN YOLO ===\n")
    
    # Descargar imagen de prueba (perro)
    print("1. Descargando imagen de prueba...")
    import urllib.request
    test_url = "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=640"
    
    try:
        req = urllib.request.Request(
            test_url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response:
            arr = np.asarray(bytearray(response.read()), dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        print(f"   ✓ Imagen descargada: {img.shape}")
    except Exception as e:
        print(f"   ✗ Error descargando imagen: {e}")
        print("   Usando imagen sintética...")
        img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Ejecutar detección
    print("\n2. Ejecutando detección...")
    detections = ENGINE.infer(img)
    
    # Mostrar resultados
    print(f"\n3. Resultados:")
    print(f"   Total detecciones: {len(detections)}")
    
    if detections:
        print("\n   Detalles:")
        for i, det in enumerate(detections):
            print(f"   [{i+1}] {det.primary_label.label.common_name}")
            print(f"       Confianza: {det.detection_confidence:.2%}")
            print(f"       Bbox: {det.bbox}")
            print(f"       Clasificación: {det.primary_label.score:.2%}")
    else:
        print("   ⚠ No se detectaron animales")
        print("\n   Posibles causas:")
        print("   - Imagen no contiene animales de las 10 clases COCO soportadas")
        print("   - Umbral de confianza muy alto (actual: {:.2f})".format(config.DETECTION_CONFIDENCE_THRESHOLD))
        print("   - Problemas con DirectML en primera inferencia")
        print("\n   Clases soportadas:")
        print("   ", config.ANIMAL_CLASS_IDS)
    
    print("\n=== FIN DEL TEST ===\n")

if __name__ == "__main__":
    main()
