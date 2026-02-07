import unittest

from config import ContractBuilder, Settings
from core import DataValidator, OrderBook


class SmokeTests(unittest.TestCase):
    def test_settings_validate_config(self) -> None:
        is_valid, errors = Settings.validate_config()
        self.assertIsInstance(is_valid, bool)
        self.assertIsInstance(errors, list)

    def test_contract_builder_future_defaults(self) -> None:
        contract = ContractBuilder.create_future_contract()
        self.assertEqual(contract.secType, "FUT")
        self.assertTrue(contract.symbol)
        self.assertTrue(contract.exchange)

    def test_orderbook_spread_positive(self) -> None:
        orderbook = OrderBook(max_depth=10)
        orderbook.update(position=0, operation=0, side=1, price=5875.00, size=10)
        orderbook.update(position=0, operation=0, side=0, price=5875.25, size=12)
        spread_abs, spread_bps = orderbook.get_spread()
        self.assertIsNotNone(spread_abs)
        self.assertIsNotNone(spread_bps)
        self.assertGreater(spread_abs, 0)
        self.assertGreater(spread_bps, 0)

    def test_data_validator_valid_trade(self) -> None:
        validator = DataValidator(max_spread_threshold=0.1, min_depth_levels=1)
        result = validator.validate_trade(
            price=5875.25,
            quantity=5,
            event_time=1738876543210,
            bids=[(0, {"price": 5875.00, "size": 25})],
            asks=[(0, {"price": 5875.25, "size": 30})],
        )
        self.assertTrue(result.final)


if __name__ == "__main__":
    unittest.main()

