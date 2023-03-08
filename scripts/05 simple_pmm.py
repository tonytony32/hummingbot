from decimal import Decimal
from typing import List

from hummingbot.core.data_type.common import OrderType, PriceType, TradeType
from hummingbot.core.data_type.order_candidate import OrderCandidate
from hummingbot.strategy.script_strategy_base import ScriptStrategyBase


class SimplePMM(ScriptStrategyBase):
    bid_spread = 0.5
    ask_spread = 0.5
    order_refresh_time = 20
    order_amount = 0.1   # it is in currency base
    trading_pair = "ETH-USDT"
    exchange = "binance_paper_trade"
    price_source = PriceType.MidPrice
    create_timestamp = 0   # it will allow the execution of the next batch of orders

    markets = {exchange: {trading_pair}}

    def on_tick(self):
        # Check if it's time to place orders
        if self.create_timestamp <= self.current_timestamp:
            # Cancel all orders
            self.cancel_all_orders()
            # Create the proposal
            proposal: List[OrderCandidate] = self.create_proposal()
            # Adjust the proposal to our budget
            proposal_adjusted: List[OrderCandidate] = self.adjust_proposal_to_budget(proposal)
            # Place the orders and check if the amount is enough, or not enough balance
            self.place_orders(proposal_adjusted)
            # Update the time variable
            self.create_timestamp = self.order_refresh_time = self.current_timestamp

    def cancel_all_orders(self):
        orders = self.get_active_orders(self.exchange)
        for order in orders:
            self.cancel(self.exchange, order.trading_pair, order.client_order_id)

    # If there were more exchanges, we need to create a loop:
    #    def cancel_all_orders(self):
    #        for exchange in self.connectors.keys()
    #            orders = self.get_active_orders(exchange)
    #            for order in orders:
    #                self.cancel(exchange, order.trading_pair, order.client_order_id)

    def create_proposal(self):
        # First we get our reference price. With the method we select the trading pair and the type (mid or last traded)
        ref_price = self.connectors[self.exchange].get_price_by_type(self.trading_pair, self.price_source)
        # Then calculate the buy and sell based on the spread
        buy_price = ref_price * Decimal(1 - self.bid_spread)
        sell_price = ref_price * Decimal(1 + self.ask_spread)

        # Now to create the order candidates
        buy_order = OrderCandidate(trading_pair=self.trading_pair, is_maker=True, order_type=OrderType.LIMIT,
                                   order_side=TradeType.BUY, amount=Decimal(self.order_amount), price=buy_price)
        sell_order = OrderCandidate(trading_pair=self.trading_pair, is_maker=True, order_type=OrderType.LIMIT,
                                    order_side=TradeType.SELL, amount=Decimal(self.order_amount), price=sell_price)
        return [buy_order, sell_order]

    # Adjust the proposal to the budget
    def adjust_proposal_to_budget(self, proposal: List[OrderCandidate]):
        # We will use the budget checker that is in the connector to adjust the budget. Adjust candidates order several
        proposal_adjusted = self.connectors[self.exchange].budget_checker.adjust_candidates(proposal, all_or_none=True)
        return proposal_adjusted

    # Place orders method
    def place_orders(self, proposal: List[OrderCandidate]):
        # If the amount is 0, it will stop.
        for order in proposal:
            # Check if it's buy or sell, and implement the method; or create a new method that will do the thing for us
            self.place_order(connector_name=self.exchange, order=order)

    def place_order(self, connector_name: str, order: OrderCandidate):
        # Check the side of the order
        if order.order_side == TradeType.SELL:  # if this is the case, we are going to sell
            self.sell(connector_name=connector_name, trading_pair=order.trading_pair, amount=order.amount,
                      order_type=order.order_type, price=order.price)
        elif order.order_side == TradeType.BUY:
            self.buy(connector_name=connector_name, trading_pair=order.trading_pair, amount=order.amount,
                     order_type=order.order_type, price=order.price)
