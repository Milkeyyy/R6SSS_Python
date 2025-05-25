import datetime
from enum import Enum


class Platform(Enum):
	"""プラットフォーム"""

	PC = "PC"
	PS4 = "PS4"
	PS5 = "PS5"
	XB1 = "XB1"
	XBSX = "XBSX/S"

class Status():
	"""サーバーステータス"""

	_platform: Platform
	_data: dict

	def __init__(self, platform: Platform, data: dict) -> None:
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
	def platform(self) -> Platform:
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
	def features(self) -> dict[str, str]:
		"""稼働状況の辞書"""

		table = {
			"authentication": self.authentication,
			"matchmaking": self.matchmaking,
			"purchase": self.purchase
		}

		return table

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
