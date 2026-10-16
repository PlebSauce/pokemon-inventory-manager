from pokemon_inventory.database.connection import engine
from pokemon_inventory.models.card import Base
from pokemon_inventory.cli.menu import start_menu


def main():
    Base.metadata.create_all(engine)
    start_menu()


if __name__ == "__main__":
    main()