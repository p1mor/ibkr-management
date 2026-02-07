import tempfile
import unittest
import sys
from pathlib import Path

import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ibkr_management.core import DataProcessor


class DataProcessorTests(unittest.TestCase):
    def test_depth_and_trade_flow_persists_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            processor = DataProcessor(
                symbol="ES",
                persist_depth_snapshots=True,
                auto_start_writer=False,
                output_dir=output_dir,
                flush_interval=1,
                max_buffer_size=1,
            )

            processor.process_depth_update(
                position=0,
                operation=0,
                side=1,
                price=5875.00,
                size=20,
                event_time_ms=1738876543000,
            )
            processor.process_depth_update(
                position=0,
                operation=0,
                side=0,
                price=5875.25,
                size=22,
                event_time_ms=1738876543100,
            )

            trade_result = processor.process_trade(
                trade_id=1,
                event_time_ms=1738876543200,
                price=5875.25,
                quantity=5,
                exchange="CME",
            )

            processor.stop()

            self.assertTrue(trade_result.final)

            parquet_files = list(output_dir.glob("es_*_trades_*.parquet"))
            self.assertEqual(len(parquet_files), 1)

            table = pq.read_table(parquet_files[0])
            self.assertGreaterEqual(table.num_rows, 3)


if __name__ == "__main__":
    unittest.main()
