# Placing 3 orders of 100 USD each, and exit the strategy when the orders are placed
from decimal import Decimal

from hummingbot.client.hummingbot_application import HummingbotApplication
from hummingbot.core.data_type.common import OrderType
from hummingbot.core.event.events import BuyOrderCreatedEvent
from hummingbot.core.rate_oracle.rate_oracle import RateOracle
from hummingbot.strategy.script_strategy_base import ScriptStrategyBase


class Example3(ScriptStrategyBase):
    order_amount_usd = Decimal(100)
    orders_created = 0
    orders_to_create = 3
    base = "ETH"
    quote = "USDT"
    markets = {
        "kucoin_paper_trade": {f"{base}-{quote}"}
    }

    def on_tick(self):
        # evaluate if we already placed the orders
        if self.orders_created < self.orders_to_create:
            # we need to find the amount we want to buy
            conversion_rate = RateOracle.get_instance().get_pair_rate(
                f"{self.base}-USD")  # get_instance because it's a singleton
            amount = self.order_amount_usd / conversion_rate
            price = self.connectors["kucoin_paper_trade"].get_mid_price(f"{self.base}-{self.quote}") * Decimal(0.99)
            self.buy(
                connector_name="kucoin_paper_trade",
                trading_pair="ETH-USDT",
                amount=amount,
                order_type=OrderType.LIMIT,
                price=price
            )

    # coding the event
    def did_create_buy_order(self, event: BuyOrderCreatedEvent):
        trading_pair = f"{self.base}-{self.quote}"
        if event.trading_pair == trading_pair:  # to get the trading pair of the event
            self.orders_created += 1  # increase the counter
            if self.orders_created == self.orders_to_create:
                self.logger().info("All order created !")
                HummingbotApplication.main_application().stop()
