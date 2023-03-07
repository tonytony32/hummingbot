# This example presents information and market data taken from three different markets, displays table with the balance
# in each market and a table with the market information from a known object called market_status_data_frame, including
# some extra depth that is defined here

from hummingbot.strategy.script_strategy_base import ScriptStrategyBase


class Example2(ScriptStrategyBase):
    markets = {
        "binance_paper_trade": {"ETH-USDT"},
        "kucoin_paper_trade": {"ETH-USDT"},
        "gate_io_paper_trade": {"ETH-USDT"}
    }

    def format_status(self) -> str:  # Define a custom-format-status
        """
        Returns status of the current strategy on user balances and current active orders. This function is called
        when status command is issued. Override this function to create custom status display output.
        """
        if not self.ready_to_trade:
            return "Market connectors are not ready."
        lines = []
        warning_lines = []
        warning_lines.extend(self.network_warning(self.get_market_trading_pair_tuples()))

        balance_df = self.get_balance_df()  # This is the first sheet for balances
        lines.extend(["", "  Balances:"] + ["    " + line for line in balance_df.to_string(index=False).split("\n")])
        market_status_df = self.get_market_status_df_with_depth()  # This is the one added with the market status data frame
        lines.extend(["", "  Market Status Data Frame:"] + ["    " + line for line in
                                                            market_status_df.to_string(index=False).split("\n")])

        warning_lines.extend(self.balance_warning(self.get_market_trading_pair_tuples()))
        if len(warning_lines) > 0:
            lines.extend(["", "*** WARNINGS ***"] + warning_lines)
        return "\n".join(lines)

    # Method to include the market data frame
    def get_market_status_df_with_depth(self):  # a new method is created
        market_status_df = self.market_status_data_frame(self.get_market_trading_pair_tuples())
        # The following expression was created through the expression explorer. lambda as a simple function and axis=1 because
        # we take into account the column, not the row
        market_status_df["Exchange"] = market_status_df.apply(
            lambda x: x["Exchange"].strip("PaperTrade") + "paper_trade", axis=1)
        market_status_df["Volume (+1%)"] = market_status_df.apply(
            lambda x: self.get_volume_for_percentage_from_mid_price(x, 0.01), axis=1)
        market_status_df["Volume (-1%)"] = market_status_df.apply(
            lambda x: self.get_volume_for_percentage_from_mid_price(x, -0.01), axis=1)
        return market_status_df

    def get_volume_for_percentage_from_mid_price(self, row, percentage):
        price = row["Mid Price"] * (1 + percentage)  # takes the mid price and search for the new price a bit up/down
        is_buy = percentage > 0  # the method takes if it's buy or sell
        result = self.connectors[row["Exchange"]].get_volume_for_price(row["Market"], is_buy, price)
        return result.result_volume
