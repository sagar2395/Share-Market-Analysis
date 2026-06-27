"""Test setup — force offline provider, isolated temp data dir, no scheduler.

Runs before any app import so cached settings pick these up.
"""

from __future__ import annotations

import os
import tempfile

os.environ.setdefault("SMA_PROVIDER", "sample")
os.environ.setdefault("SMA_DATA_DIR", tempfile.mkdtemp(prefix="sma_test_"))
os.environ.setdefault("SMA_ENABLE_SCHEDULER", "false")
