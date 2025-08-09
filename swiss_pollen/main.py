import logging
from swiss_pollen import (PollenService, Plant, PollenResult)

# Configure the logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def print_pollen_data(pollen_result : PollenResult):
    print(f"Backend version: {pollen_result.backend_version}")
    for station in pollen_result.current_values.keys():
        print(f"* {station}")
        for measurement in pollen_result.current_values.get(station):
            print(f" - {measurement}")


def main():
    # get pollen data for all available plants
    print_pollen_data(PollenService.load())
    print()

    # get pollen data for a restricted list of plants
    print_pollen_data(PollenService.load(plants=[Plant.HAZEL, Plant.GRASSES]))


if __name__ == "__main__":
    main()
