import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import vectorbt as vbt

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def custom_indicator(close, rsi_window=14, ma_window=50):
    print(close)
    rsi = vbt.RSI.run(close, window=rsi_window).rsi.to_numpy()
    ma = vbt.MA.run(close, window=ma_window).ma.to_numpy()

    trend = np.where(rsi>70, -1, 0)
    trend = np.where((rsi<30) & (close < ma), 1, trend)

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
    start_date_1h = '2023-10-15 00:00'  # crypto is in UTC

    # btc_price = vbt.YFData.download('BTC-USD', start=start, end=end, missing_index='drop').get('Close')
    # eth_price = vbt.YFData.download('ETH-USD', start=start, end=end, missing_index='drop').get('Close')

    interval = "1h"
    # interval = "1m"
    # interval = "5m"
    # lst_pairs = ['BTC-USD', 'ETH-USD', 'XRP-USD', 'ADA-USD']
    # lst_pairs = ['BTC-USD', 'ETH-USD']
    lst_pairs = ['BTC-USD']
    if interval == "1m" or interval == "5m":
        btc_price = vbt.YFData.download(lst_pairs,
                                        interval=interval,
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
    section = "section_bbbands"
    # section = "heatmap"
    # section = "bigwill"

    if section == "section_1":
        print(btc_price)
        print(type(btc_price))
        rsi = vbt.RSI.run(btc_price, window=[14])
        print(rsi.rsi)
        entries = rsi.rsi_crossed_below(30)
        # print(entries.to_string())
        exits = rsi.rsi_crossed_above(70)
        # print(exits.to_string())
        pf = vbt.Portfolio.from_signals(btc_price,
                                        entries,
                                        exits,
                                        init_cash=10000)
        pf.plot().show()
        # print(pf.total_return())
        # print(pf.total_profit())
        # print(pf.stats())
    elif section == "section_2":
        ind = vbt.IndicatorFactory(
            class_name = "Combination",
            short_name = 'comb',
            input_names=['close'],
            param_names=['rsi_window', "ma_window"],
            output_names=['value']
        ).from_apply_func(
            custom_indicator,
            rsi_window=14,
            ma_window=100
        )
        res = ind.run(btc_price, rsi_window=21, ma_window=50)
        # print(res.value.to_string())
        print(res.value)

        entries = res.value == 1
        exits = res.value == -1

        pf = vbt.Portfolio.from_signals(btc_price, entries, exits, init_cash=10000)

        # print(pf.stats())
        print(pf.total_return())
        print(pf.total_profit())
    elif section == "section_bbbands":
        print(btc_price)
        print(type(btc_price))
        bbbands = vbt.BBANDS.run(btc_price, window=[20], alpha=[2], short_name='bb')

        fig = bbbands.plot()
        fig.show()

        price_cross_above_upper = bbbands.close_crossed_above(bbbands.upper)
        price_cross_bellow_middle = bbbands.close_crossed_below(bbbands.middle)

        # Define long entry and exit signals
        long_entry = (btc_price > bbbands.upper)
        long_exit = (btc_price < bbbands.middle)  # You can adjust the exit condition

        # Define short entry and exit signals
        short_entry = (btc_price < bbbands.lower)
        short_exit = (btc_price > bbbands.middle)  # You can adjust the exit condition

        # Create a signals DataFrame
        signals = pd.DataFrame({
            'long_entry': long_entry,
            'long_exit': long_exit,
            # 'short_entry': short_entry,
            # 'short_exit': short_exit
        })

        # print(exits.to_string())
        pf = vbt.Portfolio.from_signals(btc_price,
                                        long_entry,
                                        long_exit,
                                        # fees=0.0006,
                                        # sl_stop=0.005,
                                        init_cash=10000)
        # 0.01 = 1%.
        # 0.0007 = 0.006 %.

        fig = pf.plot()

        # Access the axes and retrieve subplot names
        # subplot_names = [ax.get_title() for ax in fig.axes]
        # print(subplot_names)

        fig.show()
        """
        pf.plot_positions().show()
        pf.plot_drawdowns().show()
        pf.plot_cum_returns().show()
        pf.plot_cash_flow().show()
        pf.plot_cash().show()
        pf.plot_assets().show()
        pf.plot_asset_value().show()
        pf.plot_asset_flow().show()
        pf.plot_orders().show()
        pf.plot_position_pnl().show()
        pf.plot_trade_pnl().show()
        pf.plot_trades().show()
        pf.plot_underwater().show()
        pf.plot_value().show()
        # pf.plots_defaults().show()
        pf.plot_net_exposure().show()
        pf.plot_gross_exposure().show()
        """

        pf.plot(subplots=['orders', 'trades', 'trade_pnl',
                          'cum_returns', 'drawdowns',
                          'asset_value', 'assets',
                          'cash', 'cash_flow',
                          'value',
                          'underwater', 'gross_exposure']).show()


        # Backtest the portfolio
        returns = pf.total_return()

        # Plot price, Bollinger Bands, signals, and trade PnL

        print(type(plt))
        plt.figure(figsize=(12, 6))


        plt.plot(btc_price, label='Price')
        plt.plot(bbbands.upper, label='Upper Bollinger Band', linestyle='--')
        plt.plot(bbbands.middle, label='Middle Bollinger Band', linestyle='--')
        plt.plot(bbbands.lower, label='Lower Bollinger Band', linestyle='--')

        # Highlight long entry and short entry signals
        # plt.scatter(signals.index[signals['long_entry']], btc_price[signals['long_entry']], marker='^', color='g',
        #             label='Long Entry')
        # plt.scatter(signals.index[signals['short_entry']], btc_price[signals['short_entry']], marker='v', color='r',
        #             label='Short Entry')

        # Highlight long exit and short exit signals
        # plt.scatter(signals.index[signals['long_exit']], btc_price[signals['long_exit']], marker='v', color='r',
        #             label='Long Exit')
        # plt.scatter(signals.index[signals['short_exit']], btc_price[signals['short_exit']], marker='o', color='orange',
        #             label='Short Exit')

        # Plot trade PnL
        # pf.plot_trade_pnl()
        plt.title('Bollinger Bands Strategy with Signals and Trade PnL')
        plt.grid()
        plt.show()

        # pf.plot().show()
        # print(pf.total_return())
        # print(pf.total_profit())
        print(pf.stats())
    elif section == "heatmap":

        symbols = ["BTC-USD", "ETH-USD", "XRP-USD"]
        price = vbt.BinanceData.download(symbols, missing_index='drop')
        # price = vbt.BinanceData.download(symbols, missing_index='drop').get('Close')

        windows = np.arange(2, 101)
        fast_ma, slow_ma = vbt.MA.run_combs(price, window=windows, r=2, short_names=['fast', 'slow'])
        entries = fast_ma.ma_crossed_above(slow_ma)
        exits = fast_ma.ma_crossed_below(slow_ma)

        pf_kwargs = dict(size=np.inf, fees=0.001, freq='1D')
        pf = vbt.Portfolio.from_signals(price, entries, exits, **pf_kwargs)

        fig = pf.total_return().vbt.heatmap(
            x_level='fast_window', y_level='slow_window', slider_level='symbol', symmetric=True,
            trace_kwargs=dict(colorbar=dict(title='Total return', tickformat='%')))
        fig.show()

        windows = np.arange(1, 101)
        print("len: ", len(windows))
        print(windows)
        alpha = np.arange(1, 5.0, 4/len(windows))
        print("len: ", len(alpha))
        print(alpha)

        fast_bbbands, slow_bbbands = vbt.BBANDS.run_combs(price, window=windows, alpha=alpha, short_names=['fast', 'slow'])
        bbbands = vbt.BBANDS.run_combs(price, window=windows, alpha=alpha, short_names=['fast', 'slow'])

        print("toto")

        """ """
        entries = fast_ma.ma_crossed_above(slow_ma)
        exits = fast_ma.ma_crossed_below(slow_ma)

        entries = (btc_price > bbbands.upper)
        exits = (btc_price < bbbands.middle)

        entries = bbbands.close_crossed_above(bbbands.upper)
        exits = bbbands.close_crossed_below(bbbands.middle)
        """ """

        entries = fast_bbbands.upper_crossed_below(price)

        print("titi")
        exits = slow_bbbands.middle_crossed_above(price)
        print("tutu")

        pf_kwargs = dict(size=np.inf, fees=0.001, freq='1H')
        pf = vbt.Portfolio.from_signals(price, entries, exits, **pf_kwargs)
        print("tyty")

        heatmap = vbt.plotting.Heatmap(
            data=bbbands)
        heatmap.fig.show()


        fig = pf.total_return().vbt.heatmap(
            x_level='fast_window', y_level='slow_window', slider_level='symbol', symmetric=True,
            # x_level='window', y_level='alpha', slider_level='symbol', symmetric=True,
            trace_kwargs=dict(colorbar=dict(title='Total return', tickformat='%')))
        fig.show()
    elif section == "bigwill":
        print_hi('PyCharm')




    print_hi('PyCharm')
    exit(1)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
