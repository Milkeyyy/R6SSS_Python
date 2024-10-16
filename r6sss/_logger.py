import logging


logger = logging.getLogger("r6sss")
logger.setLevel(logging.DEBUG)

_stream_handler = logging.StreamHandler()
_stream_formatter = logging.Formatter(fmt="[%(asctime)s.%(msecs)03d] %(levelname)s [%(thread)d] %(message)s")
_stream_handler.setFormatter(_stream_formatter)

logger.addHandler(_stream_handler)
