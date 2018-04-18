import json
import traceback
import inspect
import time


class Orders:
    def __init__(self, exhange):
        f = open('config.json', 'r', encoding="utf-8")
        config = json.load(f)
        self.exhange = exhange
        self.product_code = config['productCode']

    def limit(self, side, price, size):
        return self.exhange.create_order(self.product_code, type='limit', side=side, price=price, amount=size)

    def market(self, side, size):
        return self.exhange.create_order(self.product_code,
                                         type='market', side=side, amount=size)

    def make_order(self, side, size):
        closeid = ''
        error_times = 0
        last = self.exhange.fetch_ticker(self.product_code)['last']
        while True:
            try:
                if closeid == '':
                    order = self.limit(side, last, size)
                    closeid = order['id']
                else:
                    # 15秒で確定できなかったら、成行
                    positions = self.exhange.private_get_position()[1]
                    if positions['openOrderSellQty'] != 0 or positions['openOrderBuyQty'] != 0:
                        self.exhange.cancel_order(closeid)
                        self.market(side, size)
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
