"""Persistent storage for captured animal observations."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from . import config
from .species import SpeciesLabel

ISO_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"


def _utc_now() -> str:
    return datetime.utcnow().strftime(ISO_FMT)


@dataclass
class CaptureEvent:
    """Represents a single capture of an animal."""

    timestamp: str
    location: str
    confidence: float
    image_path: str
    notes: Optional[str] = None


@dataclass
class SpeciesCaptureHistory:
    """Aggregated capture data for a given species."""

    class_index: int
    label_uuid: str
    common_name: str
    scientific_name: str
    captures: List[CaptureEvent] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "class_index": self.class_index,
            "label_uuid": self.label_uuid,
            "common_name": self.common_name,
            "scientific_name": self.scientific_name,
            "captures": [event.__dict__ for event in self.captures],
        }

    @classmethod
    def from_dict(cls, payload: Dict) -> "SpeciesCaptureHistory":
        captures = [CaptureEvent(**event) for event in payload.get("captures", [])]
        return cls(
            class_index=payload["class_index"],
            label_uuid=payload["label_uuid"],
            common_name=payload.get("common_name", ""),
            scientific_name=payload.get("scientific_name", ""),
            captures=captures,
        )

    @property
    def seen_count(self) -> int:
        return len(self.captures)

    @property
    def last_seen(self) -> Optional[str]:
        if not self.captures:
            return None
        return self.captures[-1].timestamp

    @property
    def last_location(self) -> Optional[str]:
        if not self.captures:
            return None
        return self.captures[-1].location

    @property
    def last_notes(self) -> Optional[str]:
        if not self.captures:
            return None
        return self.captures[-1].notes


class CaptureStore:
    """JSON-backed persistence for user captures."""

    def __init__(self, store_path: Path | None = None) -> None:
        self._store_path = store_path or config.CAPTURE_STORE_PATH
        self._records: Dict[str, SpeciesCaptureHistory] = {}
        self._load()

    def _load(self) -> None:
        if not self._store_path.exists():
            self._store_path.parent.mkdir(parents=True, exist_ok=True)
            # Persist an empty store without triggering capture flag
            self._persist(new_capture=False)
            return
        try:
            with self._store_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except json.JSONDecodeError:
            payload = {}
        for uuid, data in payload.get("species", {}).items():
            history = SpeciesCaptureHistory.from_dict(data)
            self._records[uuid] = history

    def _persist(self, new_capture: bool = False) -> None:
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "species": {uuid: history.to_dict() for uuid, history in self._records.items()}
        }
        with self._store_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)

        # --- Guardar SOLO la última detección ---
        last_event = None
        last_species_uuid = None
        # Compare timestamps using datetime instead of strings
        last_dt = None
        for uuid, history in self._records.items():
            if history.captures:
                ev = history.captures[-1]
                try:
                    ev_dt = datetime.strptime(ev.timestamp, ISO_FMT)
                except ValueError:
                    # Fallback if format changes; treat as not newer
                    ev_dt = None
                if ev_dt and (last_dt is None or ev_dt > last_dt):
                    last_event = ev
                    last_species_uuid = uuid
                    last_dt = ev_dt

        last_path = config.DATA_DIR / "last_detection.json"
        last_path.parent.mkdir(parents=True, exist_ok=True)
        if last_event and last_species_uuid:
            last_payload = {
                "species_uuid": last_species_uuid,
                "class_index": self._records[last_species_uuid].class_index,
                "common_name": self._records[last_species_uuid].common_name,
                "scientific_name": self._records[last_species_uuid].scientific_name,
                "event": last_event.__dict__,
            }
        else:
            last_payload = None

        with last_path.open("w", encoding="utf-8") as f:
            json.dump(last_payload, f, indent=2, ensure_ascii=False)

        # Indica que hay una nueva captura disponible SOLO si se grabó una nueva captura
        if new_capture:
            flag_path = config.DATA_DIR / "capture_flag.json"
            with flag_path.open("w", encoding="utf-8") as f:
                json.dump({"active": True, "updated_at": _utc_now()}, f, indent=2, ensure_ascii=False)

    def record_capture(
        self,
        label: SpeciesLabel,
        confidence: float,
        image_path: Path,
        location: str,
        notes: Optional[str] = None,
    ) -> SpeciesCaptureHistory:
        history = self._records.get(label.uuid)
        if history is None:
            history = SpeciesCaptureHistory(
                class_index=label.index,
                label_uuid=label.uuid,
                common_name=label.common_name,
                scientific_name=label.scientific_name,
            )
            self._records[label.uuid] = history
        event = CaptureEvent(
            timestamp=_utc_now(),
            location=location,
            confidence=float(confidence),  # asegura tipo nativo para JSON
            image_path=str(image_path),
            notes=notes,
        )
        history.captures.append(event)
        # Persist and set flag indicating a new capture
        self._persist(new_capture=True)
        return history

    def get_history(self, label: SpeciesLabel) -> Optional[SpeciesCaptureHistory]:
        return self._records.get(label.uuid)

    def get_all(self) -> List[SpeciesCaptureHistory]:
        return list(self._records.values())


STORE = CaptureStore()
