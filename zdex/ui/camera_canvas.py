"""Canvas widget that renders the live camera feed with overlays."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Sequence

import numpy as np
from PIL import Image, ImageTk

from .. import config
from ..detector import DetectionResult


class CameraCanvas(ttk.Frame):
    """Displays camera frames and detection overlays within a ttk.Frame."""

    def __init__(self, master: tk.Misc, *, width: int | None = None, height: int | None = None) -> None:
        super().__init__(master, style="Primary.TFrame")
        self._width = width or config.FRAME_DISPLAY_MAX_WIDTH
        self._height = height or config.FRAME_DISPLAY_MAX_HEIGHT
        self._canvas = tk.Canvas(
            self,
            width=self._width,
            height=self._height,
            highlightthickness=0,
            background="black",
        )
        self._canvas.pack(fill="both", expand=True)
        self._photo: ImageTk.PhotoImage | None = None
        self._current_boxes: list[int] = []
        self._flash_tag = "capture_flash"
        self._status_tag = "status_indicator"
        self._countdown_tag = "auto_capture_countdown"
        self._frame_count = 0
        self._auto_capture_time_remaining: float | None = None
        # Focused crop (x1, y1, x2, y2) in canvas coordinates; when set, render only this region
        self._focus_bbox: tuple[int, int, int, int] | None = None

    def render(self, frame_bgr: np.ndarray, detections: Sequence[DetectionResult] = ()) -> None:
        if frame_bgr is None:
            return
        self._frame_count += 1
        image, scale, offset_x, offset_y = self._prepare_image(frame_bgr)
        # If a focus bbox is set (in original frame coords), crop the image around it and
        # scale to the full canvas for emphasis.
        if self._focus_bbox:
            try:
                # self._focus_bbox is in source frame coords; translate to canvas coords
                x1, y1, x2, y2 = self._focus_bbox
                x1 = int(x1 * scale + offset_x)
                y1 = int(y1 * scale + offset_y)
                x2 = int(x2 * scale + offset_x)
                y2 = int(y2 * scale + offset_y)
                # Expand a bit for nicer composition
                expand_x = int((x2 - x1) * 0.20)
                expand_y = int((y2 - y1) * 0.20)
                x1 -= expand_x
                y1 -= expand_y
                x2 += expand_x
                y2 += expand_y
                # Clamp
                x1 = max(0, min(self._width, x1))
                y1 = max(0, min(self._height, y1))
                x2 = max(0, min(self._width, x2))
                y2 = max(0, min(self._height, y2))
                cropped = image.crop((x1, y1, x2, y2))
                image = cropped.resize((self._width, self._height), Image.Resampling.LANCZOS)
                # Remove overlays when focused
                detections = ()
            except Exception:
                pass
        self._photo = ImageTk.PhotoImage(image=image)
        self._canvas.delete("frame")
        self._canvas.create_image(0, 0, anchor="nw", image=self._photo, tags="frame")
        self._draw_overlays(detections, scale, offset_x, offset_y)
        
        # Draw scanning line if detecting but not focused
        if detections and not self._focus_bbox:
            self._draw_scanning_line()
        else:
            self._canvas.delete("scan_line")
        
        # Status indicator: green pulsing dot when detecting

        self._canvas.delete(self._status_tag)
        color = config.DETECTION_PULSE_COLOR if detections else "#94a3b8"
        self._canvas.create_oval(
            10, 10, 26, 26,
            fill=color,
            outline="white",
            width=2,
            tags=(self._status_tag,)
        )
        # Frame counter for debug
        self._canvas.create_text(
            35, 18,
            anchor="w",
            text=f"FPS: ~{int(30)} | Frames: {self._frame_count}",
            fill="white",
            font=("Segoe UI", 10),
            tags=(self._status_tag,)
        )
        
        # Auto-capture countdown
        self._canvas.delete(self._countdown_tag)
        if self._auto_capture_time_remaining is not None and self._auto_capture_time_remaining > 0:
            center_x = self._width // 2
            center_y = self._height // 2
            countdown_text = f"Auto-captura en {int(self._auto_capture_time_remaining)}s..."
            
            # Semi-transparent background
            self._canvas.create_rectangle(
                center_x - 150, center_y - 60,
                center_x + 150, center_y - 10,
                fill="#000000",
                stipple="gray75",
                outline="",
                tags=(self._countdown_tag,)
            )
            
            # Countdown text with glow effect
            self._canvas.create_text(
                center_x, center_y - 35,
                text=countdown_text,
                fill=config.DETECTION_PULSE_COLOR,
                font=("Segoe UI", 20, "bold"),
                tags=(self._countdown_tag,)
            )

    def _prepare_image(self, frame_bgr: np.ndarray) -> tuple[Image.Image, float, int, int]:
        rgb = frame_bgr[:, :, ::-1]  # BGR -> RGB without OpenCV dependency here
        frame = Image.fromarray(rgb)
        frame_ratio = frame.width / frame.height
        target_ratio = self._width / self._height
        if frame_ratio > target_ratio:
            new_width = self._width
            new_height = int(new_width / frame_ratio)
        else:
            new_height = self._height
            new_width = int(new_height * frame_ratio)
        resized = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
        image = Image.new("RGB", (self._width, self._height))
        offset_x = (self._width - new_width) // 2
        offset_y = (self._height - new_height) // 2
        image.paste(resized, (offset_x, offset_y))
        scale = new_width / frame.width
        return image, scale, offset_x, offset_y

    def _draw_overlays(
        self,
        detections: Sequence[DetectionResult],
        scale: float,
        offset_x: int,
        offset_y: int,
    ) -> None:
        for tag in self._current_boxes:
            self._canvas.delete(tag)
        self._current_boxes.clear()
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox
            x1 = int(x1 * scale + offset_x)
            y1 = int(y1 * scale + offset_y)
            x2 = int(x2 * scale + offset_x)
            y2 = int(y2 * scale + offset_y)
            tag_box = f"bbox_{len(self._current_boxes)}"
            tag_text = f"label_{len(self._current_boxes)}"
            outline = config.ACCENT_COLOR
            self._canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                outline=outline,
                width=3,
                tags=(tag_box,),
            )
            label = detection.primary_label.label.display_name
            score = detection.primary_label.score
            header = f"{label} ({score:.0%})"
            text_x = x1 + 8
            text_y = max(y1 - 16, 16)
            text_item = self._canvas.create_text(
                text_x,
                text_y,
                anchor="sw",
                text=header,
                fill="white",
                font=("Segoe UI", 12, "bold"),
                tags=(tag_text,),
            )
            bbox = self._canvas.bbox(text_item)
            if bbox:
                pad = 4
                rect_tag = f"label_rect_{len(self._current_boxes)}"
                rect = self._canvas.create_rectangle(
                    bbox[0] - pad,
                    bbox[1] - pad,
                    bbox[2] + pad,
                    bbox[3] + pad,
                    fill=outline,
                    outline="",
                    tags=(rect_tag,),
                )
                self._canvas.tag_raise(text_item, rect)
                self._current_boxes.append(rect_tag)
            self._current_boxes.extend([tag_box, tag_text])

    def flash_capture(self) -> None:
        """Play a brief flash animation to signal a successful capture."""
        self._canvas.delete(self._flash_tag)
        overlay = self._canvas.create_rectangle(
            0,
            0,
            self._width,
            self._height,
            fill="#ffffff",
            stipple="gray12",
            outline="",
            tags=(self._flash_tag,),
        )

        def _fade(step: int) -> None:
            patterns = ["gray12", "gray25", "gray50", "gray75"]
            if step >= len(patterns):
                self._canvas.delete(self._flash_tag)
                return
            self._canvas.itemconfigure(overlay, stipple=patterns[step])
            self.after(45, lambda: _fade(step + 1))

        _fade(0)
    
    def set_auto_capture_countdown(self, seconds: float | None) -> None:
        """Update the auto-capture countdown display."""
        self._auto_capture_time_remaining = seconds

    def set_focus_bbox(self, bbox: tuple[int, int, int, int]) -> None:
        """Set a focus bbox in the canvas's coordinate space (after scaling).

        This crops the frame and scales the crop to fill the canvas for a dramatic "pokedex" effect.
        """
        # bbox expected in original frame pixel coordinates; translate later during render
        self._focus_bbox = bbox
        self._focus_bbox = bbox
        # add a small visual pulse that draws attention to the focus area
        self._focus_pulse_step = 0
        self._focus_pulse_active = True
        self._animate_focus_pulse()

    def clear_focus(self) -> None:
        """Clear any focus crop and return to the normal camera feed view."""
        self._focus_bbox = None
        self._focus_pulse_active = False

    def _animate_focus_pulse(self) -> None:
        """Internal: animate a pulsing outline around the focus bbox."""
        try:
            if not getattr(self, "_focus_pulse_active", False):
                self._canvas.delete("focus_pulse")
                return
            self._focus_pulse_step = (getattr(self, "_focus_pulse_step", 0) + 1) % 12
            
            # When focused, we are zoomed in, so draw the pulse around the entire view
            # to give a "target locked" HUD effect.
            width = 4 + (self._focus_pulse_step % 6)
            color = config.ACCENT_COLOR
            
            self._canvas.delete("focus_pulse")
            # Draw a border around the canvas
            self._canvas.create_rectangle(
                2, 2, self._width - 2, self._height - 2,
                outline=color,
                width=width,
                tags=("focus_pulse",)
            )
            
            # Add "TARGET LOCKED" text blinking
            if self._focus_pulse_step % 6 < 3:
                self._canvas.create_text(
                    self._width // 2, 30,
                    text="TARGET LOCKED",
                    fill=color,
                    font=("Segoe UI", 16, "bold"),
                    tags=("focus_pulse",)
                )
            
            self.after(85, self._animate_focus_pulse)
        except Exception:
            self._canvas.delete("focus_pulse")

    def _draw_scanning_line(self) -> None:
        """Draw a futuristic scanning line moving up and down."""
        if not hasattr(self, "_scan_y"):
            self._scan_y = 0
            self._scan_direction = 1
        
        self._scan_y += 5 * self._scan_direction
        if self._scan_y > self._height:
            self._scan_direction = -1
        elif self._scan_y < 0:
            self._scan_direction = 1
            
        self._canvas.delete("scan_line")
        self._canvas.create_line(
            0, self._scan_y, self._width, self._scan_y,
            fill=config.ACCENT_COLOR,
            width=2,
            stipple="gray50",
            tags=("scan_line",)
        )



__all__ = ["CameraCanvas"]
