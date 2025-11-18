"""Generate a short demo GIF simulating the detection -> freeze -> new species flow.

Usage:
    python tools/generate_demo_gif.py

This creates a small GIF in assets/ui/demo_gif.gif suitable for README or release docs.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "ui" / "demo_gif.gif"
OUT.parent.mkdir(parents=True, exist_ok=True)
WIDTH, HEIGHT = 640, 360

frames = []
try:
    font = ImageFont.truetype("Arial.ttf", 22)
except Exception:
    from PIL import ImageFont

    font = ImageFont.load_default()

# Frame 1: camera feed with detection
for t in range(8):
    img = Image.new("RGB", (WIDTH, HEIGHT), (20, 20, 20))
    draw = ImageDraw.Draw(img)
    draw.rectangle((50, 30, 590, 330), outline=(40, 180, 99), width=3)
    draw.text((60, 40), "Detección: Perro (92%)", font=font, fill=(255, 255, 255))
    draw.text((60, 70), "Auto-capture: 2s", font=font, fill=(255, 255, 255))
    frames.append(img)

# Frame 2: freeze/pokedex effect
for t in range(8):
    img = Image.new("RGB", (WIDTH, HEIGHT), (10, 10, 40))
    draw = ImageDraw.Draw(img)
    draw.rectangle((60, 20, 580, 300), outline=(255, 255, 255), width=5)
    draw.text((80, 30), "¡ALTO! Detección de alta confianza — Vista estática", font=font, fill=(255, 215, 0))
    frames.append(img)

# Frame 3: new species popup
for t in range(12):
    img = Image.new("RGB", (WIDTH, HEIGHT), (20, 20, 20))
    draw = ImageDraw.Draw(img)
    draw.rectangle((260, 50, 620, 320), fill=(40, 40, 80))
    draw.text((280, 70), "ANIMAL NUEVO ENCONTRADO!", font=font, fill=(240, 240, 240))
    draw.text((280, 110), "Nombre: Perro doméstico", font=font, fill=(200, 200, 200))
    draw.text((280, 150), "Hábitat: Urbano, doméstico", font=font, fill=(200, 200, 200))
    draw.text((280, 190), "Dieta: Omnívoro", font=font, fill=(200, 200, 200))
    frames.append(img)

frames[0].save(OUT, format="GIF", save_all=True, append_images=frames[1:], optimize=True, duration=100, loop=0)
print("Generated demo GIF:", OUT)
