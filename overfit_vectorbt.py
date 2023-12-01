# https://vectorbt.dev/api/portfolio/base/#vectorbt.portfolio.base.Portfolio.from_signals

# https://www.youtube.com/watch?v=JOdEZMcvyac&t=438s
# https://vectorbt.dev/api/indicators/basic/#vectorbt.indicators.basic.RSI.rsi_crossed_above
# portfolio metrics:
# https://vectorbt.dev/api/portfolio/base/#vectorbt.portfolio.base.Portfolio.metrics

# plots
# https://vectorbt.dev/api/portfolio/base/#vectorbt.portfolio.base.Portfolio.plot_cash
# accessors
# https://vectorbt.dev/api/signals/accessors/#vectorbt.signals.accessors.SignalsSRAccessor.plot_as_markers

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import vectorbt as vbt
import talib
import datetime

def random_signal(close):
    return np.random.randint(0, 2, size=close.shape)

def optimize_rsi(close, window, entry, exit):
    rsi = vbt.IndicatorFactory.from_talib("RSI").run(close, timeperiod=window).real
    return_entry = rsi < entry
    return_exit = rsi > exit
    return return_entry, return_exit

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    """
    data = vbt.BinanceData.fetch(
        ["BTCUSDT"],
        start="2019-01-01 UTC",
        end="2023-02-02 UTC",
        timeframe="1m"
    )
    """
    theme = "dark"
    # theme = "seaborn"
    # theme = "light"
    if theme == "light":
        vbt.settings.set_theme("light")
    elif theme == "dark":
        vbt.settings.set_theme("dark")
    elif theme == "seaborn":
        vbt.settings.set_theme("seaborn")
    vbt.settings['plotting']['layout']['width'] = 1200
    vbt.settings['plotting']['layout']['height'] = 600

    # Prepare data
    end = datetime.datetime.now().strftime("%Y-%m-%d %Z %H:%M")
    end_date = datetime.datetime.now()
    # start = '2023-01-01 UTC'  # crypto is in UTC
    start = '2023-01-01 00:00'  # crypto is in UTC
    start_date_1m = end_date - timedelta(days=3) # For interval 1m
    start_date_1h = '2023-01-01 00:00'  # crypto is in UTC

    # interval = "1h"
    interval = "1m"
    # lst_pairs = ['BTC-USD', 'ETH-USD', 'XRP-USD', 'ADA-USD']
    lst_pairs = ['BTC-USD']
    # lst_pairs = ['BTC-USD', 'ETH-USD']
    if interval == "1m":
        btc_price = vbt.YFData.download(lst_pairs,
                                        interval="1m",
                                        start=start_date_1m,
                                        end=end_date,
                                        missing_index='drop').get('Close')
    else:
        # btc_price = vbt.YFData.download(['BTC-USD', 'ETH-USD', 'XRP-USD', 'ADA-USD'],
        btc_price = vbt.YFData.download(lst_pairs,
                                        interval="1h",
                                        start=start_date_1h,
                                        end=end_date,
                                        missing_index='drop').get('Close')

    btc_price, range_indexes = btc_price.vbt.range_split(n=100, range_len=1440)

    # print(btc_price)
    # print(range_indexes)

    rand_ind = vbt.IndicatorFactory(
        class_name="Random",
        short_name='rand',
        input_names=['close'],
        output_names=['signal']
    ).from_apply_func(
        random_signal
    )

    rand_res = rand_ind.run(
        btc_price
    )

    rand_entries = rand_res.signal == 1
    rand_exits = rand_res.signal == 0

    rand_exits.iloc[-1, :] = True # Close all potential open positions

    rand_pf = vbt.Portfolio.from_signals(btc_price,
                                         rand_entries,
                                         rand_exits,
                                         freq="1T",
                                         fees=0.001,
                                         init_cash=10000)

    rsi_ind = vbt.IndicatorFactory(
        class_name="optimizeRsi",
        short_name='rsi',
        input_names=['close'],
        param_names=["window",
                     "entry",
                     "exit"],
        output_names=['entries', 'exits']
    ).from_apply_func(
        optimize_rsi,
        window=14,
        entry=30,
        exit=70
    )

    step_size = 2
    entries = np.arange(10, 45, step=step_size, dtype=int)
    exits = np.arange(55, 95, step=step_size, dtype=int)
    volume = False
    heatmap = True
    if volume:
        windows = np.arange(10, 45, step=step_size, dtype=int)
    elif heatmap:
        windows = 14

    rsi_res = rsi_ind.run(
        btc_price,
        window=windows,
        exit=exits,
        entry=entries,
        param_product=True
    )

    rsi_entries = rsi_res.entries
    rsi_exits = rsi_res.exits

    rsi_exits.iloc[-1, :] = True # Close all potential open positions

    rsi_pf = vbt.Portfolio.from_signals(btc_price,
                                        rsi_entries,
                                        rsi_exits,
                                        freq="1T",
                                        fees=0.001,
                                        init_cash=10000)

    volume = True
    heatmap = True
    random_comp = False
    if volume:
        fig = rsi_pf.total_return().vbt.volume(
            x_level="rsi_exit",
            y_level="rsi_entry",
            z_level="rsi_window",
            slider_level="split_idx"
        )
        fig.show()
    elif heatmap:
        rsi_tot_returns = rsi_pf.total_return().groupby(
            level=['rsi_exit', 'rsi_entry']
        ).mean()

        print(rsi_tot_returns)

        fig = rsi_pf.total_return().vbt.heatmap(
            x_level="rsi_exit",
            y_level="rsi_entry",
            slider_level="split_idx"
        )
        fig.show()

        fig = rsi_tot_returns.vbt.heatmap(
            x_level="rsi_exit",
            y_level="rsi_entry",
        )
        fig.show()
    elif random_comp:
        rand_tot_returns = rand_pf.total_return()
        # rsi_tot_returns = rsi_pf.total_return()

        rsi_tot_returns = rsi_pf.total_return().groupby(
            level=['rsi_exit', 'rsi_entry']
        ).mean()

        print(rsi_tot_returns)
        print(rand_tot_returns)

        box = vbt.plotting.Box(
            data=rsi_tot_returns,
            trace_names=["RSI_stat"]
        )
        box.fig.show()

        box = vbt.plotting.Box(
            data=rand_tot_returns,
            trace_names=["random_stat"]
        )
        box.fig.show()

        df = pd.DataFrame({
            "rsi":list(rsi_tot_returns),
            "rand":list(rand_tot_returns)
        })

        print(df.median())

        box = vbt.plotting.Box(
            data=df,
            trace_names=["rsi", "rand"]
        )
        box.fig.show()

    exit(1)

    print(rsi_pf.total_return())
    print(rsi_pf.total_profit())
    print(rsi_pf.stats())