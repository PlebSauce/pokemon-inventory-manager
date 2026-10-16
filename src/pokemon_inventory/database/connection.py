from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from pokemon_inventory.models.card import Base

DATABASE_URL = os.getenv("POKEMON_INVENTORY_DB_URL", "sqlite:///pokemon_inventory.db")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)