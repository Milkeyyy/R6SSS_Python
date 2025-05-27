import httpx

from ._logger import logger
from .types import Platform, Status


_API_URL = "https://api-r6sss.milkeyyy.com/v2/status"


def get_server_status(platforms: list[Platform] | None = None) -> list[Status] | None:
	"""指定されたプラットフォームのサーバーステータスの一覧を取得して返す"""

	if platforms is None:
		params = None
	else:
		params = {"platform": [p.value for p in platforms]}

	# サーバーステータスを取得
	result = httpx.get(
		_API_URL,
		params=params,
		timeout=7
	)
	result_json = result.json()
	if result.status_code != 200:
		logger.error("サーバーステータスの取得に失敗")
		if "detail" in result_json:
			logger.error("- %s %s", str(result.status_code), result.json()["detail"])
		return None

	status = result.json()["data"]

	status_list = []

	for _platform, _status in status.items():
		status_list.append(Status(Platform[_platform], _status))

	return status_list
