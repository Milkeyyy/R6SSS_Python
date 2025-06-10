from enum import Enum, auto

from ._logger import logger
from .types import Platform, Status


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

def compare_server_status(previous: list[Status], current: list[Status]) -> list[ComparisonResult]:
	"""2つのサーバーステータスを比較して結果を返す"""

	impacted_feature_max_count: int = 3 # 影響を受ける機能の最大数 影響を受ける機能の数がこの最大数に達した場合はすべて影響を受けているとみなす

	# ステータスの変化ごとの辞書を作成 キーは現在のステータスを文字列化したものと以前のステータスを文字列化したものを結合したもの
	status_list: dict[str, list] = {}
	for status in current:
		# ステータス比較用テキスト辞書へ追加
		_prev_status = [_ for _ in previous if _.platform == status.platform][0]
		_status_text = _prev_status.text + ";" + status.text # 現在のステータスを文字列化したものと以前のステータスを文字列化したもの (以前;現在)
		if _status_text not in status_list:
			status_list[_status_text] = [[_prev_status, status], [status.platform]]
		else:
			status_list[_status_text][1].append(status.platform)

	impacted_features: list[str] # 影響を受ける機能の一覧

	results: list[ComparisonResult] = []

	for status_text, _status_data in status_list.items():
		# ステータス情報
		status = _status_data[0][1]
		pre_status = _status_data[0][0]
		# プラットフォーム一覧
		_platforms = _status_data[1]
		platform_list = []
		for _pf in _platforms:
			platform_list.append(_pf)

		# 影響を受ける機能一覧
		#impacted_feature_max_count = 3 # 影響を受ける機能一覧の最大数
		impacted_features = [] # 影響を受ける機能一覧を初期化
		changed_features = []
		if status.authentication == "Outage":
			impacted_features.append("Authentication")

		if status.matchmaking == "Outage":
			impacted_features.append("Matchmaking")

		if status.purchase == "Outage":
			impacted_features.append("Purchase")

		impacted_features_text = "・" + "\n・".join(impacted_features)

		# 以前の影響を受ける機能一覧
		previous_impacted_features = []
		if pre_status.authentication == "Outage":
			previous_impacted_features.append("Authentication")

		if pre_status.matchmaking == "Outage":
			previous_impacted_features.append("Matchmaking")

		if pre_status.purchase == "Outage":
			previous_impacted_features.append("Purchase")

		previous_impacted_features_text = "・" + "\n・".join(previous_impacted_features)


		# 問題が解消した機能一覧
		resolved_impacted_features = []
		for _feat in previous_impacted_features:
			if _feat not in impacted_features:
				resolved_impacted_features.append(_feat)
		# 新たに問題が発生した機能一覧
		new_impacted_features = []
		for _feat in impacted_features:
			if _feat not in previous_impacted_features:
				new_impacted_features.append(_feat)
		# 変更があった機能一覧
		changed_features = list(set(resolved_impacted_features + new_impacted_features))

		# logger.debug("====================")
		# logger.debug("  Status Text: %s", status_text)
		# logger.debug("    Platforms: %s", _platforms)
		# logger.debug("Prev Imp Feat: %s", previous_impacted_features)
		# logger.debug("Curr Imp Feat: %s", impacted_features)
		# logger.debug("Rslv Imp Feat: %s", resolved_impacted_features)
		# logger.debug(" New Imp Feat: %s", new_impacted_features)
		# logger.debug("====================")

		### ステータスの変化によってツイートの内容を変える
		###### メンテナンス開始
		if status.maintenance:
			# 前のステータスもメンテナンス中の場合は変化なしなのでループを続ける
			if pre_status.maintenance:
				continue
			results.append(ComparisonResult(
				detail=ComparisonDetail.START_MAINTENANCE,
				platforms=_platforms,
				impacted_features=new_impacted_features,
				resolved_impected_features=resolved_impacted_features
			))
		else:
			###### メンテナンス終了
			if pre_status.maintenance:
				results.append(ComparisonResult(
					detail=ComparisonDetail.END_MAINTENANCE,
					platforms=_platforms,
					impacted_features=new_impacted_features,
					resolved_impected_features=resolved_impacted_features
				))
			##### すべての機能が正常に稼働中
			if len(impacted_features) == 0:
				###### すべて/一部の機能で問題が発生中 -> すべての機能の問題が解消
				if len(previous_impacted_features) >= 1: # 以前の影響を受ける機能が1以上
					results.append(ComparisonResult(
						detail=ComparisonDetail.ALL_FEATURES_OUTAGE_RESOLVED,
						platforms=_platforms,
						impacted_features=new_impacted_features,
						resolved_impected_features=resolved_impacted_features
					))
			###### すべての機能で問題が発生中 ->
			elif len(impacted_features) >= impacted_feature_max_count: # 影響を受ける機能が最大数以上
				# 現在の影響を受ける機能の数が以前よりも多いか、以前の影響を受ける機能が0の場合
				# -> すべての機能で問題が発生中
				if len(previous_impacted_features) == 0 or len(previous_impacted_features) < len(impacted_features):
					results.append(ComparisonResult(
						detail=ComparisonDetail.ALL_FEATURES_OUTAGE,
						platforms=_platforms,
						impacted_features=new_impacted_features,
						resolved_impected_features=resolved_impacted_features
					))
			###### 一部の機能で問題が発生中 ->
			elif all((
				len(impacted_features) >= 1, # 影響を受ける機能が1以上
				len(impacted_features) < impacted_feature_max_count, # 影響を受ける機能が3未満
				sorted(impacted_features) != sorted(previous_impacted_features) # 現在と以前の影響を受ける機能が異なる
			)):
				# 一部の機能で問題が発生中
				# 新規
				if len(previous_impacted_features) == 0: # 以前の影響を受ける機能が0
					results.append(ComparisonResult(
						detail=ComparisonDetail.SOME_FEATURES_OUTAGE,
						platforms=_platforms,
						impacted_features=new_impacted_features,
						resolved_impected_features=resolved_impacted_features
					))
				# 影響を受ける機能が変わった
				elif sorted(impacted_features) != sorted(previous_impacted_features): # 現在と以前の影響を受ける機能が異なる
					results.append(ComparisonResult(
						detail=ComparisonDetail.SOME_FEATURES_OUTAGE_RESOLVED,
						platforms=_platforms,
						impacted_features=new_impacted_features,
						resolved_impected_features=resolved_impacted_features
					))
			# else:
			# 	results.append(ComparisonResult(
			# 		detail=ComparisonDetail.NO_CHANGE,
			# 		platforms=_platforms,
			# 		impacted_features=[],
			# 		resolved_impected_features=[]
			# 	))

	return results
