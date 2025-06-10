import datetime
from enum import Enum, auto
import json

from ._logger import logger


class Platform(Enum):
	"""プラットフォーム"""

	PC = "PC"
	PS4 = "PS4"
	PS5 = "PS5"
	XB1 = "XB1"
	XBSX = "XBSX/S"

class Status:
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

class MaintenanceSchedule:
	"""メンテナンススケジュール"""

	_data: dict

	def __init__(self, data: dict | None = None) -> None:
		if data:
			self._data = data
		else:
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
	def convert_to_dict_platform_list(cls, platforms: list[Platform]) -> list[dict[str, str]]:
		"""プラットフォーム列挙値のリストをAPIから返ってくるものと同じ辞書形式へ変換する"""

		result = []

		if set(platforms).issuperset(set(list(Platform))):
			# 全プラットフォーム
			result = [{"Name": "All"}]
		else:
			result = [{"Name": pf.name} for pf in platforms]

		return result

	@classmethod
	def convert_to_enum_platform_list(cls, platforms: list[dict[str, str]]) -> list[Platform]:
		"""プラットフォームの辞書を列挙値のリストへ変換する"""

		result = []

		for pf in platforms:
			# プラットフォーム名が All の場合は全プラットフォームをリストへ入れる
			if pf["Name"] == "All":
				result = list(Platform)
			# 名前をもとに生成した Enum をリストへ入れる
			else:
				result.append(Platform[pf["Name"]])

		return result

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
		i._data["Platforms"] = cls.convert_to_dict_platform_list(platforms)
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
			result = self.convert_to_enum_platform_list(platform_list)
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
		raw["Platforms"] = self.convert_to_dict_platform_list(self.platforms)

		# その他項目
		raw["Result"] = True

		js = json.dumps(raw)
		return js

	def db_dict(self) -> dict:
		return json.loads(self.db_json())

class ComparisonDetail(Enum):
	"""サーバーステータスの比較結果を表す列挙値"""

	UNKNOWN = -1
	"""不明"""

	NO_CHANGE = auto()
	"""変化なし"""

	ALL_FEATURES_OPERATIONAL = auto()
	"""すべての機能が正常に稼働中"""

	ALL_FEATURES_OUTAGE = auto()
	"""すべての機能で問題が発生中"""

	ALL_FEATURES_OUTAGE_RESOLVED = auto()
	"""すべての機能の問題が解消"""

	SOME_FEATURES_OUTAGE = auto()
	"""一部の機能で問題が発生中"""

	SOME_FEATURES_OUTAGE_RESOLVED = auto()
	"""一部の機能の問題が解消 (問題が発生している機能が変化した)"""

	START_MAINTENANCE = auto()
	"""メンテナンス開始"""

	END_MAINTENANCE = auto()
	"""メンテナンス終了"""

	SCHEDULED_MAINTENANCE_START = auto()
	"""計画メンテナンス開始"""

	SCHEDULED_MAINTENANCE_END = auto()
	"""計画メンテナンス終了"""

class ComparisonResult():
	"""ステータス情報の比較結果"""

	_changed_features: list[str]
	_detail: ComparisonDetail
	_platforms: list[Platform]
	_impacted_features: list[str]
	_resolved_impacted_features: list[str]

	def __init__(
		self,
		detail: ComparisonDetail,
		platforms: list[Platform],
		impacted_features: list[str],
		resolved_impected_features: list[str]
	) -> None:
		self._detail = detail
		self._platforms = platforms
		self._impacted_features = impacted_features
		self._resolved_impacted_features = resolved_impected_features

	@property
	def detail(self) -> ComparisonDetail:
		"""ステータスの比較結果
		
		メンテナンス開始 や 一部の機能で問題が発生中 など"""
		return self._detail

	@property
	def platforms(self) -> list[Platform]:
		"""対象となるプラットフォームのリスト"""
		return self._platforms

	@property
	def impacted_features(self) -> list[str]:
		"""影響を受ける機能のリスト"""
		return self._impacted_features

	@property
	def resolved_impacted_features(self) -> list[str]:
		"""影響を受けていた機能(復旧した機能)のリスト"""
		return self._resolved_impacted_features
