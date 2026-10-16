from __future__ import annotations

from pokemon_inventory.database.connection import SessionLocal
from pokemon_inventory.models.card import Card
from pokemon_inventory.repositories.card_repository import CardRepository
from pokemon_inventory.services.inventory import Inventory
from pokemon_inventory.validation.card_validation import validate_card, validate_quantity


def start_menu():
    session = SessionLocal()

    try:
        repository = CardRepository(session)
        inventory = Inventory(repository)

        while True:
            print("\nPokémon Inventory Manager")
            print("1. Add card")
            print("2. List inventory")
            print("3. Find card by name")
            print("4. Remove card")
            print("5. Update card quantity")
            print("6. Show summary")
            print("7. Exit")

            choice = input("> ")

            if choice == "1":
                try:
                    name = input("Card name: ").strip()
                    set_name = input("Set: ").strip()
                    number = input("Number: ").strip()
                    quantity = int(input("Quantity: ") or "1")
                    validate_card(name, set_name, number)
                    validate_quantity(quantity)
                    inventory.add(Card(name=name, set_name=set_name, number=number, quantity=quantity))
                    print("Card added successfully.")
                except (ValueError, TypeError) as exc:
                    print(f"Error: {exc}")

            elif choice == "2":
                cards = inventory.list()
                if not cards:
                    print("Inventory is empty.")
                for card in cards:
                    print(card)

            elif choice == "3":
                name = input("Card name: ").strip()
                matches = inventory.find_by_name(name)
                if not matches:
                    print("No matching cards found.")
                    continue
                for card in matches:
                    print(card)

            elif choice == "4":
                try:
                    name = input("Card name: ").strip()
                    inventory.remove(name)
                    print(f"Removed first matching card for: {name}")
                except ValueError as exc:
                    print(f"Error: {exc}")

            elif choice == "5":
                try:
                    name = input("Card name: ").strip()
                    new_quantity = int(input("New quantity: "))
                    validate_quantity(new_quantity)
                    updated = inventory.update_quantity(name, new_quantity)
                    print(f"Updated {updated.name} to quantity {updated.quantity}")
                except (ValueError, TypeError) as exc:
                    print(f"Error: {exc}")

            elif choice == "6":
                summary = inventory.summary()
                print(f"Total cards: {summary['total_cards']}")
                print(f"Unique cards: {summary['unique_cards']}")

            elif choice == "7":
                break

            else:
                print("Invalid choice.")
    finally:
        session.close()