import os

import tomllib


def load_config(filename) -> dict:
    if not os.path.exists(filename):
        f = open(filename, mode="w")
        f.close()

    f = open(filename, mode="rb")
    config = tomllib.load(f)
    f.close()

    return config
