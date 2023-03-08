# The purpose of the script is to log the best-bid best-ask at mid-price for each connector, every tick.

from hummingbot.strategy.script_strategy_base import ScriptStrategyBase


# Define the markets: a dictionary where the key is the connector name, and the values, the pairs
class Example1(ScriptStrategyBase):
    markets = {
        "binance_paper_trade": {"ETH-USDT"},
        "kucoin_paper_trade": {"ETH-USDT"},
        "gate_io_paper_trade": {"ETH-USDT"}
    }

    # Define the method on tick
    def on_tick(self):
        for connector_name, connector in self.connectors.items():
            self.logger().info(f"Connector: {connector_name}")
            self.logger().info(f"Best ask: {connector.get_price('ETH-USDT', True)}")  # Log the best ask
            self.logger().info(f"Best bid: {connector.get_price('ETH-USDT', False)}")  # Log the best bid
            self.logger().info(f"Mid price: {connector.get_mid_price('ETH-USDT')}")
