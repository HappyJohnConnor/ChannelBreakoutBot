import ccxt
import json
import time
from datetime import datetime
from src.orders import Orders
from src.candle import Candle
import log


class ChannelBreakout:

    def __init__(self):
        f = open('config.json', 'r', encoding="utf-8")
        config = json.load(f)
        self.logger = log.get_custom_logger(__name__)
        self.product_code = config['productCode']
        self.count = config['count']
        self.period = config['period']
        self.lot = config['lot']
        code = 'XBTUSD' if self.product_code == 'BTC/USD' self.product_code
        self.candle = Candle(code)
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
        self.order = Orders(self.bitmex)

    def loop(self):
        pos = self.frist_order(self.period, self.candle_term)
        self.logger.info('Came back to loop!!')
        while True:
            judge = self.channel_break(self.period, self.candle_term)

            if judge == 1 and pos == -1:
                self.logger.info('Buy!!')
                self.order.make_order('buy', lot*2)
                pos = 1
            elif judge == -1 and pos == 1:
                self.logger.info('Sell!!')
                self.order.make_order('sell', lot*2)
                pos = -1
            time.sleep(30)  # 一定時間(秒)待つ

    def frist_order(self, period, candle_term):
        pos = 1
        while True:
            judge = self.channel_break(period, candle_term)
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

    def channel_break(self, period, count):
        judge = 0
        error_times = 0
        while True:
            try:
                candles = self.candle.fetch_ohlcv_df(
                    period=period, count=count)
                highest = max([candles[i][2] for i in range(period - 1)])
                lowest = min([candles[i][3] for i in range(period - 1)])
                self.logger.info('highest:{}'.format(highest))
                self.logger.info('lowest:{}'.format(lowest))

                candle = self.candle.fetch_ohlcv_df(
                    period=period, count=1)
                high = candle['high'][-1]
                low = candle['low'][-1]
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
