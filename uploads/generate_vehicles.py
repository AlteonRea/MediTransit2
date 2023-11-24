from random import seed

from data.database import Database


def run():
    Database.Initialize()
    Database.generate_available_vehicles(10)


if __name__ == "__main__":
    seed(20)
    run()