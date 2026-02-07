"""Minimal data processor coordinated with current core/storage APIs.

This module is intentionally small for Phase A:
- keep order book state
- run validations
- persist normalized records through ``ParquetWriter``
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from ..config import Settings
from ..storage import ParquetWriter
from ..utils.logging_config import get_logger

from .orderbook import OrderBook
from .validators import DataValidator, ValidationResult

logger = get_logger(__name__)


class DataProcessor:
    """Coordinator for depth updates and trade events."""

    def __init__(
        self,
        symbol: Optional[str] = None,
        persist_depth_snapshots: bool = False,
        auto_start_writer: bool = False,
        output_dir: Optional[Path] = None,
        flush_interval: Optional[int] = None,
        max_buffer_size: Optional[int] = None,
    ) -> None:
        self.symbol = symbol or Settings.IBKR_SYMBOL
        self.persist_depth_snapshots = persist_depth_snapshots
        self.orderbook = OrderBook(max_depth=Settings.MARKET_DEPTH_ROWS)
        self.validator = DataValidator(
            max_spread_threshold=Settings.MAX_SPREAD_THRESHOLD,
            min_depth_levels=Settings.MIN_DEPTH_LEVELS,
        )
        self.writer = ParquetWriter(
            symbol=self.symbol,
            auto_start=auto_start_writer,
            output_dir=output_dir,
            flush_interval=flush_interval,
            max_buffer_size=max_buffer_size,
        )

    def process_trade(
        self,
        trade_id: int,
        event_time_ms: int,
        price: float,
        quantity: float,
        exchange: str = "-",
    ) -> ValidationResult:
        """Validate a trade against current book state and persist it."""
        bids, asks = self.orderbook.get_snapshot(Settings.MARKET_DEPTH_ROWS)
        result = self.validator.validate_trade(
            price=price,
            quantity=quantity,
            event_time=event_time_ms,
            bids=bids,
            asks=asks,
        )

        record = self._base_record(event_time_ms=event_time_ms)
        best_bid, best_ask = self.orderbook.get_best_bid_ask()
        spread_abs, spread_bps = self.orderbook.get_spread()
        bids_json, asks_json = self.orderbook.to_json(Settings.MARKET_DEPTH_ROWS)

        record.update(
            {
                "trade_id": int(trade_id),
                "atomic_type": "trade",
                "trade_price": str(price),
                "trade_qty": str(quantity),
                "bids_json": bids_json,
                "asks_json": asks_json,
                "best_bid_price": str(best_bid) if best_bid is not None else "0",
                "best_bid_qty": "0",
                "best_ask_price": str(best_ask) if best_ask is not None else "0",
                "best_ask_qty": "0",
                "spread_bps": str(spread_bps) if spread_bps is not None else "0",
                "depth_sync_quality": self.orderbook.get_depth_quality_score(),
                "raw_json": json.dumps(
                    {
                        "exchange": exchange,
                        "spread_points": spread_abs,
                    }
                ),
            }
        )
        record.update(result.to_dict())
        self.writer.add_record(record)
        return result

    def process_depth_update(
        self,
        position: int,
        operation: int,
        side: int,
        price: float,
        size: float,
        event_time_ms: Optional[int] = None,
    ) -> ValidationResult:
        """Update order book and optionally persist a depth snapshot."""
        self.orderbook.update(position=position, operation=operation, side=side, price=price, size=size)

        bids, asks = self.orderbook.get_snapshot(Settings.MARKET_DEPTH_ROWS)
        mid_price = self.orderbook.get_mid_price() or 0.0
        result = self.validator.validate_depth_update(mid_price=mid_price, bids=bids, asks=asks)

        if self.persist_depth_snapshots:
            timestamp_ms = event_time_ms if event_time_ms is not None else int(time.time() * 1000)
            bids_json, asks_json = self.orderbook.to_json(Settings.MARKET_DEPTH_ROWS)
            best_bid, best_ask = self.orderbook.get_best_bid_ask()
            _spread_abs, spread_bps = self.orderbook.get_spread()

            record = self._base_record(event_time_ms=timestamp_ms)
            record.update(
                {
                    "trade_id": self.orderbook.update_count,
                    "atomic_type": "depth",
                    "trade_price": "0",
                    "trade_qty": "0",
                    "bids_json": bids_json,
                    "asks_json": asks_json,
                    "best_bid_price": str(best_bid) if best_bid is not None else "0",
                    "best_bid_qty": "0",
                    "best_ask_price": str(best_ask) if best_ask is not None else "0",
                    "best_ask_qty": "0",
                    "spread_bps": str(spread_bps) if spread_bps is not None else "0",
                    "depth_sync_quality": self.orderbook.get_depth_quality_score(),
                    "depth_last_update_id": self.orderbook.update_count,
                    "raw_json": json.dumps(
                        {
                            "position": position,
                            "operation": operation,
                            "side": side,
                            "price": price,
                            "size": size,
                        }
                    ),
                }
            )
            record.update(result.to_dict())
            self.writer.add_record(record)

        return result

    def stop(self) -> None:
        """Flush and stop writer resources."""
        logger.info("Stopping data processor")
        self.writer.stop(flush_remaining=True)

    def _base_record(self, event_time_ms: int) -> dict:
        return {
            "symbol": self.symbol,
            "trade_id": 0,
            "atomic_type": "trade",
            "event_time_server_ms": event_time_ms,
            "trade_time_ms": event_time_ms,
            "received_at_ingest_ns": time.time_ns(),
            "trade_price": "0",
            "trade_qty": "0",
            "buyer_is_maker": False,
            "depth_last_update_id": 0,
            "bids_json": "[]",
            "asks_json": "[]",
            "best_bid_price": "0",
            "best_bid_qty": "0",
            "best_ask_price": "0",
            "best_ask_qty": "0",
            "spread_bps": "0",
            "depth_sync_quality": 0,
            "raw_json": "{}",
            "validation_v1": False,
            "validation_v2": False,
            "validation_v3": False,
            "validation_v4": False,
            "validation_v5": False,
            "validation_p1": False,
            "validation_final": False,
            "validation_flags": 0,
        }
