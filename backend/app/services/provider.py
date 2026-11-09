"""Price providers. The mock provider needs no API key, so the project runs anywhere.
To use real data, implement another class with the same quote() signature
and return it from get_provider()."""
import os
import random
import zlib
from datetime import date
from decimal import Decimal

AIRLINES = ["Thai AirAsia", "Thai Lion Air", "Thai Airways", "Bangkok Airways", "Nok Air", "VietJet"]


class MockProvider:
    def quote(self, origin: str, destination: str, departure_date: date) -> tuple[str, Decimal]:
        key = zlib.crc32(f"{origin}{destination}{departure_date}".encode())
        base = 1500 + key % 6000                      # stable base price for this route/date
        days_out = max((departure_date - date.today()).days, 0)
        closeness = 1 + max(0, 30 - days_out) * 0.012  # prices rise as the date gets close
        wobble = random.uniform(-0.08, 0.08)          # market movement between checks
        airline = AIRLINES[key % len(AIRLINES)]
        return airline, Decimal(str(round(base * closeness * (1 + wobble), 2)))


def get_provider():
    name = os.getenv("PRICE_PROVIDER", "mock")
    if name == "mock":
        return MockProvider()
    raise RuntimeError(f"Unknown PRICE_PROVIDER '{name}'. Only 'mock' is implemented.")
