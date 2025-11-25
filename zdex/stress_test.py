"""
Script de Stress Test para ZDex.
Genera 100,000+ eventos sintéticos para validar robustez, métricas y visualización.
"""
import json
import random
import time
import math
from pathlib import Path
from datetime import datetime, timedelta

from zdex import config
from zdex.metrics import METRICS

DATASET_SOURCES = [
    "NatGeo Megafauna","African Savannah 4K","Amazon Rainforest Survey",
    "Arctic Wildlife Watch","Indo-Pacific Coral Cam","Urban Biodiversity 24/7"
]

ENVIRONMENTS = [
    "selva tropical","sabana","tundra","desierto","humedal","urbano nocturno",
    "bosque templado","costa rocosa","glaciar","pantano"
]

LIGHTING_CONDITIONS = [
    "amanecer","mediodía","atardecer","noche","tormenta","nublado",
    "niebla","luz artificial","luna llena","contraluz"
]

WEATHER_CONDITIONS = [
    "soleado","lluvia ligera","tormenta eléctrica","nevando","ventoso",
    "calima","granizo","niebla densa","monzón","huracán"
]

CAMERA_PROFILES = [
    "DJI-M600-Pro","GoPro-Hero12","Sony-A7R-V","Nikon-Z9","Canon-R5",
    "Bosch-PTZ-IP","RaspberryPi-Cam","Thermal-XT2","Intel-RealSense"
]

def load_species_list():
    """Load a large list of species from taxonomy_release.txt"""
    species = []
    taxonomy_path = Path("taxonomy_release.txt")
    if taxonomy_path.exists():
        with open(taxonomy_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(";")
                if len(parts) >= 7:
                    name = parts[6]
                    if name:
                        species.append(name)
    
    # Fallback if file not found or empty
    if not species:
        species = [
            "domestic dog", "domestic cat", "human", "brown bear", 
            "eagle", "giraffe", "elephant", "lion", "tiger", "wolf",
            "red fox", "bald eagle", "giant panda", "polar bear", "kangaroo",
            "koala", "platypus", "cheetah", "leopard", "jaguar"
        ]
    return species

def generate_stress_data(num_events=100000):
    print(f"🚀 Iniciando Stress Test EXTENSO: Generando {num_events} eventos...")
    print("🔥 Modo: DESPIADADO (Alta variabilidad, picos de latencia, errores)")
    
    species_list = load_species_list()
    print(f"📚 Catálogo de especies cargado: {len(species_list)} especies únicas.")
    
    # Simulate data over a longer period (e.g., 7 days) to show trends
    days_history = 7
    base_time = datetime.now().timestamp() - (days_history * 24 * 3600)
    
    events = []
    
    # Batch generation for performance
    batch_size = 1000
    
    for i in range(num_events):
        # Non-linear time distribution (bursts of activity)
        # Base progression + random bursts
        progress = i / num_events
        time_offset = progress * (days_history * 24 * 3600)
        
        # Add "burst" noise to timestamp (clusters of events)
        if random.random() < 0.1: # 10% chance of being in a burst
            time_offset += random.uniform(0, 300) # Within 5 minutes
        
        current_time = base_time + time_offset
        
        # 1. Evento de Detección
        # Latency: Mixture of distributions
        # 80% Normal operation: ~2.2s
        # 15% High load: ~4.5s
        # 5%  Severe lag/Timeout: >5s (up to 15s)
        rand_lat = random.random()
        if rand_lat < 0.80:
            latency = random.normalvariate(2200, 500)
        elif rand_lat < 0.95:
            latency = random.normalvariate(4500, 800)
        else:
            latency = random.uniform(5000, 15000) # SPIKES!
            
        if latency < 100: latency = 100
        
        # Confidence:
        # Most are high, but some are very low (difficult detections)
        if random.random() < 0.1:
            confidence = random.uniform(0.3, 0.6) # Low confidence
        else:
            confidence = random.uniform(0.6, 0.99)
        
        species = random.choice(species_list)
        dataset_source = random.choice(DATASET_SOURCES)
        environment = random.choice(ENVIRONMENTS)
        lighting = random.choice(LIGHTING_CONDITIONS)
        weather = random.choice(WEATHER_CONDITIONS)
        camera_profile = random.choice(CAMERA_PROFILES)
        scene_complexity = random.randint(1, 10)
        session_id = f"session-{i // 5000:03d}"
        geo_hint = random.choice([
            "Amazonas, BR","Serengeti, TZ","Sahara, DZ","Patagonia, AR",
            "Yosemite, US","Atacama, CL","Sumatra, ID","Queensland, AU",
            "Alpes, FR","Andes, PE"
        ])
        
        detection_event = {
            "event": "detection",
            "timestamp": current_time,
            "species_name": species,
            "detection_confidence": confidence,
            "classification_score": random.uniform(0.7, 0.99),
            "latency_ms": latency,
            "bbox_area": random.randint(5000, 1000000), # Tiny to huge
            "detections_in_frame": random.randint(1, 5), # Crowded scenes
            "dataset_source": dataset_source,
            "environment": environment,
            "lighting": lighting,
            "weather": weather,
            "camera_profile": camera_profile,
            "scene_complexity": scene_complexity,
            "session_id": session_id,
            "geolocation_hint": geo_hint
        }
        events.append(detection_event)
        
        # 2. Evento de Captura (aprox 15% de las detecciones se capturan)
        if random.random() < 0.15:
            capture_latency = latency + random.uniform(100, 1000)
            
            # Accuracy Simulation
            # Target is >= 80%. Let's simulate around 85-90% but with dips.
            # Difficult species or low confidence -> higher chance of error
            error_chance = 0.10
            if confidence < 0.5: error_chance += 0.30
            if latency > 5000: error_chance += 0.10 # System stress leads to errors?
            
            is_correct = random.random() > error_chance
            
            ground_truth = species if is_correct else random.choice(species_list)
            
            capture_event = {
                "event": "capture",
                "timestamp": current_time + 0.2,
                "predicted_name": species,
                "ground_truth_name": ground_truth,
                "correct": is_correct,
                "detection_confidence": confidence,
                "classification_score": random.uniform(0.7, 0.99),
                "latency_ms": capture_latency,
                "auto_capture": random.choice([True, False]),
                "dataset_source": dataset_source,
                "environment": environment,
                "lighting": lighting,
                "weather": weather,
                "camera_profile": camera_profile,
                "scene_complexity": scene_complexity,
                "session_id": session_id,
                "geolocation_hint": geo_hint
            }
            events.append(capture_event)
        
        if i % 10000 == 0:
            print(f"⏳ Generados {i}/{num_events} eventos...")
            
    # Escribir a archivo
    output_path = config.DATA_DIR / "metrics" / "events.jsonl"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"💾 Guardando {len(events)} eventos en {output_path}...")
    
    with open(output_path, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
            
    print("✅ Stress Test EXTENSO completado exitosamente.")

if __name__ == "__main__":
    generate_stress_data(100000)
