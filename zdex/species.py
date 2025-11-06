"""Utilities for loading and querying SpeciesNet label metadata."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from . import config


@dataclass(frozen=True)
class SpeciesLabel:
    """Represents a single class entry from the SpeciesNet label manifest."""

    index: int
    uuid: str
    kingdom_class: str
    order: str
    family: str
    genus: str
    species: str
    common_name: str

    @property
    def scientific_name(self) -> str:
        """Return the concatenated binomial name if available."""
        genus = self.genus.strip()
        species = self.species.strip()
        if genus and species:
            return f"{genus.capitalize()} {species}"
        if genus:
            return genus.capitalize()
        return species or self.common_name

    @property
    def display_name(self) -> str:
        """Return a friendly name to show on the UI."""
        return self.common_name.title() if self.common_name else self.scientific_name


class SpeciesIndex:
    """Load the SpeciesNet label file and provide lookup helpers."""

    def __init__(self, label_path: Path | None = None) -> None:
        self._label_path = label_path or config.LABELS_PATH
        self._labels: List[SpeciesLabel] = []
        self._by_uuid: Dict[str, SpeciesLabel] = {}
        self._load()

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._labels)

    def __iter__(self) -> Iterable[SpeciesLabel]:  # pragma: no cover - simple proxy
        return iter(self._labels)

    def _load(self) -> None:
        if not self._label_path.exists():
            raise FileNotFoundError(f"Label file not found: {self._label_path}")

        with self._label_path.open("r", encoding="utf-8") as handle:
            for idx, raw_line in enumerate(handle):
                line = raw_line.strip()
                if not line:
                    continue
                parts = line.split(";")
                # Pad to 7 columns to avoid index errors on incomplete entries
                parts += [""] * (7 - len(parts))
                label = SpeciesLabel(
                    index=idx,
                    uuid=parts[0],
                    kingdom_class=parts[1],
                    order=parts[2],
                    family=parts[3],
                    genus=parts[4],
                    species=parts[5],
                    common_name=parts[6],
                )
                self._labels.append(label)
                self._by_uuid[label.uuid] = label

    def get(self, index: int) -> SpeciesLabel:
        return self._labels[index]

    def find_by_uuid(self, uuid: str) -> Optional[SpeciesLabel]:
        return self._by_uuid.get(uuid)

    def search(self, query: str, limit: int = 10) -> List[SpeciesLabel]:
        query_lower = query.lower()
        matches = [label for label in self._labels if query_lower in label.display_name.lower()]
        return matches[:limit]


# Instantiate a shared index on module import to avoid repeated disk reads.
INDEX = SpeciesIndex()
