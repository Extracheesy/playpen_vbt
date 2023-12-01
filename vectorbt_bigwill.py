# https://www.youtube.com/watch?v=JOdEZMcvyac&t=438s
# https://vectorbt.dev/api/indicators/basic/#vectorbt.indicators.basic.RSI.rsi_crossed_above
# https://vectorbt.dev/api/portfolio/base/#vectorbt.portfolio.base.Portfolio.plot_cum_returns



# https://www.youtube.com/watch?v=JOdEZMcvyac&t=438s
# https://vectorbt.dev/api/indicators/basic/#vectorbt.indicators.basic.RSI.rsi_crossed_above
# portfolio metrics:
# https://vectorbt.dev/api/portfolio/base/#vectorbt.portfolio.base.Portfolio.metrics
import talib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import ta
import vectorbt as vbt

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def custom_indicator(close, high, low,
                     ao_window_1=6,
                     ao_window_2=22,
                     ma_window_100=100,
                     ma_window_200=200,
                     rsi_window=14,
                     period=14,
                     AO_Threshold=0,
                     stochOverBought=0.8,
                     stochOverSold=0.2,
                     willOverSold=-80,
                     willOverBought=-10
                     ):

    # SMAIndicator = vbt.IndicatorFactory.from_ta('SMAIndicator')
    AOIndicator = vbt.IndicatorFactory.from_ta('AwesomeOscillatorIndicator')
    WilliamsRIndicator = vbt.IndicatorFactory.from_ta('WilliamsRIndicator')
    StochRSIIndicator = vbt.IndicatorFactory.from_ta('StochRSIIndicator')

    # indicators = vbt.IndicatorFactory.get_ta_indicators()
    # print(indicators)

    ao = AOIndicator.run(high=high, low=low, window1=ao_window_1, window2=ao_window_2)
    # print(ao.awesome_oscillator)

    ao_n1 = AOIndicator.run(high=high.shift(1), low=low.shift(1), window1=ao_window_1, window2=ao_window_2)
    # print(ao_n1.awesome_oscillator)

    willr = WilliamsRIndicator.run(high=high, low=low, close=close, lbp=period)
    # print(willr.williams_r)

    stoch_rsi = StochRSIIndicator.run(close=close, window=rsi_window)
    # print(stoch_rsi.stochrsi)

    sma_100 = vbt.MA.run(close, window=ma_window_100).ma.to_numpy()
    sma_200 = vbt.MA.run(close, window=ma_window_200).ma.to_numpy()

    # sma_100 = SMAIndicator.run(close, window=ma_window_100)
    # print(sma_100.sma_indicator)

    # sma_200 = SMAIndicator.run(close, window=ma_window_200)
    # print(sma_200.sma_indicator)

    # print(ao.awesome_oscillator.shape)
    # print(stoch_rsi.stochrsi.shape)
    # print(willr.williams_r.shape)

    # trend = np.where((ao.awesome_oscillator < AO_Threshold) & (stoch_rsi.stochrsi > stochOverSold) & (willr.williams_r > willOverBought), -1, 0)
    """
    tmp1 = (ao.awesome_oscillator < AO_Threshold)
    print("Type:", type(tmp1))
    print("Shape:", tmp1.shape)
    tmp2 = (stoch_rsi.stochrsi > stochOverSold)
    print("Type:", type(tmp2))
    print("Shape:", tmp2.shape)
    tmp3 = (willr.williams_r > willOverBought)
    print("Type:", type(tmp3))
    print("Shape:", tmp3.shape)
    tmp = (tmp1 & tmp2)
    print("Type:", type(tmp))
    print("Shape:", tmp.shape)
    # tmp = tmp & tmp3
    """
    # trend = np.full(close.shape, np.nan)
    """
    trend = np.where((ao.awesome_oscillator > AO_Threshold)
                     & (ao_n1.awesome_oscillator > ao.awesome_oscillator)
                     & (willr.williams_r < willOverSold)
                     & (sma_100 > sma_200),
                     1,
                     trend)

    trend = np.where((ao.awesome_oscillator > AO_Threshold)
                     & (ao_n1.awesome_oscillator > ao.awesome_oscillator)
                     & (willr.williams_r < willOverSold)
                     & (sma_100 > sma_200),
                     1,
                     trend)

    trend = np.where((ao.awesome_oscillator > AO_Threshold)
                     & (ao_n1.awesome_oscillator > ao.awesome_oscillator)
                     & (willr.williams_r < willOverSold)
                     & (sma_100 > sma_200),
                     1,
                     trend)
    """

    # Define long entry and exit signals
    # long_entry = (ao.awesome_oscillator > AO_Threshold) \
    #              & (ao_n1.awesome_oscillator > ao.awesome_oscillator)\
    #              & (willr.williams_r < willOverSold)\
    #              & (sma_100 > sma_200)

    long_entry = np.where((ao.awesome_oscillator > AO_Threshold),
                          1,
                          0)
    long_entry = np.where((ao_n1.awesome_oscillator > ao.awesome_oscillator),
                          long_entry + 1,
                          long_entry)
    long_entry = np.where((willr.williams_r < willOverSold),
                          long_entry + 1,
                          long_entry)
    long_entry = np.where((sma_100 > sma_200),
                          long_entry + 1,
                          long_entry)
    long_entry = np.where((long_entry == 4),
                          True,
                          False)

    # long_exit = (ao.awesome_oscillator < AO_Threshold) \
    #             & (stoch_rsi.stochrsi > stochOverSold) \
    #             | (willr.williams_r > willOverBought)

    long_exit = np.where((ao.awesome_oscillator < AO_Threshold),
                         1,
                         0)
    long_exit = np.where((stoch_rsi.stochrsi > stochOverSold),
                         long_exit + 1,
                         long_exit)
    long_exit = np.where((willr.williams_r > willOverBought),
                         2,
                         long_exit)
    long_exit = np.where((long_exit == 2),
                         True,
                         False)

    trend = np.where(long_exit, -1, 0)
    trend = np.where(long_entry, 1, trend)

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

    interval = "1h"
    # interval = "1m"
    lst_pairs = ['BTC-USD', 'ETH-USD', 'XRP-USD', 'ADA-USD']
    lst_pairs = ['BTC-USD']
    lst_pairs = ['BTC-USD', 'ETH-USD']
    if interval == "1m":
        btc_price = vbt.YFData.download(lst_pairs,
                                        interval="1m",
                                        start=start_date_1m,
                                        end=end_date,
                                        missing_index='drop').get('Close')
        btc_high = vbt.YFData.download(lst_pairs,
                                       interval="1m",
                                       start=start_date_1h,
                                       end=end_date,
                                       missing_index='drop').get('High')
        btc_low = vbt.YFData.download(lst_pairs,
                                      interval="1m",
                                      start=start_date_1h,
                                      end=end_date,
                                      missing_index='drop').get('Low')
        print(btc_price)
        print(btc_high)
        print(btc_low)
    else:
        # btc_price = vbt.YFData.download(['BTC-USD', 'ETH-USD', 'XRP-USD', 'ADA-USD'],
        btc_price = vbt.YFData.download(lst_pairs,
                                        interval="1h",
                                        start=start_date_1h,
                                        end=end_date,
                                        missing_index='drop').get('Close')
        btc_high = vbt.YFData.download(lst_pairs,
                                       interval="1h",
                                       start=start_date_1h,
                                       end=end_date,
                                       missing_index='drop').get('High')
        btc_low = vbt.YFData.download(lst_pairs,
                                      interval="1h",
                                      start=start_date_1h,
                                      end=end_date,
                                      missing_index='drop').get('Low')
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
            input_names=['close', 'high', 'low'],
            param_names=["ao_window_1",
                         "ao_window_2",
                         "ma_window_100",
                         "ma_window_200",
                         "rsi_window",
                         "period",
                         "AO_Threshold",
                         "stochOverBought",
                         "stochOverSold",
                         "willOverSold",
                         "willOverBought"],
            output_names=['value']
        ).from_apply_func(
            custom_indicator,
            ao_window_1=6,
            ao_window_2=22,
            ma_window_100=100,
            ma_window_200=200,
            rsi_window=14,
            period=14,
            AO_Threshold=0,
            stochOverBought=0.8,
            stochOverSold=0.2,
            willOverSold=-80,
            willOverBought=-10,
            keep_pd=True
        )
        res = ind.run(btc_price, btc_high, btc_low,
                      ao_window_1=6,
                      ao_window_2=22,
                      ma_window_100=100,
                      ma_window_200=200,
                      rsi_window=14,
                      period=14,
                      AO_Threshold=0,
                      stochOverBought=0.8,
                      # stochOverBought=np.arange(0.6, 1.0, step=0.1, dtype=float),
                      #stochOverSold=0.2,
                      stochOverSold=np.arange(0.0, 0.4, step=0.1, dtype=float),
                      # willOverSold=-80,
                      willOverSold=np.arange(-60, -100, step=-5, dtype=int),
                      # willOverBought=-10,
                      willOverBought=np.arange(-5, -40, step=-5, dtype=int),
                      param_product = True
                      )

        # print(res.value.to_string())
        # print(res.value)

        entries = res.value == 1
        exits = res.value == -1

        pf = vbt.Portfolio.from_signals(btc_price, entries, exits, init_cash=10000)

        print(pf.stats())

        pf.total_profit().sort_values(ascending=False)


        # print(pf.total_return().to_string())
        # print(pf.total_profit().to_string())

        returns = pf.total_return()
        profits = pf.total_profit()
        print("return max: ", returns.max())
        print(returns.idxmax())
        print("profit max: ", profits.max())
        print(profits.idxmax())

        returns = pf.total_return()
        profits = pf.total_profit()

        heatmap = True
        volume = True
        if heatmap:
            returns = returns.groupby(level=["comb_bb_window", "comb_alpha", "symbol"]).mean()

            print(returns.to_string())
            print(profits.to_string())

            print(returns.max())
            print(returns.idxmax())
            print(profits.max())
            print(profits.idxmax())

            # "comb_rsi_window  comb_ma_window  symbol "

            fig = returns.vbt.heatmap(
                x_level="comb_bb_window",
                y_level="comb_alpha",
                slider_level="symbol"
            )

            fig.show()

            pf.plot(subplots=['orders', 'trades', 'trade_pnl',
                              'cum_returns', 'drawdowns',
                              'asset_value', 'assets',
                              'cash', 'cash_flow',
                              'value',
                              'underwater', 'gross_exposure']).show()


        elif volume:
            print(returns.to_string())
            print(profits.to_string())

            print("return max: ", returns.max())
            print(returns.idxmax())
            print("profit max: ", profits.max())
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

