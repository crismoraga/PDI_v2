"""Generate corporate branding assets (placeholder) - icon, splash, GIF overlay
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "assets" / "ui"
OUT.mkdir(parents=True, exist_ok=True)

# small icon
icon = Image.new('RGBA', (256, 256), (176, 58, 126))
d = ImageDraw.Draw(icon)
d.ellipse((36,36,220,220), fill=(255,255,255))
icon.save(OUT / 'app_icon.png')

# splash
splash = Image.new('RGBA', (1280, 720), (15, 23, 42))
d = ImageDraw.Draw(splash)
try:
    f = ImageFont.truetype('Arial.ttf', 36)
except Exception:
    f = ImageFont.load_default()
d.text((60,60), 'ZDex - Pokédex de Animales', font=f, fill=(255,255,255))
splash.save(OUT / 'splash.png')

print('Generated branding assets in', OUT)
