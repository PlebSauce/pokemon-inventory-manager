from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from pokemon_inventory.database.connection import DATABASE_URL, Base
from pokemon_inventory.models.card import Card
from pokemon_inventory.repositories.card_repository import CardRepository
from pokemon_inventory.services.inventory import Inventory


class CardBase(BaseModel):
    name: str = Field(..., min_length=1)
    set_name: str = Field(..., min_length=1)
    number: str = Field(..., min_length=1)
    quantity: int = Field(default=1, ge=1)

    @field_validator("name", "set_name", "number")
    @classmethod
    def strip_and_validate(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be blank")
        return cleaned


class CardCreate(CardBase):
    pass


class CardUpdate(BaseModel):
    name: str | None = Field(default=None)
    set_name: str | None = Field(default=None)
    number: str | None = Field(default=None)
    quantity: int | None = Field(default=None, ge=1)

    @field_validator("name", "set_name", "number")
    @classmethod
    def strip_optional_fields(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be blank")
        return cleaned


class CardRead(BaseModel):
    id: int
    name: str
    set_name: str
    number: str
    quantity: int

    model_config = ConfigDict(from_attributes=True)


def create_app(database_url: str = DATABASE_URL) -> FastAPI:
    engine_kwargs = {"future": True}
    if database_url.startswith("sqlite:///:memory:"):
        engine_kwargs.update(
            {
                "poolclass": StaticPool,
                "connect_args": {"check_same_thread": False},
            }
        )
    engine = create_engine(database_url, **engine_kwargs)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        Base.metadata.create_all(bind=engine)
        yield

    def get_db() -> Session:
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def get_inventory(db: Session = Depends(get_db)) -> Inventory:
        return Inventory(CardRepository(db))

    app = FastAPI(title="Pokémon Inventory Manager API", lifespan=lifespan)

    def _raise_service_error(exc: ValueError) -> None:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from exc

    @app.get("/cards", response_model=list[CardRead])
    def list_cards(inventory: Inventory = Depends(get_inventory)) -> list[Card]:
        return inventory.list()

    @app.post("/cards", response_model=CardRead, status_code=status.HTTP_201_CREATED)
    def create_card(
        card_data: CardCreate,
        inventory: Inventory = Depends(get_inventory),
    ) -> Card:
        try:
            card = Card(
                name=card_data.name,
                set_name=card_data.set_name,
                number=card_data.number,
                quantity=card_data.quantity,
            )
            return inventory.add(card)
        except ValueError as exc:
            _raise_service_error(exc)

    @app.get("/cards/{card_id}", response_model=CardRead)
    def get_card(
        card_id: int,
        inventory: Inventory = Depends(get_inventory),
    ) -> Card:
        card = inventory.get_by_id(card_id)
        if card is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
        return card

    @app.put("/cards/{card_id}", response_model=CardRead)
    def update_card(
        card_id: int,
        card_data: CardUpdate,
        inventory: Inventory = Depends(get_inventory),
    ) -> Card:
        try:
            return inventory.update_card(
                card_id,
                name=card_data.name,
                set_name=card_data.set_name,
                number=card_data.number,
                quantity=card_data.quantity,
            )
        except ValueError as exc:
            _raise_service_error(exc)

    @app.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_card(
        card_id: int,
        inventory: Inventory = Depends(get_inventory),
    ) -> Response:
        try:
            inventory.delete_card(card_id)
        except ValueError as exc:
            _raise_service_error(exc)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @app.get("/inventory/summary")
    def inventory_summary(inventory: Inventory = Depends(get_inventory)) -> dict[str, int]:
        return inventory.summary()

    return app


app = create_app()
