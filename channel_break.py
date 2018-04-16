import time
import ccxt
import pytz
import inspect
from datetime import datetime
import traceback

bitmex = ccxt.bitmex({
    'apiKey': 'your key',
    'secret': 'secret',
})

periods = {
    '1m': ['1m', 1],
    '5m': ['5m', 5],
    '1h': ['1h', 60]
}


def main(number, period):

    pos = bitmex.private_get_position()[0]['currentQty']
    balance = get_balance()
    print('Position: ' + str(pos))
    print('Balance:' + str(balance))

    frist_order(number, period)

    print('came back to main\n')
    error_times = 0
    while True:
        try:
            pos = bitmex.private_get_position()[0]['currentQty']
            high_and_low = get_high_and_low(period)
            max_and_min = channel_break(number, period)
            print(time_is())
            print('high:' + str(high_and_low[0]))
            print('low:'+str(high_and_low[1]))
            print('max:' + str(max_and_min[0]))
            print('min:' + str(max_and_min[1]))

            if max_and_min[0] < high_and_low[0] and pos < 0:
                print("Buy!!")
                make_order('buy', round(get_balance()*3 / 4))

            elif max_and_min[1] > high_and_low[1] and pos > 0:
                print("Sell!!")
                make_order('sell', round(get_balance() * 3 / 4))
            print('\n')
            time.sleep(30)  # 一定時間(秒)待つ
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


def frist_order(number, period):
    error_times = 0
    while True:
        try:
            max_and_min = channel_break(number, period)
            high_and_low = get_high_and_low(period)
            print(time_is())
            print('high:' + str(high_and_low[0]))
            print('low:'+str(high_and_low[1]))
            print('max:' + str(max_and_min[0]))
            print('min:' + str(max_and_min[1]))
            if max_and_min[0] < high_and_low[0]:
                print("Buy!!")
                make_order('buy', round(get_balance()*3 / 2))
                break
            elif max_and_min[1] > high_and_low[1]:
                print("Sell!!")
                make_order('sell', round(get_balance() * 3 / 2))
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


def get_balance():
    try:
        balance = bitmex.fetch_balance(
        )['BTC']['free'] * bitmex.fetch_ticker('BTC/USD')['close']
    except IndexError as error:
        print('エラーが発生しました。')
        print("Place is " + inspect.currentframe().f_code.co_name)
        balance = 0
    return balance


def channel_break(number, period):
    timestamp = round(datetime.now().timestamp()*1000)
    past_time = timestamp - (number+1) * period[1] * 60000  # 1分は60000
    candles = bitmex.fetch_ohlcv(
        'BTC/USD', timeframe=period[0], since=past_time)
    min = candles[0][3]
    max = candles[0][2]
    for i in range(1, number-1):
        if candles[i][3] < min:
            min = candles[i][3]
        if candles[i][2] > max:
            max = candles[i][2]

    return max, min


def get_high_and_low(period):
    timestamp = round(datetime.now().timestamp()*1000)
    past_time = timestamp - period[1] * 60000  # 1分は60000
    candles = bitmex.fetch_ohlcv(
        'BTC/USD', timeframe=period[0], since=past_time)

    return candles[0][2], candles[0][3]


def make_order(side, size):
    closeid = ''
    last = bitmex.fetch_ticker('BTC/USD')['last']
    while True:
        try:
            if closeid == '':
                if side == 'buy':
                    order = limit(side, last+0.5, size)
                elif side == 'sell':
                    order = limit(side, last-0.5, size)
                closeid = order['id']
            else:
                # 15秒で確定できなかったら、成行
                positions = bitmex.private_get_position()[0]
                if positions['openOrderSellQty'] != 0 or positions['openOrderBuyQty'] != 0:
                    bitmex.cancel_order(closeid)
                    market(side, size)
                    print(side + ' by market')
                    break
                else:
                    print(side+' by limit')
                    break

            error_times = 0
            time.sleep(10)
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


def market(side, size):
    return bitmex.create_order('BTC/USD',
                               type='market', side=side, amount=size)


def limit(side, price, size):
    return bitmex.create_order('BTC/USD', type='limit', side=side, price=price, amount=size)


def time_is():
    now = datetime.now()
    tokyo_timezone = pytz.timezone('Asia/Tokyo')
    tokyo_datetime = tokyo_timezone.localize(now)

    return tokyo_datetime.strftime('%Y/%m/%d %H:%M:%S')


if __name__ == '__main__':
    main(3, periods['5m'])
    # period:1h, 1m,5m,
    # 最初の引数は期間です．
