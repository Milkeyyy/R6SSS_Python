# R6SSS Web API Python Wrapper Library

[R6SSS Web API](https://api-r6sss.milkeyyy.com/v2) の Python クライアントです。
サーバーステータスとメンテナンススケジュールの取得、ステータスの比較を行えます。

## 要件

- Python 3.11 以上
- `httpx`
- `datetimerange`

## インストール

```sh
uv add "r6sss @ git+https://github.com/Milkeyyy/R6SSS_Python.git"
```

```sh
pip install "r6sss @ git+https://github.com/Milkeyyy/R6SSS_Python.git"
```

## 使い方

```python
import r6sss

# 全プラットフォームのステータスを取得
statuses = r6sss.get_server_status()

for status in statuses:
	print(status.platform.name, status.connectivity, status.maintenance)

# プラットフォームを指定して取得
pc_status = r6sss.get_server_status([r6sss.Platform.PC])

# 直近のメンテナンススケジュールを取得 (未登録の場合は None)
schedule = r6sss.get_maintenance_schedule(language="ja")

if schedule is not None:
	print(schedule.title, schedule.date, schedule.downtime)

# 以前と現在のステータスを比較
results = r6sss.compare_server_status(statuses, current_statuses, schedule)

for result in results:
	print(result.detail, result.platforms)
```

### HTTP クライアントの指定

タイムアウトやプロキシなどを変更したい場合は、`httpx.Client` を渡せます。

```python
import httpx
import r6sss

with httpx.Client(timeout=10.0) as client:
	statuses = r6sss.get_server_status(client=client)
```

### エラー処理

取得に失敗した場合は例外を送出します。

| 例外 | 内容 |
| --- | --- |
| `R6SSSRequestError` | 通信・タイムアウトに失敗した |
| `R6SSSResponseError` | JSON やレスポンスの形式が想定と異なる |
| `R6SSSAPIError` | API が 200 以外を返した (`status_code`, `detail` を持つ) |

スケジュールが登録されていない場合だけは例外ではなく、`get_maintenance_schedule()` が `None`、`get_maintenance_schedule_list()` が `[]` を返します。

```python
import r6sss

try:
	statuses = r6sss.get_server_status()
except r6sss.R6SSSAPIError as exc:
	print(exc.status_code, exc.detail)
except r6sss.R6SSSError as exc:
	print(exc)
```

### ログ

`r6sss` ロガーには `NullHandler` のみ登録しています。ログを表示する場合は利用側で設定してください。

```python
import logging

logging.basicConfig(level=logging.INFO)
```

## API

- `get_server_status(platforms=None, *, client=None) -> list[Status]`
- `get_maintenance_schedule(language=None, *, client=None) -> MaintenanceSchedule | None`
- `get_maintenance_schedule_list(language=None, *, client=None) -> list[MaintenanceSchedule]`
- `compare_server_status(previous, current, maintenance_schedule=None) -> list[ComparisonResult]`

### データ型

- `Platform` — `PC`, `PS4`, `PS5`, `XB1`, `XBSX`
- `Status` — `platform`, `connectivity`, `authentication`, `matchmaking`, `purchase`, `maintenance`, `features`, `updated_at`, `data`
- `MaintenanceSchedule` — `title`, `detail`, `downtime`, `date`, `patchnotes`, `platforms`
- `ComparisonResult` — `detail`, `platforms`, `impacted_features`, `resolved_impacted_features`

## 開発

```sh
uv sync
uv run ruff check .
uv run pytest
```

## ライセンス

ライセンスは設定していません。
