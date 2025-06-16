import logging
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

import requests
from pytz import timezone

_SWISS_TIMEZONE = timezone('Europe/Zurich')
_POLLEN_URL = ('https://www.meteoschweiz.admin.ch/'
               'product/output/measured-values/stationsTable/'
               'messwerte-pollen-{}-1h/stationsTable.messwerte-pollen-{}-1h.{}.json')
_UNIT = "No/m³"
_EXPECTED_DATA_VERSION = "3.0.0"

logger = logging.getLogger(__name__)


class Plant(Enum):
    BIRCH = ("birch", "birke")
    BEECH = ("beech", "buche")
    OAK = ("oak", "eiche")
    ALDER = ("alder", "erle")
    ASH = ("ash", "esche")
    GRASSES = ("grasses", "graeser")
    HAZEL = ("hazel", "hasel")

    def __init__(self, description, key):
        self.description = description
        self.key = key


class Level(Enum):
    NONE = ("none", 1)
    LOW = ("low", 10)
    MEDIUM = ("medium", 70)
    STRONG = ("strong", 250)
    VERY_STRONG = ("very_strong", None)

    def __init__(self, description, lower_bound:int):
        self.description = description
        self.lower_bound:int = lower_bound

    @staticmethod
    def level(value:int):
        for level in Level:
            bound = level.lower_bound
            if bound is not None and value <= bound:
                return level
        return Level.VERY_STRONG

@dataclass
class Station:
    code: str
    name: str
    canton: str
    altitude: int
    coordinates: list[int]
    latlong: list[float]

    def __eq__(self, other):
        if not isinstance(other, Station):
            return False
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)


@dataclass
class Measurement:
    plant: Plant
    value: int
    unit: str
    level: Level
    date: datetime


class PollenService:
    @staticmethod
    def current_values(plants: list[Plant] = Plant) -> dict[Station, list[Measurement]]:
        pollen_measurements = {}
        for plant in plants:
            url = _POLLEN_URL.format(plant.key, plant.key, "en")
            try:
                logger.debug("Requesting station data...")
                response = requests.get(url)

                if response.status_code == 200:
                    json_data = response.json()
                    logger.debug("Received data: %s", json_data)
                    version = json_data.get("config", {}).get("version", None)
                    if version is None:
                        raise Exception(f"Unknown data format", json_data)

                    if version != _EXPECTED_DATA_VERSION:
                        logger.warning("Unexpected data version: %s, expected: %s", version, _EXPECTED_DATA_VERSION)

                    for station_data in json_data["stations"]:
                        station = Station(
                            station_data["id"],
                            station_data["station_name"],
                            station_data["canton"],
                            int(station_data["altitude"]),
                            station_data["coordinates"],
                            station_data["latlong"]
                        )
                        measurements = pollen_measurements.setdefault(station, [])
                        current = station_data["current"]
                        if current["summary"] != "no data" and current["value"] is not None:
                            value = int(current["value"])
                            measurements.append(Measurement(
                                plant,
                                value,
                                _UNIT,
                                Level.level(value),
                                datetime.fromtimestamp(current["date"] / 1000, tz=_SWISS_TIMEZONE)
                            ))
                else:
                    logger.error(f"Failed to fetch data. Status code: {response.status_code}")
            except requests.exceptions.RequestException:
                logger.error("Connection failure.")
        return pollen_measurements
