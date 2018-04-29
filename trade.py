import json
from src import logic
from logging import (
    getLogger,
    Formatter,
    FileHandler,
    StreamHandler,
    DEBUG,
    ERROR,
)

if __name__ == '__main__':
    logger = getLogger(__name__)

    # 出力フォーマット
    formatter = Formatter(
        fmt='[%(levelname)s] %(asctime)s : %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # ログ用ハンドラー: コンソール出力用
    log_stream_handler = StreamHandler()
    log_stream_handler.setFormatter(formatter)
    log_stream_handler.setLevel(DEBUG)

    # ログ用ハンドラー: ファイル出力用
    log_file_handler = FileHandler(filename="crawler.log")
    log_file_handler.setFormatter(formatter)
    log_file_handler.setLevel(DEBUG)

    # ロガーにハンドラーとレベルをセット
    logger.setLevel(DEBUG)
    logger.addHandler(log_stream_handler)
    logger.addHandler(log_file_handler)

    _logic = logic.ChannelBreakout(logger)
    # 稼働開始
    _logic.loop()
