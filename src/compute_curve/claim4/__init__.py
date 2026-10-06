"""Claim 4: do changes in our GPU rental index lead compute-linked equities?

Pre-registration: ``docs/claim4_plan.md``. Results: ``docs/claim4_results.md``.

Alpaca is used for two things only: daily bars from its market data API, and
a *paper* trading account. Every Alpaca client refuses to start unless
``APCA_API_BASE_URL`` is exactly the paper endpoint (``alpaca.py``). Alpaca
data is cached under ``var/`` and never committed (docs/decisions.md D29).
"""
