"""Generate a small celebration GIF for the app using Pillow.

Run:
    python tools/generate_celebration_gif.py

Outputs:
    assets/ui/celebration.gif

This is a simple programmatic placeholder to create a small confetti-like animation
that can be used for 'animal new' celebrations. You can replace the GIF with a
fancier one if you have an artist or a stock asset.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "ui" / "celebration.gif"
OUT.parent.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 220, 220
FRAMES = 18

colors = ["#ffcc00", "#ff5252", "#00e676", "#29b6f6", "#9c27b0"]

frames = []
for i in range(FRAMES):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    # minimal confetti
    for j in range(18):
        c = colors[j % len(colors)]
        x = int(WIDTH * (j / 18.0) + ((i * (j % 5 + 1)) % 20) - 10)
        y = int((i * 10 + j * 12) % HEIGHT)
        draw.ellipse((x, y, x + 6, y + 6), fill=c)
    # draw a banner text
    try:
        font = ImageFont.truetype("Arial.ttf", 24)
    except Exception:
        font = ImageFont.load_default()
    text = "¡NUEVO!"
    # Pillow compatibility: prefer textbbox (newer), fallback to font.getsize
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except Exception:
        try:
            tw, th = font.getsize(text)
        except Exception:
            # Fallback static size
            tw, th = (60, 16)
    draw.text(((WIDTH - tw) / 2, HEIGHT - th - 12), text, fill="#ffffff", font=font)
    frames.append(img)

frames[0].save(OUT, format="GIF", save_all=True, append_images=frames[1:], optimize=True, duration=80, loop=0)
print("Generated celebration GIF:", OUT)
