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
    print(btc_price)
    section = "section_1"
    # section = "section_2"

    if section == "section_1":
        print(type(btc_price))
        rsi = vbt.RSI.run(btc_price, window=21)

        entries2 = rsi.rsi_crossed_below(20)
        exits2 = rsi.rsi_crossed_above(80)

        entries = rsi.rsi_crossed_below(30)
        # print(entries.to_string())
        exits = rsi.rsi_crossed_above(70)
        # print(exits.to_string())
        long = False
        short = True
        if long:
            pf = vbt.Portfolio.from_signals(btc_price,
                                            entries,
                                            exits,
                                            sl_stop=0.005,    # => -0.5%
                                            # tp_stop=0.002,
                                            sl_trail=True,
                                            upon_stop_exit=vbt.portfolio.enums.StopExitMode.Reverse,
                                            init_cash=10000)
        elif short:
            pf = vbt.Portfolio.from_signals(btc_price,
                                            entries=entries2,
                                            exits=exits2,
                                            short_exits=entries,
                                            short_entries=exits,

                                            sl_stop=0.002,  # => -0.5%
                                            # tp_stop=0.002,
                                            # sl_trail=True,
                                            upon_stop_exit=vbt.portfolio.enums.StopExitMode.Reverse,

                                            # upon_dir_conflict=vbt.portfolio.enums.DirectionConflictMode.Short,
                                            # upon_dir_conflict=vbt.portfolio.enums.OppositeEntryMode.Reverse,
                                            init_cash=10000)


        pf.plot().show()
        print(pf.total_return())
        print(pf.total_profit())
        print(pf.stats())