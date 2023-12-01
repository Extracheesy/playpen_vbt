# https://www.youtube.com/watch?v=JOdEZMcvyac&t=438s
# https://vectorbt.dev/api/indicators/basic/#vectorbt.indicators.basic.RSI.rsi_crossed_above
# portfolio metrics:
# https://vectorbt.dev/api/portfolio/base/#vectorbt.portfolio.base.Portfolio.metrics
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import vectorbt as vbt

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def custom_indicator(close, rsi_window=14, ma_window=50, entry=30, exit=70):
    close_5m = close.resample("5T").last()
    # rsi = vbt.RSI.run(close, window=rsi_window).rsi.to_numpy()
    rsi = vbt.RSI.run(close_5m, window=rsi_window).rsi
    rsi, _ = rsi.align(close,
                       broadcast_axis=0,
                       method='ffill',
                       join='right')
    close = close.to_numpy()
    rsi = rsi.to_numpy()
    ma = vbt.MA.run(close, window=ma_window).ma.to_numpy()

    trend = np.where(rsi > exit, -1, 0)
    trend = np.where((rsi < entry) & (close < ma), 1, trend)

    return trend


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
    if interval == "1m":
        btc_price = vbt.YFData.download(lst_pairs,
                                        interval="1m",
                                        start=start_date_1m,
                                        end=end_date,
                                        missing_index='drop').get('Close')
        print(btc_price)
    else:
        # btc_price = vbt.YFData.download(['BTC-USD', 'ETH-USD', 'XRP-USD', 'ADA-USD'],
        btc_price = vbt.YFData.download(lst_pairs,
                                        interval="1h",
                                        start=start_date_1h,
                                        end=end_date,
                                        missing_index='drop').get('Close')
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
            param_names=['rsi_window', "ma_window", "entry", "exit"],
            output_names=['value']
        ).from_apply_func(
            custom_indicator,
            rsi_window=14,
            ma_window=100,
            entry=30,
            exit=70,
            keep_pd=True
        )
        res = ind.run(btc_price,
                      # rsi_window=[14, 35, 21],
                      rsi_window=np.arange(10, 40, step=3, dtype=int),
                      # ma_window=[21, 50, 100],
                      # ma_window=np.arange(20, 200, step=20, dtype=int),
                      # entry=[30, 40],
                      entry=np.arange(10, 40, step=4, dtype=int),
                      # exit=[60, 70],
                      exit=np.arange(60, 90, step=4, dtype=int),
                      param_product = True
                      )

        # print(res.value.to_string())
        # print(res.value)

        entries = res.value == 1
        exits = res.value == -1

        pf = vbt.Portfolio.from_signals(btc_price, entries, exits, init_cash=10000)

        # print(pf.stats())
        print(pf.total_return().to_string())
        print(pf.total_profit().to_string())

        returns = pf.total_return()
        profits = pf.total_profit()
        print(returns.max())
        print(returns.idxmax())
        print(profits.max())
        print(profits.idxmax())

        returns = pf.total_return()
        profits = pf.total_profit()

        heatmap = True
        volume = True
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


    print_hi('PyCharm')
    exit(1)

    comb_price = btc_price.vbt.concat(eth_price, keys=pd.Index(['BTC', 'ETH'], name='symbol'))

    comb_price2 = vbt.YFData.download(['BTC-USD', 'ETH-USD'], start=start, end=end, timeframe="1h").get('Close')

    print(comb_price)
    print(comb_price2)

    comb_price.vbt.drop_levels(-1, inplace=True)
    # print(comb_price)

    fast_ma = vbt.MA.run(comb_price, [10, 20], short_name='fast')
    slow_ma = vbt.MA.run(comb_price, [30, 40], short_name='slow')

    entries = fast_ma.ma_crossed_above(slow_ma)

    exits = fast_ma.ma_crossed_below(slow_ma)

    pf = vbt.Portfolio.from_signals(comb_price, entries, exits, init_cash=10000)
    print(pf.total_return())
    print(pf.total_profit())
    print(pf.stats())

    # pf = vbt.Portfolio.from_signals(comb_price, entries, exits, init_cash=10000)
    # pf.plot().show()

    mean_return = pf.total_return().groupby('symbol').mean()
    bar = mean_return.vbt.barplot(xaxis_title='Symbol', yaxis_title='Mean total return')

    bar.show()

    mult_comb_price, _ = comb_price.vbt.range_split(n=2)
    print(mult_comb_price)

    fast_ma = vbt.MA.run(mult_comb_price, [10, 20], short_name='fast')
    slow_ma = vbt.MA.run(mult_comb_price, [30, 30], short_name='slow')

    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)

    pf = vbt.Portfolio.from_signals(mult_comb_price, entries, exits, freq='1D', init_cash=10000)
    print(pf.total_return())

    mean_return = pf.total_return().groupby(['split_idx', 'symbol']).mean()
    bar = mean_return.unstack(level=-1).vbt.barplot(xaxis_title='Split index', yaxis_title='Mean total return', legend_title_text='Symbol')

    bar.show()

    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
