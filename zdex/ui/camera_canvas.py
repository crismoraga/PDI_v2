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
        self._frame_count = 0

    def render(self, frame_bgr: np.ndarray, detections: Sequence[DetectionResult] = ()) -> None:
        if frame_bgr is None:
            return
        self._frame_count += 1
        image, scale, offset_x, offset_y = self._prepare_image(frame_bgr)
        self._photo = ImageTk.PhotoImage(image=image)
        self._canvas.delete("frame")
        self._canvas.create_image(0, 0, anchor="nw", image=self._photo, tags="frame")
        self._draw_overlays(detections, scale, offset_x, offset_y)
        
        # Status indicator: green dot when detecting
        self._canvas.delete(self._status_tag)
        color = "#22c55e" if detections else "#94a3b8"
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


__all__ = ["CameraCanvas"]
