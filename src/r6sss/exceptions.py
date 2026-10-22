class R6SSSError(Exception):
	"""R6SSS ライブラリの基底例外"""


class R6SSSRequestError(R6SSSError):
	"""API への通信に失敗した場合の例外"""


class R6SSSResponseError(R6SSSError):
	"""API のレスポンスを解釈できなかった場合の例外"""


class R6SSSAPIError(R6SSSError):
	"""API がエラーを返した場合の例外"""

	def __init__(self, status_code: int, detail: str | None = None) -> None:
		self.status_code = status_code
		self.detail = detail
		message = f"API request failed with status code {status_code}"
		if detail:
			message = f"{message}: {detail}"
		super().__init__(message)
