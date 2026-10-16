def validate_card(name: str, set_name: str, number: str):
    if not name.strip():
        raise ValueError("Card name cannot be empty")

    if not set_name.strip():
        raise ValueError("Set name cannot be empty")

    if not number.strip():
        raise ValueError("Card number cannot be empty")


def validate_quantity(quantity: int):
    if quantity < 1:
        raise ValueError("Quantity must be at least 1")


def validate_card_exists(card):
    if card is None:
        raise ValueError("Card not found")