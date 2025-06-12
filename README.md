# Swiss-Pollen
[![PyPI][pypi-shield]][pypi]
[![PyPI - Python Version][pypi-python-version-shield]][pypi]

![Project Maintenance][maintenance-shield]
[![License][license-shield]][license]

[![Build Status][build-status-shield]][build-status]
[![Deploy Status][deploy-status-shield]][deploy-status]

Python API to gather the current pollen load from [MeteoSchweiz][MeteoSchweiz] for the following pants:
* birch
* beech
* oak
* alder
* ash
* grasses
* hazel

For the use within [Home Assistant][home-assistant] use the custom component [hass-swiss-pollen][hass-swiss-pollen].

This module is not official developed, supported or endorsed by [MeteoSchweiz][MeteoSchweiz].

## Installation
### Using pip
1. Install python3.9 or higher
1. Install swiss-pollen with ```pip install swiss-pollen```.
1. Run swiss-pollen test with ```swiss-pollen```.

## Usage
### API

```python
class PollenService:
    @staticmethod
    def current_values(plants : list[Plant] = Plant) -> dict[Station, list[PollenMeasurement]]
```

### Example
```python
from swiss_pollen import (PollenService, Plant)

# get pollen data for all available plants
all_pollen_data_per_station = PollenService.current_values()

# get pollen data for a restricted list of plants
specific_pollen_data_per_station = PollenService.current_values(plants = [Plant.HAZEL, Plant.GRASSES])
```

[maintenance-shield]: https://img.shields.io/maintenance/yes/2025.svg
[license-shield]: https://img.shields.io/github/license/frimtec/swiss-pollen.svg
[license]: https://opensource.org/licenses/Apache-2.0
[pypi-shield]: https://img.shields.io/pypi/v/swiss-pollen.svg 
[pypi-python-version-shield]: https://img.shields.io/pypi/pyversions/swiss-pollen.svg 
[pypi]: https://pypi.org/project/swiss-pollen/
[pypi-files]: https://pypi.org/project/swiss-pollen/#files
[build-status-shield]: https://github.com/frimtec/swiss-pollen/workflows/Build/badge.svg
[build-status]: https://github.com/frimtec/swiss-pollen/actions?query=workflow%3ABuild
[deploy-status-shield]: https://github.com/frimtec/swiss-pollen/workflows/Deploy%20release/badge.svg
[deploy-status]: https://github.com/frimtec/swiss-pollen/actions?query=workflow%3A%22Deploy+release%22
[home-assistant]: https://www.home-assistant.io/
[MeteoSchweiz]: https://www.meteoschweiz.admin.ch/service-und-publikationen/applikationen/pollenprognose.html
[hass-swiss-pollen]: https://github.com/frimtec/hass-swiss-pollen
