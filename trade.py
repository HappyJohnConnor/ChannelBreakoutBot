import time
import ccxt
import pytz
import inspect
import orders
import json
import traceback
from datetime import datetime


bitmex = ccxt.bitmex({
    'apiKey': 'your key',
    'secret': 'secret',
})

f = open('config.json', 'r', encoding="utf-8")
config = json.load(f)
product_code = config['productCode']
candle_term = int(config['candleTerm'])
period = config['period']
if config['isTest']:
    apiKey = config['test']['key']
    secret = config['test']['secret']
    bitmex = ccxt.bitmex({
        'apiKey': apiKey,
        'secret': secret,
    })
    bitmex.urls['api'] = bitmex.urls['test']
else:
    apiKey = config['real']['key']
    secret = config['real']['secret']
    bitmex = ccxt.bitmex({
        'apiKey': apiKey,
        'secret': secret,
    })
lot = config['lot']
orders = orders.Orders(bitmex)


def main():

    balance = get_balance()
    print('Balance:' + str(balance))

    pos = frist_order(period, candle_term)
    print('came back to main\n')
    while True:
        judge = channel_break(period, candle_term)

        if judge == 1 and pos == -1:
            print("Buy!!")
            orders.make_order('buy', lot)
            pos = 1
        elif judge == 0 and pos == 1:
            print("Sell!!")
            orders.make_order('sell', lot)
            pos = -1
        print('\n')
        time.sleep(30)  # 一定時間(秒)待つ


def frist_order(period, candle_term):
    pos = 1
    while True:
        judge = channel_break(period, candle_term)
        if judge == 1:
            print("Buy!!")
            orders.make_order('buy', lot / 2)
            pos = 1
            break
        elif judge == 0:
            print("Sell!!")
            orders.make_order('sell', lot / 2)
            pos = -1
            break
        print('\n')
        time.sleep(30)
    return pos


def get_balance():
    try:
        balance = bitmex.fetch_balance(
        )['BTC']['free'] * bitmex.fetch_ticker('BTC/USD')['close']
    except IndexError as error:
        print('エラーが発生しました。')
        print("Place is " + inspect.currentframe().f_code.co_name)
        balance = 0
    return balance


def channel_break(period, candle_term):
    judge = 0
    error_times = 0
    while True:
        try:
            print(time_is())
            timestamp = round(datetime.now().timestamp()*1000)
            past_time = timestamp - (period+1) * \
                candle_term * 60000  # 1分は60000
            multi_candles = fetch_original_ohlcv(
                product_code, candle_term, past_time)

            highest = max([multi_candles[i][2] for i in range(period - 1)])
            lowest = min([multi_candles[i][3] for i in range(period - 1)])
            print('highest:' + str(highest))
            print('lowest:' + str(lowest))

            before_1candle = timestamp - candle_term * 60000  # 1分は60000
            candle = fetch_original_ohlcv(
                product_code, candle_term, before_1candle)
            high = candle[0][2]
            low = candle[0][3]

            print('high:' + str(high))
            print('low:'+str(low))

            if highest < high:
                judge = 1
                break
            if lowest > low:
                judge = 0
                break
            print('\n')
            time.sleep(30)

        except:
            print('エラーが発生しました。')
            print("Place is " + inspect.currentframe().f_code.co_name)
            traceback.print_exc()
            error_times += 1
            if error_times <= 10:
                continue
            else:
                time.sleep(10)
                continue
    return judge


def fetch_original_ohlcv(product_code, num, since):
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

    candles = bitmex.fetch_ohlcv(
        product_code, timeframe=candle_term, since=since)

    for candle in candles:
        if candle[0] % (1000 * 60 * num) == 0:
            candle_list.append(candle)

    return candle_list


def time_is():
    now = datetime.now()
    tokyo_timezone = pytz.timezone('Asia/Tokyo')
    tokyo_datetime = tokyo_timezone.localize(now)

    return tokyo_datetime.strftime('%Y/%m/%d %H:%M:%S')


if __name__ == '__main__':
    main()
    # candle_term:1h, 1m,5m,
