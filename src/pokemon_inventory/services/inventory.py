from __future__ import annotations

from pokemon_inventory.models.card import Card
from pokemon_inventory.repositories.card_repository import CardRepository
from pokemon_inventory.validation.card_validation import (
    validate_card,
    validate_card_exists,
    validate_quantity,
)


class Inventory:
    def __init__(self, repository: CardRepository):
        self.repository = repository

    def add(self, card: Card) -> Card:
        validate_card(card.name, card.set_name, card.number)
        validate_quantity(card.quantity)

        existing = self.repository.find_by_exact_identity(card.name, card.set_name, card.number)
        if existing is not None:
            raise ValueError("Card already exists in inventory")

        return self.repository.add(card)

    def list(self) -> list[Card]:
        return list(self.repository.list())

    def get_by_id(self, card_id: int) -> Card | None:
        return self.repository.get_by_id(card_id)

    def find(self, name: str) -> Card | None:
        matches = self.repository.find_by_name(name)
        return matches[0] if matches else None

    def find_by_name(self, name: str) -> list[Card]:
        return self.repository.find_by_name(name)

    def remove(self, name: str) -> None:
        card = self.find(name)
        validate_card_exists(card)
        self.repository.remove(card)

    def delete_card(self, card_id: int) -> None:
        card = self.get_by_id(card_id)
        validate_card_exists(card)
        self.repository.remove(card)

    def update_quantity(self, name: str, quantity: int) -> Card:
        validate_quantity(quantity)
        card = self.find(name)
        validate_card_exists(card)
        card.quantity = quantity
        return self.repository.update(card)

    def update_card(
        self,
        card_id: int,
        *,
        name: str | None = None,
        set_name: str | None = None,
        number: str | None = None,
        quantity: int | None = None,
    ) -> Card:
        card = self.get_by_id(card_id)
        validate_card_exists(card)

        candidate_name = card.name if name is None else name.strip()
        candidate_set = card.set_name if set_name is None else set_name.strip()
        candidate_number = card.number if number is None else number.strip()
        candidate_quantity = card.quantity if quantity is None else quantity

        validate_card(candidate_name, candidate_set, candidate_number)
        if quantity is not None:
            validate_quantity(candidate_quantity)

        duplicate = self.repository.find_by_exact_identity(candidate_name, candidate_set, candidate_number)
        if duplicate is not None and duplicate.id != card_id:
            raise ValueError("Card already exists in inventory")

        card.name = candidate_name
        card.set_name = candidate_set
        card.number = candidate_number
        if quantity is not None:
            card.quantity = candidate_quantity

        return self.repository.update(card)

    def summary(self) -> dict[str, int]:
        cards = self.list()
        total_cards = sum(card.quantity for card in cards)
        unique_cards = len(cards)
        return {
            "total_cards": total_cards,
            "unique_cards": unique_cards,
            "total_items": total_cards,
        }