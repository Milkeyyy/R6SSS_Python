import httpx

from ._logger import logger
from .types import MaintenanceSchedule, Platform, Status


_API_URL = "https://api-r6sss.milkeyyy.com/v2"


def get_server_status(platforms: list[Platform] | None = None) -> list[Status] | None:
	"""指定されたプラットフォームのサーバーステータスの一覧を取得して返す"""

	if platforms is None:
		params = None
	else:
		params = {"platform": [p.value for p in platforms]}

	# サーバーステータスを取得
	result = httpx.get(
		_API_URL + "/status",
		params=params,
		timeout=7
	)
	result_json = result.json()

	if result.status_code != 200:
		logger.error("サーバーステータスの取得に失敗")
		if "detail" in result_json:
			logger.error("- %s %s", str(result.status_code), result.json()["detail"])
		return None

	status = result_json.get("data")

	if not status:
		logger.error("サーバーステータスの取得に失敗")
		logger.error("- 'data' is None")
		return []

	status_list = []

	for _platform, _status in status.items():
		status_list.append(Status(Platform[_platform], _status))

	return status_list

def get_maintenance_schedule() -> MaintenanceSchedule | None:
	"""メンテナンスのスケジュール情報を取得して返す"""

	# メンテナンススケジュールを取得
	result = httpx.get(
		_API_URL + "/schedule/latest",
		timeout=7
	)
	result_json = result.json()

	if result.status_code != 200:
		logger.error("メンテナンススケジュールの取得に失敗")
		if "detail" in result_json:
			logger.error("- %s %s", str(result.status_code), result.json()["detail"])
		return None

	raw_schedule = result_json.get("data")
	schedule = MaintenanceSchedule()
	schedule._data = raw_schedule

	if not schedule:
		logger.error("メンテナンススケジュールの取得に失敗")
		logger.error("- 'data' is None")
		return None

	return schedule
