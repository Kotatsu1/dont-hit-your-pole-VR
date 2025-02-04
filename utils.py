import os
import json


config = {
    'transparency': 1,
    'height': 10,
    'color': [130, 80, 230],
    'size': 0.2,
    'base_station_serial': "LHB-32E3676B",
    'x': 1.7,
    'y': 0,
    'z': 1.73
}


def rgb_to_normalized(rgb: list):
    return [round(x / 255.0, 1) for x in rgb]


def config_exists():
    config_exists = os.path.exists('config.json')
    if config_exists:
        return True

    return False


def create_config():
    if not config_exists():
        with open("config.json", "w") as f:
            f.write(json.dumps(config))


def save_config():
    with open("config.json", "w") as f:
        f.write(json.dumps(config))


def find_config():
    if config_exists():
        global config
        with open('config.json', 'r') as f:
            config = json.loads(f.read())

    else:
        create_config()


find_config()
