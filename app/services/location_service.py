import time
from typing import List, Optional

import requests


class PhilippineLocationService:
    """
    Lightweight helper around the public PSGC (Philippine Standard Geographic
    Code) API with naive in-memory caching so repeated lookups stay responsive.
    """

    PSGC_BASE_URL = "https://psgc.gitlab.io/api"

    def __init__(self, cache_ttl: int = 60 * 60 * 12):
        # Cache entries: {url: (timestamp, payload)}
        self._cache = {}
        self.cache_ttl = cache_ttl

        # Local fallback data used if the live API is temporarily unreachable.
        self._fallback_provinces = [
            {"code": "130000000", "name": "Metro Manila"},
            {"code": "031400000", "name": "Pampanga"},
            {"code": "043400000", "name": "Laguna"},
            {"code": "042100000", "name": "Cavite"},
            {"code": "034900000", "name": "Nueva Ecija"},
        ]
        self._fallback_cities = {
            "130000000": [
                {"code": "133900000", "name": "Manila"},
                {"code": "137404000", "name": "Taguig"},
                {"code": "137403000", "name": "Pasig"},
                {"code": "137602000", "name": "Makati"},
                {"code": "137501000", "name": "Caloocan"},
            ],
            "043400000": [
                {"code": "043404000", "name": "San Pablo"},
                {"code": "043405000", "name": "Santa Rosa"},
                {"code": "043416000", "name": "Calamba"},
            ],
        }
        self._fallback_barangays = {
            "133900000": [
                {"code": "133900001", "name": "Ermita"},
                {"code": "133900002", "name": "Malate"},
                {"code": "133900003", "name": "Intramuros"},
                {"code": "133900004", "name": "Paco"},
                {"code": "133900005", "name": "Sampaloc"},
            ],
            "137403000": [
                {"code": "137403001", "name": "San Joaquin"},
                {"code": "137403002", "name": "Bagong Ilog"},
                {"code": "137403003", "name": "Pinagbuhatan"},
                {"code": "137403004", "name": "Ugong"},
                {"code": "137403005", "name": "Rosario"},
            ],
            "137602000": [
                {"code": "137602001", "name": "Bel-Air"},
                {"code": "137602002", "name": "Poblacion"},
                {"code": "137602003", "name": "San Antonio"},
                {"code": "137602004", "name": "San Lorenzo"},
                {"code": "137602005", "name": "Cembo"},
            ],
        }

    def _get(self, endpoint: str):
        url = f"{self.PSGC_BASE_URL}{endpoint}"
        now = time.time()
        cached = self._cache.get(url)
        if cached and now - cached[0] < self.cache_ttl:
            return cached[1]

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        payload = response.json()
        self._cache[url] = (now, payload)
        return payload

    @staticmethod
    def _simple_payload(items: List[dict], name_key: str = "name"):
        simplified = []
        for item in items:
            if not item:
                continue
            simplified.append(
                {
                    "code": item.get("code"),
                    "name": item.get(name_key) or item.get("name") or item.get("regionName"),
                }
            )
        return [entry for entry in simplified if entry["code"] and entry["name"]]

    def get_regions(self):
        data = self._get("/regions/")
        regions = self._simple_payload(data, name_key="regionName")
        # Keep NCR first for convenience
        regions.sort(key=lambda r: (r["code"] != "130000000", r["name"]))
        return regions

    def get_provinces(self, region_code: Optional[str] = None):
        try:
            if region_code:
                data = self._get(f"/regions/{region_code}/provinces/")
            else:
                data = self._get("/provinces/")
            provinces = self._simple_payload(data)
            provinces.sort(key=lambda p: p["name"])
            return provinces
        except requests.RequestException:
            # Fall back to a curated subset so the UI remains usable offline.
            return self._fallback_provinces

    def get_cities(self, province_code: str):
        if not province_code:
            return []

        try:
            data = self._get(f"/provinces/{province_code}/cities-municipalities/")
            cities = self._simple_payload(data)
            cities.sort(key=lambda c: c["name"])
            return cities
        except requests.RequestException:
            return self._fallback_cities.get(province_code, [])

    def get_barangays(self, city_code: str):
        if not city_code:
            return []

        try:
            data = self._get(f"/cities-municipalities/{city_code}/barangays/")
            barangays = self._simple_payload(data)
            barangays.sort(key=lambda b: b["name"])
            return barangays
        except requests.RequestException:
            return self._fallback_barangays.get(city_code, [])


location_service = PhilippineLocationService()

