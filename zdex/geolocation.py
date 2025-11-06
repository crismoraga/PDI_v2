"""Geolocation utilities using IP-based location."""
from __future__ import annotations

import logging
import requests
from functools import lru_cache
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Location:
    """Represents a geographic location."""
    city: str
    region: str
    country: str
    latitude: float
    longitude: float
    
    @property
    def display_name(self) -> str:
        """Return human-readable location string."""
        parts = []
        if self.city:
            parts.append(self.city)
        if self.region:
            parts.append(self.region)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts) if parts else "Ubicación desconocida"


class GeolocatorService:
    """IP-based geolocation service."""
    
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'ZDex/2.0 (Animal Detection App)'
        })
    
    @lru_cache(maxsize=1)
    def get_current_location(self) -> Optional[Location]:
        """
        Get current location based on IP address.
        Uses ipapi.co free service (no API key required).
        Returns None if location cannot be determined.
        """
        try:
            logger.info("Obteniendo ubicación geográfica...")
            response = self._session.get(
                "https://ipapi.co/json/",
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            location = Location(
                city=data.get("city", ""),
                region=data.get("region", ""),
                country=data.get("country_name", ""),
                latitude=float(data.get("latitude", 0)),
                longitude=float(data.get("longitude", 0))
            )
            
            logger.info(f"Ubicación detectada: {location.display_name}")
            return location
            
        except requests.RequestException as e:
            logger.warning(f"No se pudo obtener ubicación: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.warning(f"Respuesta de geolocalización inválida: {e}")
            return None
    
    def refresh_location(self) -> Optional[Location]:
        """Force refresh of cached location."""
        self.get_current_location.cache_clear()
        return self.get_current_location()


# Global instance
GEOLOCATOR = GeolocatorService()


__all__ = ["Location", "GeolocatorService", "GEOLOCATOR"]
