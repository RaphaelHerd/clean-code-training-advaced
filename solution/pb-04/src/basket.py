from dataclasses import dataclass, field


@dataclass
class Item:
    name: str
    price: float


class Basket:
    def __init__(self):
        self._items: list[Item] = []

    def add_item(self, name: str, price: float) -> None:
        """Add an item to the basket."""
        if price < 0:
            raise ValueError(f"Price cannot be negative: {price}")
        self._items.append(Item(name=name, price=price))

    def remove_item(self, name: str) -> None:
        """Remove all items with the given name. No-op if name is not in basket."""
        self._items = [i for i in self._items if i.name != name]

    def total(self) -> float:
        """Return the sum of all item prices."""
        return sum(i.price for i in self._items)

    def item_names(self) -> list[str]:
        """Return a list of all item names (with duplicates)."""
        return [i.name for i in self._items]

    def __len__(self) -> int:
        return len(self._items)