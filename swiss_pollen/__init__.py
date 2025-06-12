import logging
from datetime import datetime
from enum import Enum

import requests
from pytz import timezone

_SWISS_TIMEZONE = timezone('Europe/Zurich')
_POLLEN_URL = ('https://www.meteoschweiz.admin.ch/'
               'product/output/measured-values/stationsTable/'
               'messwerte-pollen-{}-1h/stationsTable.messwerte-pollen-{}-1h.{}.json')

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


class Station:
    def __init__(self, code, name, canton, altitude, coordinates, latlong):
        self.code = code
        self.name = name
        self.canton = canton
        self.altitude = altitude
        self.coordinates = coordinates
        self.latlong = latlong

    def __str__(self):
        return (
            f"Station("
            f"code={self.code}, "
            f"name={self.name}, "
            f"canton={self.canton}, "
            f"altitude={self.altitude}, "
            f"coordinates={self.coordinates}, "
            f"latlong={self.latlong})"
        )

    def __eq__(self, other):
        if not isinstance(other, Station):
            return False
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)


class PollenMeasurement:
    def __init__(self, plant, value, date):
        self.plant = plant
        self.value = value
        self.date = date

    def __str__(self):
        return f"PollenMeasurement(plant={self.plant}, value={self.value}, date={self.date})"


class PollenService:
    @staticmethod
    def current_values(plants: list[Plant] = Plant) -> dict[Station, list[PollenMeasurement]]:
        pollen_measurements = {}
        for plant in plants:
            url = _POLLEN_URL.format(plant.key, plant.key, "en")
            try:
                logger.debug("Requesting station data...")
                response = requests.get(url)

                if response.status_code == 200:
                    json_data = response.json()
                    for station_data in json_data["stations"]:
                        station = Station(
                            station_data["id"],
                            station_data["station_name"],
                            station_data["canton"],
                            station_data["altitude"],
                            station_data["coordinates"],
                            station_data["latlong"]
                        )
                        measurements = pollen_measurements.setdefault(station, [])
                        measurements.append(PollenMeasurement(
                            plant,
                            station_data["current"]["value"],
                            datetime.fromtimestamp(station_data["current"]["date"] / 1000, tz=_SWISS_TIMEZONE)
                        ))
                else:
                    logger.error(f"Failed to fetch data. Status code: {response.status_code}")
            except requests.exceptions.RequestException:
                logger.error("Connection failure.")
        return pollen_measurements
