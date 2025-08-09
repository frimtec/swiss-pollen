import unittest
from datetime import datetime
from logging import WARNING, ERROR
from unittest.mock import patch, MagicMock

from pytz import timezone

from swiss_pollen import PollenService, Plant, EXPECTED_DATA_VERSION, Level


class TestInit(unittest.TestCase):
    @patch("swiss_pollen.requests.get")
    def test_load_successful_response(self, mock_get):
        mock_data = {
            "config": {
                "name": "measurement-messwerte-pollen-graeser-1h-stations",
                "language": "en",
                "version": "3.0.0",
                "timestamp": 1754753233957
            },
            "stations": [
                {
                    "network": "messwerte-pollen-graeser-1h",
                    "network_type": "messnetz-pollen",
                    "station_name": "Luzern",
                    "id": "PLZ",
                    "current": {
                        "value": "9",
                        "date": 1754751600000,
                        "label": "Current value",
                        "summary": "Grasses, measured on 9.8.2025, 17:00 at 499 m a. sea level"
                    },
                    "station_type": "Pollen autom.",
                    "altitude": "499",
                    "measurement_height": "36.00 m (on 34.00 m-roof)",
                    "coordinates": [
                        2665198,
                        1212207
                    ],
                    "latlong": [
                        47.057678,
                        8.296803
                    ],
                    "canton": "LU"
                },
                {
                    "network": "messwerte-pollen-graeser-1h",
                    "network_type": "messnetz-pollen",
                    "station_name": "Zürich",
                    "id": "PZH",
                    "current": {
                        "value": "42",
                        "date": 1754751600000,
                        "label": "Current value",
                        "summary": "Grasses, measured on 9.8.2025, 17:00 at 581 m a. sea level"
                    },
                    "station_type": "Pollen autom.",
                    "altitude": "581",
                    "measurement_height": "22.00 m (on 20.00 m-roof)",
                    "coordinates": [
                        2685110,
                        1248099
                    ],
                    "latlong": [
                        47.378225,
                        8.565644
                    ],
                    "canton": "ZH"
                },
            ]
        }

        mock_get.return_value = MagicMock(status_code=200, json=lambda: mock_data)

        result = PollenService.load([Plant.GRASSES])

        self.assertEqual(EXPECTED_DATA_VERSION, result.backend_version)
        self.assertEqual(len(result.current_values), 2)

        expected_name = {
            "PLZ": "Luzern",
            "PZH": "Zürich"
        }
        expected_canton = {
            "PLZ": "LU",
            "PZH": "ZH"
        }
        expected_altitude = {
            "PLZ": 499,
            "PZH": 581
        }
        expected_coordinates = {
            "PLZ": [
                2665198,
                1212207
            ],
            "PZH": [
                2685110,
                1248099
            ]
        }
        expected_latlong = {
            "PLZ": [
                47.057678,
                8.296803
            ],
            "PZH": [
                47.378225,
                8.565644
            ]
        }
        expected_values = {
            "PLZ": 9,
            "PZH": 42
        }
        expected_levels = {
            "PLZ": Level.LOW,
            "PZH": Level.MEDIUM
        }
        expected_date = datetime.fromtimestamp(1754751600000 / 1000, tz=timezone('Europe/Zurich'))
        for station in result.current_values.keys():
            self.assertEqual(expected_name[station.code], station.name)
            self.assertEqual(expected_canton[station.code], station.canton)
            self.assertEqual(expected_altitude[station.code], station.altitude)
            self.assertEqual(expected_coordinates[station.code], station.coordinates)
            self.assertEqual(expected_latlong[station.code], station.latlong)

            for measurement in result.current_values.get(station):
                self.assertEqual(Plant.GRASSES, measurement.plant)
                self.assertEqual(expected_values[station.code], measurement.value)
                self.assertEqual(expected_levels[station.code], measurement.level)
                self.assertEqual("No/m³", measurement.unit)
                self.assertEqual(expected_date, measurement.date)

    @patch("swiss_pollen.requests.get")
    def test_load_successful_nodata_response(self, mock_get):
        mock_data = {
            "config": {
                "name": "measurement-messwerte-pollen-graeser-1h-stations",
                "language": "en",
                "version": "3.0.0",
                "timestamp": 1754753233957
            },
            "stations": [
                {
                    "network": "messwerte-pollen-hasel-1h",
                    "network_type": "messnetz-pollen",
                    "station_name": "Luzern",
                    "id": "PLZ",
                    "current": {
                        "value": "9",
                        "date": 1754751600000,
                        "label": "Current value",
                        "summary": "Hazel, measured on 9.8.2025, 17:00 at 499 m a. sea level"
                    },
                    "station_type": "Pollen autom.",
                    "altitude": "499",
                    "measurement_height": "36.00 m (on 34.00 m-roof)",
                    "coordinates": [
                        2665198,
                        1212207
                    ],
                    "latlong": [
                        47.057678,
                        8.296803
                    ],
                    "canton": "LU"
                },
                {
                    "network": "messwerte-pollen-hasel-1h",
                    "network_type": "messnetz-pollen",
                    "station_name": "Zürich",
                    "id": "PZH",
                    "current": {
                        "summary": "no data"
                    },
                    "station_type": "Pollen autom.",
                    "altitude": "581",
                    "measurement_height": "22.00 m (on 20.00 m-roof)",
                    "coordinates": [
                        2685110,
                        1248099
                    ],
                    "latlong": [
                        47.378225,
                        8.565644
                    ],
                    "canton": "ZH"
                },
            ]
        }

        mock_get.return_value = MagicMock(status_code=200, json=lambda: mock_data)

        result = PollenService.load([Plant.HAZEL])

        self.assertEqual(EXPECTED_DATA_VERSION, result.backend_version)
        self.assertEqual(len(result.current_values), 2)

        expected_measures_size = {
            "PLZ": 1,
            "PZH": 0
        }
        for station in result.current_values.keys():
            self.assertEqual(expected_measures_size[station.code], len(result.current_values.get(station)))

    @patch("swiss_pollen.requests.get")
    def test_load_unexpected_version(self, mock_get):
        mock_data = {
            "config": {"version": "1.0"},
            "stations": [],
        }
        mock_get.return_value = MagicMock(status_code=200, json=lambda: mock_data)

        result = PollenService.load([Plant.GRASSES])

        with self.assertLogs("swiss_pollen", level=WARNING) as cm:
            PollenService.load([Plant.GRASSES])

        self.assertTrue(
            any("Unexpected data version: 1.0" in msg for msg in cm.output),
            f"Expected warning not found in logs: {cm.output}"
        )
        self.assertEqual("1.0", result.backend_version)
        self.assertEqual(len(result.current_values), 0)

    @patch("swiss_pollen.requests.get")
    def test_load_error_status_code(self, mock_get):
        mock_get.return_value = MagicMock(status_code=404)

        result = PollenService.load([Plant.GRASSES])

        with self.assertLogs("swiss_pollen", level=ERROR) as cm:
            PollenService.load([Plant.GRASSES])

        self.assertTrue(
            any("Failed to fetch data" in msg for msg in cm.output),
            f"Expected error not found in logs: {cm.output}"
        )
        self.assertIsNone(result.backend_version)
        self.assertEqual(len(result.current_values), 0)
