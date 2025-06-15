import logging
from swiss_pollen import (PollenService, Plant)

# Configure the logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def print_pollen_data(pollen_data):
    for station in pollen_data.keys():
        print(f"* {station}")
        for measurement in pollen_data.get(station):
            print(f" - {measurement}")


def main():
    # get pollen data for all available plants
    print_pollen_data(PollenService.current_values())
    print()

    # get pollen data for a restricted list of plants
    print_pollen_data(PollenService.current_values(plants=[Plant.HAZEL, Plant.GRASSES]))


if __name__ == "__main__":
    main()
