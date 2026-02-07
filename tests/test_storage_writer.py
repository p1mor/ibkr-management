import tempfile
import time
import unittest
import sys
from pathlib import Path

import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ibkr_management.storage import ParquetWriter


def build_sample_record(symbol: str, trade_id: int = 1) -> dict:
    now_ms = int(time.time() * 1000)
    return {
        "symbol": symbol,
        "trade_id": trade_id,
        "atomic_type": "trade",
        "event_time_server_ms": now_ms,
        "trade_time_ms": now_ms,
        "received_at_ingest_ns": time.time_ns(),
        "trade_price": "5875.25",
        "trade_qty": "5",
        "buyer_is_maker": False,
        "depth_last_update_id": 0,
        "bids_json": "[]",
        "asks_json": "[]",
        "best_bid_price": "5875.00",
        "best_bid_qty": "25",
        "best_ask_price": "5875.25",
        "best_ask_qty": "30",
        "spread_bps": "4",
        "depth_sync_quality": 100,
        "raw_json": "{}",
        "validation_v1": True,
        "validation_v2": True,
        "validation_v3": True,
        "validation_v4": True,
        "validation_v5": True,
        "validation_p1": True,
        "validation_final": True,
        "validation_flags": 63,
    }


class ParquetWriterTests(unittest.TestCase):
    def test_flush_writes_file_and_tracks_stats(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "nested" / "data"
            writer = ParquetWriter(
                symbol="NQ",
                output_dir=output_dir,
                flush_interval=1,
                max_buffer_size=10,
                auto_start=False,
            )

            writer.add_record(build_sample_record(symbol="NQ"))
            written = writer.flush()

            self.assertEqual(written, 1)
            self.assertTrue(output_dir.exists())

            parquet_files = list(output_dir.glob("nq_*_trades_*.parquet"))
            self.assertEqual(len(parquet_files), 1)

            table = pq.read_table(parquet_files[0])
            self.assertEqual(table.num_rows, 1)
            self.assertEqual(table.column("symbol")[0].as_py(), "NQ")

            stats = writer.get_stats()
            self.assertEqual(stats["total_records_written"], 1)
            self.assertEqual(stats["flush_count"], 1)
            self.assertEqual(stats["current_buffer_size"], 0)


if __name__ == "__main__":
    unittest.main()
