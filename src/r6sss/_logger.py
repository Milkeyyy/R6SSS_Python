import logging

# ライブラリ利用側がログ設定を行えるよう、ハンドラは追加しない
logger = logging.getLogger("r6sss")
logger.addHandler(logging.NullHandler())
