import json
import time
import log


class Orders:
    def __init__(self, exhange):
        f = open('config.json', 'r', encoding="utf-8")
        config = json.load(f)
        self.exhange = exhange
        self.product_code = config['productCode']
        self.logger = log.get_custom_logger(__name__)

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
                    pos_list = self.exhange.private_get_position()
                    self.logger.info(pos_list)
                    positions = ''
                    for pos in pos_list:
                        if self.product_code == 'BTC/USD':
                            if pos['symbol'] == 'XBTUSD':
                                positions = pos
                                break
                        elif pos['symbol'] == self.product_code:
                            positions = pos
                            break
                    if positions == '':
                        self.logger.error('symbolが見つかりませんでした．')
                    positions = self.exhange.private_get_position()[1]
                    if positions['openOrderSellQty'] != 0 or positions['openOrderBuyQty'] != 0:
                        self.exhange.cancel_order(closeid)
                        self.market(side, size)
                        self.logger.info('%s by maker', side)
                        break
                    else:
                        self.logger.info('%s by limit', side)
                        break

                time.sleep(5)
            except Exception as e:
                self.logger.exception('例外が発生しました。%r', e)
                error_times += 1
                if error_times <= 5:
                    continue
                else:
                    time.sleep(5)
                    continue
