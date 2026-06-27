"""Indicator contract — the heart of the extensible, *teaching* analysis engine.

Every indicator implements two things:

* ``compute(df)``  → the numeric series (for plotting / signals).
* ``explain(df)``  → a plain-language :class:`Explanation` built from the **live
  values** that says what it measures, what the current reading means, and what
  action it typically implies. This is what makes the tool teach the owner rather
  than just display numbers (see ``PLAN.md`` §6d).

Add an indicator by subclassing :class:`Indicator` and decorating with
``@register`` — it then appears across the API/UI automatically.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal

import pandas as pd
from pydantic import BaseModel

Stance = Literal["bullish", "bearish", "neutral"]


class Explanation(BaseModel):
    indicator: str
    title: str
    value: dict[str, float | None]
    stance: Stance
    summary: str          # one line: what it measures
    reading: str          # what the CURRENT value means for this stock
    action: str           # what a trader typically does here
    caveat: str | None = None  # when the signal is unreliable / what invalidates it


class Indicator(ABC):
    key: str = "base"
    title: str = "Indicator"

    @abstractmethod
    def compute(self, df: pd.DataFrame) -> pd.Series | pd.DataFrame:
        """Return the indicator series aligned to ``df``'s index."""

    @abstractmethod
    def explain(self, df: pd.DataFrame) -> Explanation:
        """Return plain-language teaching text computed from live values."""
