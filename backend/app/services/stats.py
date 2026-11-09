from decimal import Decimal
from typing import List, Optional


def summarize(prices: List[Decimal], target: Optional[Decimal]) -> dict:
    """prices must be in chronological order."""
    if not prices:
        return {"latest_price": None, "lowest_price": None, "highest_price": None,
                "change_pct": None, "below_target": False, "checks": 0}
    latest, first = prices[-1], prices[0]
    change = None if first == 0 else round(float((latest - first) / first * 100), 2)
    return {
        "latest_price": latest,
        "lowest_price": min(prices),
        "highest_price": max(prices),
        "change_pct": change,
        "below_target": target is not None and latest <= target,
        "checks": len(prices),
    }
