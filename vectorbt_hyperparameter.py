# https://www.youtube.com/watch?v=JOdEZMcvyac&t=438s
# https://vectorbt.dev/api/indicators/basic/#vectorbt.indicators.basic.RSI.rsi_crossed_above
# portfolio metrics:
# https://vectorbt.dev/api/portfolio/base/#vectorbt.portfolio.base.Portfolio.metrics

# https://medium.datadriveninvestor.com/superfast-supertrend-6269a3af0c2a

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import time
import talib
import ta

from numba import njit
import vectorbt as vbt



@njit
def produce_signal(rsi, entry, exit):
    trend = np.where(rsi > exit, -1, 0)
    trend = np.where((rsi < entry), 1, trend)

    return trend

def print_hi(name, start_time):
    # Use a breakpoint in the code line below to debug your script.
    # Record the end time
    end_time = time.time()
    # Calculate the elapsed time
    elapsed_time = end_time - start_time
    # Print the elapsed time
    print(f"Elapsed Time: {elapsed_time} seconds")
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def custom_indicator(close, rsi_window=14, entry=30, exit=70):
    # rsi = vbt.RSI.run(close, window=rsi_window).rsi.to_numpy()

    use_talib = False
    use_ta = False
    use_factory = True

    if use_talib:
        rsi = talib.RSI(close, rsi_window)
    elif use_factory:
        RSI = vbt.IndicatorFactory.from_talib('RSI')
        rsi = RSI.run(close, rsi_window).real.to_numpy()
    elif use_ta:
        rsi = ta.momentum.rsi(close=close, window=rsi_window)
        rsi = rsi.to_numpy()
    else:
        rsi = vbt.RSI.run(close, window=rsi_window).rsi

    return produce_signal(rsi, entry, exit)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Record the start time
    start_time = time.time()
    """
    data = vbt.BinanceData.fetch(
        ["BTCUSDT"],
        start="2019-01-01 UTC",
        end="2023-02-02 UTC",
        timeframe="1m"
    )
    """

    # Prepare data
    end = datetime.utcnow().strftime("%Y-%m-%d %Z %H:%M")
    end_date = datetime.now()
    # start = '2023-01-01 UTC'  # crypto is in UTC
    start = '2023-01-01 00:00'  # crypto is in UTC
    start_date_1m = end_date - timedelta(days=3) # For interval 1m
    start_date_1h = '2023-01-01 00:00'  # crypto is in UTC

    # btc_price = vbt.YFData.download('BTC-USD', start=start, end=end, missing_index='drop').get('Close')
    # eth_price = vbt.YFData.download('ETH-USD', start=start, end=end, missing_index='drop').get('Close')

    # interval = "1h"
    interval = "1m"
    lst_pairs = ['BTC-USD', 'ETH-USD', 'XRP-USD', 'ADA-USD']
    # lst_pairs = ['BTC-USD']
    lst_pairs = ['BTC-USD', 'ETH-USD']
    data_from_csv = True
    if data_from_csv:
        btc_price = pd.read_csv("data.csv")
        print(btc_price)
        btc_price["Datetime"] = pd.to_datetime((btc_price["Datetime"]))
        btc_price.set_index("Datetime", inplace=True)

        # btc_price = btc_price["BTC-USD"]

        print(btc_price)
    elif interval == "1m":
        btc_price = vbt.YFData.download(lst_pairs,
                                        interval="1m",
                                        start=start_date_1m,
                                        end=end_date,
                                        missing_index='drop').get('Close')
        btc_price.to_csv("data.csv")
    else:
        # btc_price = vbt.YFData.download(['BTC-USD', 'ETH-USD', 'XRP-USD', 'ADA-USD'],
        btc_price = vbt.YFData.download(lst_pairs,
                                        interval="1h",
                                        start=start_date_1h,
                                        end=end_date,
                                        missing_index='drop').get('Close')
        btc_price.to_csv("data.csv")
        print(btc_price)

    section = "section_1"
    section = "section_2"

    if section == "section_1":
        print(btc_price)
        print(type(btc_price))
        rsi = vbt.RSI.run(btc_price, window=[14])
        print(rsi.rsi)
        entries = rsi.rsi_crossed_below(30)
        # print(entries.to_string())
        exits = rsi.rsi_crossed_above(70)
        # print(exits.to_string())
        pf = vbt.Portfolio.from_signals(btc_price, entries, exits, init_cash=10000)
        pf.plot().show()
        # print(pf.total_return())
        # print(pf.total_profit())
        # print(pf.stats())
    elif section == "section_2":
        ind = vbt.IndicatorFactory(
            class_name = "Combination",
            short_name = 'comb',
            input_names=['close'],
            param_names=['rsi_window', "entry", "exit"],
            output_names=['value']
        ).from_apply_func(
            custom_indicator,
            rsi_window=14,
            entry=30,
            exit=70,
            # keep_pd=True,
            # to_2d=False
        )

        rsi_window = np.arange(10, 40, step=2, dtype=int)
        master_returns = []
        master_profits = []
        memory_ram = False
        if memory_ram:
            for window in rsi_window:
                res = ind.run(btc_price,
                              rsi_window=window,
                              entry=np.arange(10, 40, step=2, dtype=int),
                              exit=np.arange(60, 90, step=2, dtype=int),
                              param_product=True
                              )
                # print(res.value.to_string())
                # print(res.value)
                entries = res.value == 1
                exits = res.value == -1
                pf = vbt.Portfolio.from_signals(btc_price, entries, exits, init_cash=10000)

                master_returns.append(pf.total_return())
                master_profits.append(pf.total_profit())

            returns = pd.concat(master_returns)
            profits = pd.concat(master_profits)
        else:
            res = ind.run(btc_price,
                          rsi_window=np.arange(10, 40, step=2, dtype=int),
                          entry=np.arange(10, 40, step=2, dtype=int),
                          exit=np.arange(60, 90, step=2, dtype=int),
                          param_product=True
                          )
            # print(res.value.to_string())
            # print(res.value)
            entries = res.value == 1
            exits = res.value == -1
            pf = vbt.Portfolio.from_signals(btc_price, entries, exits, init_cash=10000)

            returns = pf.total_return()
            profits = pf.total_profit()

        print(returns.max())
        print(returns.idxmax())
        print(profits.max())
        print(profits.idxmax())

        returns = pf.total_return()
        profits = pf.total_profit()

        heatmap = False
        volume = False
        if heatmap:
            returns = returns.groupby(level=["comb_entry", "comb_exit", "symbol"]).mean()

            print(returns.to_string())
            print(profits.to_string())

            print(returns.max())
            print(returns.idxmax())
            print(profits.max())
            print(profits.idxmax())

            # "comb_rsi_window  comb_ma_window  symbol "

            fig = returns.vbt.heatmap(
                x_level="comb_exit",
                y_level="comb_entry",
                slider_level="symbol"
            )

            fig.show()
        elif volume:
            print(returns.to_string())
            print(profits.to_string())

            print(returns.max())
            print(returns.idxmax())
            print(profits.max())
            print(profits.idxmax())

            # "comb_rsi_window  comb_ma_window  symbol "

            fig = returns.vbt.volume(
                x_level="comb_rsi_window",
                y_level="comb_entry",
                z_level="comb_exit",
                slider_level="symbol"
            )

            fig.show()

        else:
            # returns = returns[returns.index.isin(['BTC-USD'], level="symbol")]
            # profits = profits[profits.index.isin(['BTC-USD'], level="symbol")]

            print(returns.to_string())
            print(profits.to_string())

            print(returns.max())
            print(returns.idxmax())
            print(profits.max())
            print(profits.idxmax())


    print_hi('PyCharm', start_time)
    exit(1)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
