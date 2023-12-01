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
        fast_ma = vbt.MA.run(btc_price, window=50, short_name='fast')
        slow_ma = vbt.MA.run(btc_price, window=200, short_name='slow')

        entries = fast_ma.ma_crossed_above(slow_ma)
        exits = fast_ma.ma_crossed_below(slow_ma)

        pf = vbt.Portfolio.from_signals(btc_price, entries, exits, init_cash=10000)

        plot_1 = False
        plot_2 = False
        plot_3 = False
        plot_4 = False
        plot_5 = True
        if plot_1:
            pf.plot().show()
            pf.orders.plot().show()
            pf.trades.plot_pnl().show()
            pf.trades.plot().show()

            print(pf.orders.records_arr)
            print(pf.trades.records_arr)

            print(pf.total_return())
            print(pf.total_profit())
            print(pf.stats())
        elif plot_2:
            # fig = btc_price.vbt.plot(trace_kwargs=dict(name='price', line=dict(color='red')))
            fig = btc_price.vbt.plot(trace_kwargs=dict(name='price'))
            fig = fast_ma.ma.vbt.plot(trace_kwargs=dict(name='fast_ma', line=dict(color='blue')), fig=fig)
            fig = slow_ma.ma.vbt.plot(trace_kwargs=dict(name='slow_ma', line=dict(color='green')), fig=fig)
            fig = entries.vbt.signals.plot_as_entry_markers(btc_price, fig=fig)
            fig = exits.vbt.signals.plot_as_exit_markers(btc_price, fig=fig)
            fig.show()
        elif plot_3:
            fig = pf.plot(subplots=['orders', 'trades', 'trade_pnl',
                                    'cum_returns', 'drawdowns',
                                    'asset_value', 'assets',
                                    'cash', 'cash_flow',
                                    'value',
                                    'underwater', 'gross_exposure'])
            fig.show()
        elif plot_4:
            fig = pf.plot(subplots=[('price', dict(title='Price', yaxis_kwargs=dict(title='Price'))),
                                    ('price', dict(title='Price', yaxis_kwargs=dict(title='Price'))),
                                    'orders', 'trades', 'trade_pnl',
                                    'cum_returns', 'drawdowns',
                                    'asset_value', 'assets',
                                    'cash', 'cash_flow',
                                    'value',
                                    'underwater', 'gross_exposure'])

            scatter = vbt.plotting.Scatter(
                data = btc_price,
                x_labels= btc_price.index,
                trace_names=["Price"],
                # trace_kwargs=dict(line=dict(color='red')),
                add_trace_kwargs=dict(row=1, col=1),
                fig=fig)

            fast_ma_scatter = vbt.plotting.Scatter(
                data = fast_ma.ma,
                x_labels= fast_ma.ma.index,
                trace_names=["Fast_ma"],
                # trace_kwargs=dict(line=dict(color='red')),
                add_trace_kwargs=dict(row=1, col=1),
                fig=fig)

            slow_ma_scatter = vbt.plotting.Scatter(
                data = slow_ma.ma,
                x_labels= slow_ma.ma.index,
                trace_names=["Slow_ma"],
                # trace_kwargs=dict(line=dict(color='red')),
                add_trace_kwargs=dict(row=1, col=1),
                fig=fig)

            scatter2 = vbt.plotting.Scatter(
                data = slow_ma.ma,
                x_labels= slow_ma.ma.index,
                trace_names=["slow_ma"],
                # trace_kwargs=dict(line=dict(color='red')),
                add_trace_kwargs=dict(row=1, col=2),
                fig=fig)

            scatter3 = vbt.plotting.Scatter(
                data = fast_ma.ma,
                x_labels= fast_ma.ma.index,
                trace_names=["fast_ma"],
                # trace_kwargs=dict(line=dict(color='red')),
                add_trace_kwargs=dict(row=1, col=2),
                fig=fig)

            entries_plot = entries.vbt.signals.plot_as_entry_markers(slow_ma.ma,
                                                                     add_trace_kwargs=dict(row=1, col=2),
                                                                     fig=fig)
            exits_plot = exits.vbt.signals.plot_as_exit_markers(slow_ma.ma,
                                                                add_trace_kwargs=dict(row=1, col=2),
                                                                fig=fig)
            fig.add_hline(y=37000,
                          line_color="#FFFFFF",
                          row=1,
                          col=2,
                          line_width=5)

            fig.show()
        elif plot_5:
            fig = pf.plot(subplots=[('price', dict(title='Price', yaxis_kwargs=dict(title='Price'))),
                                    ('price', dict(title='Price', yaxis_kwargs=dict(title='Price'))),
                                    'orders', 'trades', 'trade_pnl',
                                    'cum_returns', 'drawdowns',
                                    'asset_value', 'assets',
                                    'cash', 'cash_flow',
                                    'value',
                                    'underwater', 'gross_exposure'],
                          make_subplots_kwargs=dict(rows=16, cols=2))

            scatter = vbt.plotting.Scatter(
                data = btc_price,
                x_labels= btc_price.index,
                trace_names=["Price"],
                # trace_kwargs=dict(line=dict(color='red')),
                add_trace_kwargs=dict(row=1, col=1),
                fig=fig)

            fast_ma_scatter = vbt.plotting.Scatter(
                data = fast_ma.ma,
                x_labels= fast_ma.ma.index,
                trace_names=["Fast_ma"],
                # trace_kwargs=dict(line=dict(color='red')),
                add_trace_kwargs=dict(row=1, col=1),
                fig=fig)

            slow_ma_scatter = vbt.plotting.Scatter(
                data = slow_ma.ma,
                x_labels= slow_ma.ma.index,
                trace_names=["Slow_ma"],
                # trace_kwargs=dict(line=dict(color='red')),
                add_trace_kwargs=dict(row=1, col=1),
                fig=fig)

            scatter2 = vbt.plotting.Scatter(
                data = slow_ma.ma,
                x_labels= slow_ma.ma.index,
                trace_names=["slow_ma"],
                # trace_kwargs=dict(line=dict(color='red')),
                add_trace_kwargs=dict(row=1, col=2),
                fig=fig)

            scatter3 = vbt.plotting.Scatter(
                data = fast_ma.ma,
                x_labels= fast_ma.ma.index,
                trace_names=["fast_ma"],
                # trace_kwargs=dict(line=dict(color='red')),
                add_trace_kwargs=dict(row=1, col=2),
                fig=fig)

            entries_plot = entries.vbt.signals.plot_as_entry_markers(slow_ma.ma,
                                                                     add_trace_kwargs=dict(row=1, col=2),
                                                                     fig=fig)
            exits_plot = exits.vbt.signals.plot_as_exit_markers(slow_ma.ma,
                                                                add_trace_kwargs=dict(row=1, col=2),
                                                                fig=fig)
            fig.add_hline(y=37000,
                          line_color="#FFFFFF",
                          row=1,
                          col=2,
                          line_width=5)

            fig.show()

        # print(res.value.to_string())
        # print(res.value)

        print_hi('PyCharm')
        exit(1)


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
