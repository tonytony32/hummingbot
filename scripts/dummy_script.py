from hummingbot.strategy.script_strategy_base import ScriptStrategyBase


class DummyScritp(ScriptStrategyBase):
    markets = {"binance_paper_trade": {"ETH-USDC"}}

    def on_tick(self):
        self.logger().info("Hello world")
