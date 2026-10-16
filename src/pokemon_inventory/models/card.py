from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)
    set_name: Mapped[str] = mapped_column(index=True)
    number: Mapped[str] = mapped_column(index=True)
    quantity: Mapped[int] = mapped_column(default=1)

    def __repr__(self) -> str:
        return (
            f"Card(id={self.id}, name={self.name!r}, set_name={self.set_name!r}, "
            f"number={self.number!r}, quantity={self.quantity})"
        )