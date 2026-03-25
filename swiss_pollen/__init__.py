import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import requests
from pytz import timezone

_SWISS_TIMEZONE = timezone('Europe/Zurich')
_POLLEN_URL = ('https://www.meteoschweiz.admin.ch/'
               'product/output/measured-values/stationsTable/'
               'messwerte-pollen-{}-1h/stationsTable.messwerte-pollen-{}-1h.{}.json')
_UNIT = "No/m³"
EXPECTED_DATA_VERSION = "3.0.0"

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
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

    def __init__(self, description):
        self.description = description

    @staticmethod
    def level(value: int, plant: Plant = None):
        if value <= 0:
            return Level.NONE

        # Define thresholds: (low_max, moderate_max, high_max)
        # according to https://www.meteoswiss.admin.ch/dam/jcr:43b4f361-8bc1-4af7-a232-c126de0f2f80/Belastungsklassen-der-allergenen-Pollenarten_E.pdf
        thresholds = {
            Plant.BIRCH: (0, 10, 69, 299),
            Plant.BEECH: (0, 49, 129, 399),
            Plant.OAK: (0, 49, 129, 399),
            Plant.ALDER: (0, 10, 69, 249),
            Plant.ASH: (0, 10, 99, 349),
            Plant.GRASSES: (0, 19, 49, 149),
            Plant.HAZEL: (0, 10, 69, 249),
        }
        none, low, moderate, high = thresholds.get(plant, (1, 10, 70, 250))

        if value <= none:
            return Level.NONE
        if value <= low:
            return Level.LOW
        if value <= moderate:
            return Level.MEDIUM
        if value <= high:
            return Level.STRONG
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


@dataclass
class PollenResult:
    backend_version: str
    current_values: dict[Station, list[Measurement]]

    def measurement_by_station(self, station: Station, plant: Plant) -> Measurement:
        return next(filter(lambda m: m.plant == plant, self.current_values.get(station, [])), None)

    def station_by_code(self, station_code: str) -> Station:
        return next(filter(lambda s: s.code == station_code, self.current_values.keys()), None)

    def measurement_by_station_code(self, station_code: str, plant: Plant) -> Measurement:
        return self.measurement_by_station(self.station_by_code(station_code), plant)


class PollenService:

    @staticmethod
    def load(plants: list[Plant] = Plant) -> PollenResult:
        pollen_measurements = {}
        version = None
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

                    if version != EXPECTED_DATA_VERSION:
                        logger.warning("Unexpected data version: %s, expected: %s", version, EXPECTED_DATA_VERSION)

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
                                Level.level(value, plant),
                                datetime.fromtimestamp(current["date"] / 1000, tz=_SWISS_TIMEZONE)
                            ))
                else:
                    logger.error(f"Failed to fetch data. Status code: {response.status_code}")
            except requests.exceptions.RequestException:
                logger.error("Connection failure.")
        return PollenResult(version, pollen_measurements)

    @staticmethod
    def current_values(plants: list[Plant] = Plant) -> dict[Station, list[Measurement]]:
        logger.warning("Method current_values is deprecated and will be removed in future versions. Use load instead.")
        return PollenService.load(plants).current_values
