import ccxt
import json
import time
from datetime import datetime
from . import orders


class ChannelBreakout:

    def __init__(self, logger):
        f = open('config.json', 'r', encoding="utf-8")
        config = json.load(f)

        self.logger = logger
        self.product_code = config['productCode']
        self.candle_term = config['candleTerm']
        self.period = config['period']
        self.lot = config['lot']
        if config['isTest']:
            apiKey = config['test']['key']
            secret = config['test']['secret']
            self.bitmex = ccxt.bitmex({
                'apiKey': apiKey,
                'secret': secret,
            })
            self.bitmex.urls['api'] = self.bitmex.urls['test']
        else:
            apiKey = config['real']['key']
            secret = config['real']['secret']
            self.bitmex = ccxt.bitmex({
                'apiKey': apiKey,
                'secret': secret,
            })
        self.order = orders.Orders(self.bitmex, self.logger)

    def loop(self):
        pos = self.frist_order(
            self.product_code, self.period, self.candle_term)
        self.logger.info('Came back to loop!!')
        while True:
            judge = self.channel_break(
                self.product_code, self.period, self.candle_term)

            if judge == 1 and pos == -1:
                self.logger.info('Buy!!')
                self.order.make_order('buy', lot*2)
                pos = 1
            elif judge == -1 and pos == 1:
                self.logger.info('Sell!!')
                self.order.make_order('sell', lot*2)
                pos = -1
            time.sleep(30)  # 一定時間(秒)待つ

    def frist_order(self, product_code, period, candle_term):
        pos = 1
        while True:
            judge = self.channel_break(product_code, period, candle_term)
            if judge == 1:
                self.logger.info('Buy!!')
                self.order.make_order('buy', lot)
                pos = 1
                break
            elif judge == -1:
                self.logger.info('Sell!!')
                self.order.make_order('sell', lot)
                pos = -1
                break
            time.sleep(30)
        return pos

    def get_balance(self):
        try:
            balance = self.bitmex.fetch_balance(
            )['BTC']['free'] * self.bitmex.fetch_ticker('BTC/USD')['close']
        except Exception as e:
            self.logger.exception('例外が発生しました。%r', e)
            balance = 0
        return balance

    def channel_break(self, product_code, period, candle_term):
        judge = 0
        error_times = 0
        while True:
            try:
                timestamp = round(datetime.now().timestamp()*1000)
                past_time = timestamp - (period+1) * \
                    candle_term * 60000  # 1分は60000
                multi_candles = self.fetch_original_ohlcv(
                    product_code, candle_term, past_time)

                highest = max([multi_candles[i][2] for i in range(period - 1)])
                lowest = min([multi_candles[i][3] for i in range(period - 1)])
                self.logger.info('highest:{}'.format(highest))
                self.logger.info('lowest:{}'.format(lowest))

                before_1candle = timestamp - candle_term * 60000  # 1分は60000
                candle = self.fetch_original_ohlcv(
                    product_code, candle_term, before_1candle)
                high = candle[-1][2]
                low = candle[-1][3]
                self.logger.info('high:{}'.format(high))
                self.logger.info('low:{}\n'.format(low))

                if highest < high:
                    judge = 1
                    break
                if lowest > low:
                    judge = -1
                    break
                time.sleep(30)

            except Exception as e:
                self.logger.exception('例外が発生しました。%r', e)
                error_times += 1
                if error_times <= 5:
                    continue
                else:
                    time.sleep(10)
                    continue
        return judge

    def fetch_original_ohlcv(self, product_code, num, since):
        candle_list = []
        if num == 1:
            candle_term = '1m'
        elif 1 < num and num < 5:
            candle_term = '1m'
        elif num == 5:
            candle_term = '5m'
        elif 5 < num and num < 60:
            candle_term = '5m'
        elif num == 60:
            candle_term = '1h'
        elif 60 < num and num % 60 == 0:
            candle_term = '1h'

        candles = self.bitmex.fetch_ohlcv(
            product_code, timeframe=candle_term, since=since)

        for candle in candles:
            if candle[0] % (1000 * 60 * num) == 0:
                candle_list.append(candle)

        return candle_list
