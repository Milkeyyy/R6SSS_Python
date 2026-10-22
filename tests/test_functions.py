import httpx
import pytest

from r6sss import (
	Platform,
	R6SSSAPIError,
	R6SSSRequestError,
	R6SSSResponseError,
	get_maintenance_schedule,
	get_maintenance_schedule_list,
	get_server_status,
)

STATUS_DATA = {
	"PC": {
		"Status": {
			"Connectivity": "Operational",
			"Features": {
				"Authentication": "Operational",
				"Leaderboard": "Operational",
				"Matchmaking": "Operational",
				"Purchase": "Operational",
			},
			"Maintenance": False,
		},
		"UpdatedAt": 1700000000,
	},
	"XBSX": {
		"Status": {
			"Connectivity": "Outage",
			"Features": {
				"Authentication": "Outage",
				"Leaderboard": "Operational",
				"Matchmaking": "Outage",
				"Purchase": "Outage",
			},
			"Maintenance": True,
		},
		"UpdatedAt": 1700000001,
	},
}

SCHEDULE_DATA = {
	"Title": "Maintenance",
	"Detail": "Detail",
	"Downtime": 60,
	"Timestamp": 1700000000,
	"Date": "2023-11-14T22:13:20Z",
	"PatchNotes": "https://example.com",
	"Platforms": [{"Name": "All"}],
}


@pytest.fixture
def client_factory():
	def factory(handler):
		return httpx.Client(transport=httpx.MockTransport(handler))

	return factory


def test_get_server_status(client_factory):
	def handler(request):
		assert request.url.params.get_list("platform") == ["PC", "XBSX"]
		return httpx.Response(200, json={"data": STATUS_DATA})

	statuses = get_server_status([Platform.PC, Platform.XBSX], client=client_factory(handler))

	assert [status.platform for status in statuses] == [Platform.PC, Platform.XBSX]
	assert statuses[0].connectivity == "Operational"
	assert statuses[0].maintenance is False
	assert statuses[1].maintenance is True


def test_get_server_status_without_platforms(client_factory):
	def handler(request):
		assert "platform" not in request.url.params
		return httpx.Response(200, json={"data": {}})

	assert get_server_status(client=client_factory(handler)) == []


def test_get_server_status_with_empty_platforms_does_not_request(client_factory):
	def handler(request):
		raise AssertionError("request should not be sent")

	assert get_server_status([], client=client_factory(handler)) == []


def test_get_server_status_raises_response_error_for_unknown_platform(client_factory):
	def handler(request):
		return httpx.Response(200, json={"data": {"PS6": STATUS_DATA["PC"]}})

	with pytest.raises(R6SSSResponseError):
		get_server_status(client=client_factory(handler))


def test_get_server_status_raises_api_error(client_factory):
	def handler(request):
		return httpx.Response(503, json={"detail": "unavailable"})

	with pytest.raises(R6SSSAPIError) as exc_info:
		get_server_status(client=client_factory(handler))

	assert exc_info.value.status_code == 503
	assert exc_info.value.detail == "unavailable"


def test_get_server_status_raises_request_error(client_factory):
	def handler(request):
		raise httpx.ConnectError("connection failed")

	with pytest.raises(R6SSSRequestError):
		get_server_status(client=client_factory(handler))


def test_get_server_status_raises_response_error_for_invalid_json(client_factory):
	def handler(request):
		return httpx.Response(200, text="not json")

	with pytest.raises(R6SSSResponseError):
		get_server_status(client=client_factory(handler))


def test_get_maintenance_schedule(client_factory):
	def handler(request):
		assert request.url.params.get("lang") == "ja"
		return httpx.Response(200, json={"data": SCHEDULE_DATA})

	schedule = get_maintenance_schedule("ja", client=client_factory(handler))

	assert schedule is not None
	assert schedule.title == "Maintenance"
	assert schedule.downtime == 60
	assert schedule.platforms == list(Platform)


def test_get_maintenance_schedule_without_schedule(client_factory):
	def handler(request):
		return httpx.Response(404, json={"detail": "No schedule information found.", "data": None})

	assert get_maintenance_schedule(client=client_factory(handler)) is None


def test_get_maintenance_schedule_with_empty_data(client_factory):
	def handler(request):
		return httpx.Response(200, json={"data": {}})

	assert get_maintenance_schedule(client=client_factory(handler)) is None


def test_get_maintenance_schedule_raises_api_error_for_other_404(client_factory):
	def handler(request):
		return httpx.Response(404, json={"detail": "Not Found"})

	with pytest.raises(R6SSSAPIError):
		get_maintenance_schedule(client=client_factory(handler))


def test_get_maintenance_schedule_list(client_factory):
	def handler(request):
		return httpx.Response(200, json={"data": [SCHEDULE_DATA]})

	schedules = get_maintenance_schedule_list(client=client_factory(handler))

	assert len(schedules) == 1
	assert schedules[0].title == "Maintenance"


def test_get_maintenance_schedule_list_without_schedule(client_factory):
	def handler(request):
		return httpx.Response(404, json={"detail": "No schedule information found.", "data": []})

	assert get_maintenance_schedule_list(client=client_factory(handler)) == []
