import datetime
from enum import Enum

import httpx

from r6sss._logger import logger


_API_URL = "https://api-r6sss.milkeyyy.com/v2/status"

class Platform(Enum):
	"""プラットフォーム"""

	PC = "PC"
	PS4 = "PS4"
	PS5 = "PS5"
	XB1 = "XBOXONE"
	XBSX = "XBOX SERIES X"

class Status():
	"""サーバーステータス"""

	_platform: str
	_data: dict

	def __init__(self, platform, data) -> None:
		self._platform = platform
		self._data = data

	def _get_data(self, key: str):
		if key not in self._data["Status"]:
			return "Unknown"
		return self._data["Status"][key]

	def _get_feat_data(self, key: str):
		if key not in self._data["Status"]["Features"]:
			return "Unknown"
		return self._data["Status"]["Features"][key]

	@property
	def data(self) -> dict:
		"""生データ"""
		return self._data.copy()

	@property
	def platform(self) -> str:
		"""プラットフォーム"""
		return self._platform

	@property
	def updated_at(self) -> datetime.datetime:
		"""最終更新日時"""
		_d = self._data["UpdatedAt"]
		return datetime.datetime.fromtimestamp(_d)

	@property
	def connectivity(self) -> str:
		"""接続状況"""
		return self._get_data("Connectivity")

	@property
	def authentication(self) -> str:
		"""認証の稼働状況"""
		return self._get_feat_data("Authentication")

	@property
	def matchmaking(self) -> str:
		"""マッチメイキングの稼働状況"""
		return self._get_feat_data("Matchmaking")

	@property
	def purchase(self) -> str:
		"""ストアの稼働状況"""
		return self._get_feat_data("Purchase")

	@property
	def maintenance(self) -> bool:
		"""メンテナンス中かどうか"""
		_d = self._get_data("Maintenance")
		if _d == "Unknown":
			return False
		return _d

	@property
	def text(self) -> str:
		"""すべてのステータスを文字列にして結合したもの"""

		texts = [
			self.connectivity,
			self.authentication,
			self.purchase,
			self.matchmaking,
			str(self.maintenance)
		]

		return ";".join(texts)

def get_server_status(platform: Platform) -> Status | None:
	"""指定されたプラットフォームのサーバーステータスを取得して返す"""

	if platform is None:
		params = None
	else:
		params = {"platform": platform.value}

	# サーバーステータスを取得
	result = httpx.get(
		_API_URL,
		params=params
	)
	result_json = result.json()
	if result.status_code != 200:
		logger.error("サーバーステータスの取得に失敗")
		if "detail" in result_json:
			logger.error("- %s %s", str(result.status_code), result.json()["detail"])
		return None

	status = result.json()["data"]

	return Status(platform.value, status[platform.value])

def get_server_status_list(platforms: list[Platform] | None = None) -> list[Status] | None:
	"""指定されたプラットフォームのサーバーステータスの一覧を取得して返す"""

	if platforms is None:
		params = None
	else:
		params = {"platform": [p.value for p in platforms]}

	# サーバーステータスを取得
	result = httpx.get(
		_API_URL,
		params=params
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
		status_list.append(Status(_platform, _status))

	return status_list
