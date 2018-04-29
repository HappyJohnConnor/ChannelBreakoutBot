# ChannelBreakoutBot
## 使い方
configファイルにBitmexのAPIキーを入力後，```python trade.py```で実行．時間足は1分から60分，またはそれ以降まで．
## 注意点
configファイル'isTest'は'true'の場合，Bitmex Testnetでトレードを行います．本番の環境で行いたい場合は'false'にしてください．またsrcフォルダの，orders.pyの
31行目```exhange.private_get_position()[1]```のインデックスは人によっては0の場合がございます．気を付けてください．本ソフトウェアで被った損害は一切保証しません．
## Lisence
MIT
