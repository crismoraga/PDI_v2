# Demo assets and sample GIF

This document describes how to generate and use the demo assets included in this repository.

## Generate the celebration GIF

```powershell
python tools/generate_celebration_gif.py
```
This creates: `assets/ui/celebration.gif`. The GIF shows confetti and `¡NUEVO!` text and is used by the "ANIMAL NUEVO ENCONTRADO" popup.

## Generate the demo GIF for documentation

```powershell
python tools/generate_demo_gif.py
```
This creates: `assets/ui/demo_gif.gif`. It simulates the detection -> freeze -> capture flow used in the README and docs.

## Tips
- Replace the generated GIFs with high-quality designs if you have a designer; the asset filenames are documented in `ZDex/app.py`.
