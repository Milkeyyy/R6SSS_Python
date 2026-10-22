import httpx

from .exceptions import R6SSSAPIError, R6SSSRequestError, R6SSSResponseError
from .types import MaintenanceSchedule, Platform, Status

_API_URL = "https://api-r6sss.milkeyyy.com/v2"
_HTTP_OK = 200
_HTTP_NOT_FOUND = 404


def _request(
	path: str,
	params: dict[str, list[str] | str] | None,
	client: httpx.Client | None,
	timeout: float,
	*,
	allow_not_found: bool = False,
) -> dict | list | None:
	"""GET リクエストを送り、レスポンスの data を返す"""
	requester = client or httpx

	try:
		response = requester.get(_API_URL + path, params=params, timeout=timeout)
	except httpx.HTTPError as exc:
		raise R6SSSRequestError(str(exc)) from exc

	try:
		payload = response.json()
	except ValueError as exc:
		raise R6SSSResponseError("API returned invalid JSON") from exc

	if response.status_code != _HTTP_OK:
		# スケジュール未登録時は 404 と data キーが返る
		if allow_not_found and response.status_code == _HTTP_NOT_FOUND and isinstance(payload, dict) and "data" in payload:
			return None

		detail = payload.get("detail") if isinstance(payload, dict) else None
		raise R6SSSAPIError(response.status_code, detail)

	if not isinstance(payload, dict) or "data" not in payload:
		raise R6SSSResponseError("response does not contain 'data'")

	return payload["data"]


def get_server_status(
	platforms: list[Platform] | None = None,
	*,
	client: httpx.Client | None = None,
) -> list[Status]:
	"""指定されたプラットフォームのサーバーステータスの一覧を取得して返す

	platforms を省略した場合は全プラットフォームを取得する。
	"""
	if platforms is not None and not platforms:
		return []

	params = None if platforms is None else {"platform": [p.name for p in platforms]}
	data = _request("/status", params, client, timeout=7.0)

	if not data:
		return []
	if not isinstance(data, dict):
		raise R6SSSResponseError("'data' is not an object")

	try:
		return [Status(Platform[name], value) for name, value in data.items()]
	except KeyError as exc:
		raise R6SSSResponseError(f"unknown platform: {exc.args[0]}") from exc


def get_maintenance_schedule(
	language: str | None = None,
	*,
	client: httpx.Client | None = None,
) -> MaintenanceSchedule | None:
	"""直近のメンテナンスのスケジュール情報を取得して返す

	スケジュールが登録されていない場合は None を返す。
	"""
	params = {"lang": language} if language else {}
	data = _request("/schedule/recent", params, client, timeout=10.0, allow_not_found=True)

	if not data:
		return None
	if not isinstance(data, dict):
		raise R6SSSResponseError("'data' is not an object")

	return MaintenanceSchedule(data)


def get_maintenance_schedule_list(
	language: str | None = None,
	*,
	client: httpx.Client | None = None,
) -> list[MaintenanceSchedule]:
	"""全てのメンテナンスのスケジュール情報を取得して返す"""
	params = {"lang": language} if language else {}
	data = _request("/schedule/list", params, client, timeout=10.0, allow_not_found=True)

	if not data:
		return []
	if not isinstance(data, list):
		raise R6SSSResponseError("'data' is not an array")

	return [MaintenanceSchedule(d) for d in data]
