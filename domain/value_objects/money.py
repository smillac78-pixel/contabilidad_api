from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    value: Decimal
    currency: str = "EUR"

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Money value cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter ISO code")

    def add(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.value + other.value, self.currency)

    def subtract(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.value - other.value, self.currency)

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot operate on different currencies: {self.currency} vs {other.currency}"
            )

    def __str__(self) -> str:
        return f"{self.value:.2f} {self.currency}"
