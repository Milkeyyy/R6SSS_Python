import datetime
from enum import Enum
import json

from ._logger import logger


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

class MaintenanceSchedule():
	"""メンテナンススケジュール"""

	_data: dict

	def __init__(self) -> None:
		self._data = {
			"Title": "",
			"Detail": "",
			"Downtime": 0,
			"Timestamp": 0,
			"Date": "1970-01-01T00:00:00Z",
			"PatchNotes": "",
			"Platforms": []
		}

	@classmethod
	def create(cls,
		title: str,
		detail: str,
		downtime: int,
		date: datetime.datetime,
		patchnotes: str,
		platforms: list[Platform]
	):
		i = MaintenanceSchedule()
		i._data["Title"] = title
		i._data["Detail"] = detail
		i._data["Downtime"] = downtime
		i._data["Timestamp"] = date.timestamp()
		i._data["Date"] = date.isoformat()
		i._data["PatchNotes"] = patchnotes
		if set(platforms).issuperset(set(list(Platform))):
			i._data["Platforms"] = [{"Name": "All"}]
		else:
			i._data["Platforms"] = [{"Name": pf.name} for pf in platforms]
		return i

	def _get_data(self, key: str):
		return self._data[key]

	@property
	def title(self) -> str:
		"""メンテナンスのタイトル"""
		return self._get_data("Title")

	@property
	def detail(self) -> str:
		"""メンテナンスの詳細情報"""
		return self._get_data("Detail")

	@property
	def downtime(self) -> int:
		"""メンテナンスのダウンタイム"""
		return self._get_data("Downtime")

	@property
	def date(self) -> datetime.datetime:
		"""メンテナンスの予定日時"""
		return datetime.datetime.fromtimestamp(self._get_data("Timestamp"))

	@property
	def patchnotes(self) -> str:
		"""パッチノートのURL"""
		return self._get_data("PatchNotes")

	@property
	def platforms(self) -> list[Platform]:
		"""メンテナンスの対象プラットフォーム"""
		result = []
		platform_list: list[dict[str, str]] | None = self._get_data("Platforms")
		if platform_list:
			for pf in platform_list:
				# プラットフォーム名が All の場合は全プラットフォームをリストへ入れる
				if pf["Name"] == "All":
					result = list(Platform)
				# 名前をもとに生成した Enum をリストへ入れる
				else:
					result.append(Platform[pf["Name"]])
		return result

	def db_json(self) -> str:
		raw = self._data.copy()

		# 日時
		# None の場合は今の日時にする
		if not self.date:
			logger.warning("Schedule Date is None. Set to the current date.")
			raw["Timestamp"] = datetime.datetime.now().timestamp()
			raw["Date"] = datetime.datetime.now().isoformat()
		else:
			raw["Timestamp"] = self.date.timestamp()
			raw["Date"] = self.date.isoformat()

		# プラットフォーム一覧
		# 全プラットフォームの場合は専用の値
		if set(self.platforms).issuperset(set(list(Platform))):
			raw["Platforms"] = [{"Name": "All"}]
		else:
			raw["Platforms"] = [{"Name": pf.name} for pf in self.platforms]

		# その他項目
		raw["Result"] = True

		js = json.dumps(raw)
		return js

	def db_dict(self) -> dict:
		return json.loads(self.db_json())
