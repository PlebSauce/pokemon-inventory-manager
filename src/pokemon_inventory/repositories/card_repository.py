from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from pokemon_inventory.models.card import Card


class CardRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, card: Card) -> Card:
        self.session.add(card)
        self.session.commit()
        self.session.refresh(card)
        return card

    def list(self) -> Sequence[Card]:
        return self.session.scalars(select(Card).order_by(Card.name, Card.set_name, Card.number)).all()

    def get_by_id(self, card_id: int) -> Card | None:
        return self.session.get(Card, card_id)

    def find_by_name(self, name: str) -> list[Card]:
        search = f"%{name.strip()}%"
        return self.session.scalars(
            select(Card).where(Card.name.ilike(search)).order_by(Card.name, Card.set_name, Card.number)
        ).all()

    def find_by_exact_identity(self, name: str, set_name: str, number: str) -> Card | None:
        return self.session.scalar(
            select(Card).where(
                Card.name.ilike(name.strip()),
                Card.set_name.ilike(set_name.strip()),
                Card.number.ilike(number.strip()),
            )
        )

    def remove(self, card: Card) -> None:
        self.session.delete(card)
        self.session.commit()

    def update(self, card: Card) -> Card:
        self.session.add(card)
        self.session.commit()
        self.session.refresh(card)
        return card