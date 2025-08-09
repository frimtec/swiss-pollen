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

        self.assertIsNone(result.station_by_code("PBS"))
        self.assertIsNone(result.measurement_by_station_code("PBS", Plant.GRASSES))

        luzern = result.station_by_code("PLZ")
        zuerich = result.station_by_code("PZH")
        self.assertEqual("Luzern", luzern.name)
        self.assertEqual("LU", luzern.canton)
        self.assertEqual(499, luzern.altitude)
        self.assertEqual([2665198, 1212207], luzern.coordinates)
        self.assertEqual([47.057678, 8.296803], luzern.latlong)

        self.assertEqual("Zürich", zuerich.name)
        self.assertEqual("ZH", zuerich.canton)
        self.assertEqual(581, zuerich.altitude)
        self.assertEqual([2685110, 1248099], zuerich.coordinates)
        self.assertEqual([47.378225, 8.565644], zuerich.latlong)

        expected_date = datetime.fromtimestamp(1754751600000 / 1000, tz=timezone('Europe/Zurich'))

        grasses_luzern = result.measurement_by_station(luzern, Plant.GRASSES)
        self.assertEqual(Plant.GRASSES, grasses_luzern.plant)
        self.assertEqual(9, grasses_luzern.value)
        self.assertEqual(Level.LOW, grasses_luzern.level)
        self.assertEqual("No/m³", grasses_luzern.unit)
        self.assertEqual(expected_date, grasses_luzern.date)
        self.assertIsNone(result.measurement_by_station(luzern, Plant.HAZEL))

        grasses_zuerich = result.measurement_by_station(zuerich, Plant.GRASSES)
        self.assertEqual(Plant.GRASSES, grasses_zuerich.plant)
        self.assertEqual(42, grasses_zuerich.value)
        self.assertEqual(Level.MEDIUM, grasses_zuerich.level)
        self.assertEqual("No/m³", grasses_zuerich.unit)
        self.assertEqual(expected_date, grasses_zuerich.date)
        self.assertIsNone(result.measurement_by_station(zuerich, Plant.HAZEL))

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

        self.assertEqual(9, result.measurement_by_station_code("PLZ", Plant.HAZEL).value)
        self.assertIsNone(result.measurement_by_station_code("PZH", Plant.HAZEL))

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
