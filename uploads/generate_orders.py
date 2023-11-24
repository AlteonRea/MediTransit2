from random import seed

from data.database import Database


def run():
    Database.Initialize()
    
    Database.generate_random_orders(9, 3, 10)


if __name__ == "__main__":
    seed(20)
    run()