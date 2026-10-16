import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from pokemon_inventory.models.card import Base, Card
from pokemon_inventory.repositories.card_repository import CardRepository
from pokemon_inventory.services.inventory import Inventory


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    with Session(bind=engine) as session:
        yield session


def test_add_card_and_summary(session: Session):
    repository = CardRepository(session)
    inventory = Inventory(repository)

    inventory.add(Card(name="Pikachu", set_name="Base", number="1", quantity=3))
    inventory.add(Card(name="Charizard", set_name="Base", number="4", quantity=2))

    summary = inventory.summary()

    assert summary["total_cards"] == 5
    assert summary["unique_cards"] == 2


def test_duplicate_record_is_rejected(session: Session):
    repository = CardRepository(session)
    inventory = Inventory(repository)

    inventory.add(Card(name="Bulbasaur", set_name="Base", number="2", quantity=2))

    with pytest.raises(ValueError, match="already exists"):
        inventory.add(Card(name="Bulbasaur", set_name="Base", number="2", quantity=4))


def test_update_quantity_and_find_by_name(session: Session):
    repository = CardRepository(session)
    inventory = Inventory(repository)

    inventory.add(Card(name="Squirtle", set_name="Base", number="7", quantity=1))
    updated = inventory.update_quantity("Squirtle", 5)

    assert updated.quantity == 5
    matches = inventory.find_by_name("squirt")
    assert len(matches) == 1
    assert matches[0].name == "Squirtle"


def test_invalid_quantity_raises(session: Session):
    repository = CardRepository(session)
    inventory = Inventory(repository)

    with pytest.raises(ValueError, match="Quantity"):
        inventory.add(Card(name="Jigglypuff", set_name="Base", number="8", quantity=0))
