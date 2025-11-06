"""Gamification system for ZDex - achievements, stats, and progression."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from . import config

logger = logging.getLogger(__name__)


@dataclass
class SpeciesStats:
    """Statistics for a specific species."""
    species_name: str
    common_name: str
    total_sightings: int = 0
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    locations: List[str] = field(default_factory=list)
    best_confidence: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SpeciesStats":
        return cls(**data)


@dataclass
class Achievement:
    """Represents a gamification achievement."""
    id: str
    name: str
    description: str
    icon: str  # Emoji
    unlocked: bool = False
    unlock_date: Optional[str] = None
    progress: int = 0
    target: int = 1
    
    @property
    def is_complete(self) -> bool:
        return self.progress >= self.target
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Achievement":
        return cls(**data)


class GamificationSystem:
    """Manages gamification features - achievements, stats, progression."""
    
    def __init__(
        self,
        stats_path: Path | None = None,
        achievements_path: Path | None = None
    ):
        self._stats_path = stats_path or config.STATS_FILE_PATH
        self._achievements_path = achievements_path or config.ACHIEVEMENTS_FILE_PATH
        
        self.species_stats: Dict[str, SpeciesStats] = {}
        self.achievements: Dict[str, Achievement] = {}
        self.total_captures = 0
        self.session_start = datetime.now().isoformat()
        
        self._load()
        self._initialize_achievements()
    
    def _load(self) -> None:
        """Load stats and achievements from disk."""
        # Load species stats
        if self._stats_path.exists():
            try:
                with self._stats_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.species_stats = {
                        k: SpeciesStats.from_dict(v)
                        for k, v in data.get("species", {}).items()
                    }
                    self.total_captures = data.get("total_captures", 0)
                    logger.info(f"Estadísticas cargadas: {len(self.species_stats)} especies, {self.total_captures} capturas totales")
            except Exception as e:
                logger.error(f"Error cargando estadísticas: {e}")
        
        # Load achievements
        if self._achievements_path.exists():
            try:
                with self._achievements_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.achievements = {
                        k: Achievement.from_dict(v)
                        for k, v in data.items()
                    }
                    logger.info(f"Logros cargados: {len(self.achievements)} logros")
            except Exception as e:
                logger.error(f"Error cargando logros: {e}")
    
    def _save(self) -> None:
        """Save stats and achievements to disk."""
        # Save species stats
        try:
            self._stats_path.parent.mkdir(parents=True, exist_ok=True)
            with self._stats_path.open("w", encoding="utf-8") as f:
                data = {
                    "species": {k: v.to_dict() for k, v in self.species_stats.items()},
                    "total_captures": self.total_captures,
                    "session_start": self.session_start
                }
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando estadísticas: {e}")
        
        # Save achievements
        try:
            self._achievements_path.parent.mkdir(parents=True, exist_ok=True)
            with self._achievements_path.open("w", encoding="utf-8") as f:
                data = {k: v.to_dict() for k, v in self.achievements.items()}
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando logros: {e}")
    
    def _initialize_achievements(self) -> None:
        """Initialize achievement definitions."""
        default_achievements = [
            Achievement(
                id="first_capture",
                name="Primera Captura",
                description="Captura tu primer animal",
                icon="🎯",
                target=1
            ),
            Achievement(
                id="explorer",
                name="Explorador",
                description="Captura 10 animales diferentes",
                icon="🗺️",
                target=10
            ),
            Achievement(
                id="researcher",
                name="Investigador",
                description="Captura 25 animales diferentes",
                icon="🔬",
                target=25
            ),
            Achievement(
                id="naturalist",
                name="Naturalista",
                description="Captura 50 animales diferentes",
                icon="🌿",
                target=50
            ),
            Achievement(
                id="dedicated",
                name="Dedicado",
                description="Realiza 100 capturas totales",
                icon="⭐",
                target=100
            ),
            Achievement(
                id="master",
                name="Maestro ZDex",
                description="Realiza 500 capturas totales",
                icon="👑",
                target=500
            ),
            Achievement(
                id="dog_lover",
                name="Amante de Perros",
                description="Captura 10 perros",
                icon="🐕",
                target=10
            ),
            Achievement(
                id="cat_lover",
                name="Amante de Gatos",
                description="Captura 10 gatos",
                icon="🐈",
                target=10
            ),
            Achievement(
                id="bird_watcher",
                name="Observador de Aves",
                description="Captura 15 aves",
                icon="🦅",
                target=15
            ),
            Achievement(
                id="global_explorer",
                name="Explorador Global",
                description="Captura animales en 5 ubicaciones diferentes",
                icon="🌍",
                target=5
            ),
        ]
        
        for achievement in default_achievements:
            if achievement.id not in self.achievements:
                self.achievements[achievement.id] = achievement
            else:
                # Preserve unlocked status
                existing = self.achievements[achievement.id]
                achievement.unlocked = existing.unlocked
                achievement.unlock_date = existing.unlock_date
                achievement.progress = existing.progress
                self.achievements[achievement.id] = achievement
    
    def record_sighting(
        self,
        species_name: str,
        common_name: str,
        location: str,
        confidence: float
    ) -> List[Achievement]:
        """
        Record a new animal sighting and update stats.
        Returns list of newly unlocked achievements.
        """
        newly_unlocked = []
        
        # Update species stats
        if species_name not in self.species_stats:
            self.species_stats[species_name] = SpeciesStats(
                species_name=species_name,
                common_name=common_name,
                first_seen=datetime.now().isoformat()
            )
        
        stats = self.species_stats[species_name]
        stats.total_sightings += 1
        stats.last_seen = datetime.now().isoformat()
        if location and location not in stats.locations:
            stats.locations.append(location)
        if confidence > stats.best_confidence:
            stats.best_confidence = confidence
        
        self.total_captures += 1
        
        # Update achievements
        newly_unlocked.extend(self._check_achievements(common_name, location))
        
        # Save
        self._save()
        
        logger.info(f"Avistamiento registrado: {common_name} (Total: {self.total_captures})")
        
        return newly_unlocked
    
    def _check_achievements(self, common_name: str, location: str) -> List[Achievement]:
        """Check and unlock achievements based on current stats."""
        newly_unlocked = []
        
        # First capture
        if self._update_achievement_progress("first_capture", self.total_captures):
            newly_unlocked.append(self.achievements["first_capture"])
        
        # Unique species count
        unique_species = len(self.species_stats)
        if self._update_achievement_progress("explorer", unique_species):
            newly_unlocked.append(self.achievements["explorer"])
        if self._update_achievement_progress("researcher", unique_species):
            newly_unlocked.append(self.achievements["researcher"])
        if self._update_achievement_progress("naturalist", unique_species):
            newly_unlocked.append(self.achievements["naturalist"])
        
        # Total captures
        if self._update_achievement_progress("dedicated", self.total_captures):
            newly_unlocked.append(self.achievements["dedicated"])
        if self._update_achievement_progress("master", self.total_captures):
            newly_unlocked.append(self.achievements["master"])
        
        # Species-specific
        if "dog" in common_name.lower():
            dog_count = sum(
                s.total_sightings for s in self.species_stats.values()
                if "dog" in s.common_name.lower()
            )
            if self._update_achievement_progress("dog_lover", dog_count):
                newly_unlocked.append(self.achievements["dog_lover"])
        
        if "cat" in common_name.lower():
            cat_count = sum(
                s.total_sightings for s in self.species_stats.values()
                if "cat" in s.common_name.lower()
            )
            if self._update_achievement_progress("cat_lover", cat_count):
                newly_unlocked.append(self.achievements["cat_lover"])
        
        if "bird" in common_name.lower():
            bird_count = sum(
                s.total_sightings for s in self.species_stats.values()
                if "bird" in s.common_name.lower()
            )
            if self._update_achievement_progress("bird_watcher", bird_count):
                newly_unlocked.append(self.achievements["bird_watcher"])
        
        # Location-based
        unique_locations = len(set(
            loc for stats in self.species_stats.values()
            for loc in stats.locations
        ))
        if self._update_achievement_progress("global_explorer", unique_locations):
            newly_unlocked.append(self.achievements["global_explorer"])
        
        return newly_unlocked
    
    def _update_achievement_progress(self, achievement_id: str, progress: int) -> bool:
        """
        Update achievement progress.
        Returns True if achievement was just unlocked.
        """
        achievement = self.achievements.get(achievement_id)
        if not achievement:
            return False
        
        was_unlocked = achievement.unlocked
        achievement.progress = progress
        
        if achievement.is_complete and not was_unlocked:
            achievement.unlocked = True
            achievement.unlock_date = datetime.now().isoformat()
            logger.info(f"🏆 ¡Logro desbloqueado! {achievement.name}: {achievement.description}")
            return True
        
        return False
    
    def get_stats_summary(self) -> Dict:
        """Get summary of all statistics."""
        from datetime import datetime, timezone
        
        # Convert species stats to dict with relative time
        top_species = []
        for species_stat in sorted(self.species_stats.values(), key=lambda s: s.total_sightings, reverse=True)[:5]:
            # Calculate relative time
            last_seen_relative = "Nunca"
            if species_stat.last_seen:
                try:
                    last_dt = datetime.fromisoformat(species_stat.last_seen.replace('Z', '+00:00'))
                    now = datetime.now(timezone.utc)
                    delta = now - last_dt
                    
                    if delta.days > 0:
                        last_seen_relative = f"Hace {delta.days} día{'s' if delta.days > 1 else ''}"
                    elif delta.seconds >= 3600:
                        hours = delta.seconds // 3600
                        last_seen_relative = f"Hace {hours} hora{'s' if hours > 1 else ''}"
                    elif delta.seconds >= 60:
                        minutes = delta.seconds // 60
                        last_seen_relative = f"Hace {minutes} minuto{'s' if minutes > 1 else ''}"
                    else:
                        last_seen_relative = "Hace unos segundos"
                except Exception:
                    last_seen_relative = species_stat.last_seen
            
            top_species.append({
                "species_name": species_stat.species_name,
                "common_name": species_stat.common_name,
                "total_sightings": species_stat.total_sightings,
                "first_seen": species_stat.first_seen,
                "last_seen": species_stat.last_seen,
                "last_seen_relative": last_seen_relative,
                "locations": species_stat.locations,
                "best_confidence": species_stat.best_confidence
            })
        
        return {
            "total_captures": self.total_captures,
            "unique_species": len(self.species_stats),
            "achievements_unlocked": sum(1 for a in self.achievements.values() if a.unlocked),
            "achievements_total": len(self.achievements),
            "top_species": top_species
        }
    
    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements."""
        return [a for a in self.achievements.values() if a.unlocked]
    
    def get_locked_achievements(self) -> List[Achievement]:
        """Get all locked achievements with progress."""
        return [a for a in self.achievements.values() if not a.unlocked]


# Global instance
GAMIFICATION = GamificationSystem()


__all__ = ["SpeciesStats", "Achievement", "GamificationSystem", "GAMIFICATION"]
