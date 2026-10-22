import datetime

from r6sss import ComparisonDetail, MaintenanceSchedule, Platform, Status, compare_server_status


def make_status(
	platform=Platform.PC,
	*,
	maintenance=False,
	authentication="Operational",
	matchmaking="Operational",
	purchase="Operational",
):
	return Status(
		platform,
		{
			"Status": {
				"Connectivity": "Operational",
				"Features": {
					"Authentication": authentication,
					"Matchmaking": matchmaking,
					"Purchase": purchase,
				},
				"Maintenance": maintenance,
			},
			"UpdatedAt": 1700000000,
		},
	)


def make_schedule():
	return MaintenanceSchedule.create(
		title="Maintenance",
		detail="Detail",
		downtime=60,
		date=datetime.datetime.now(tz=datetime.UTC),
		patchnotes="https://example.com",
		platforms=list(Platform),
	)


def test_start_maintenance():
	previous = [make_status()]
	current = [make_status(maintenance=True)]

	results = compare_server_status(previous, current)

	assert [result.detail for result in results] == [ComparisonDetail.START_MAINTENANCE]


def test_end_maintenance():
	previous = [make_status(maintenance=True)]
	current = [make_status()]

	results = compare_server_status(previous, current)

	assert [result.detail for result in results] == [ComparisonDetail.END_MAINTENANCE]


def test_scheduled_maintenance_start():
	previous = [make_status()]
	current = [make_status(maintenance=True)]

	results = compare_server_status(previous, current, make_schedule())

	assert [result.detail for result in results] == [ComparisonDetail.SCHEDULED_MAINTENANCE_START]


def test_some_features_outage():
	previous = [make_status()]
	current = [make_status(authentication="Outage")]

	results = compare_server_status(previous, current)

	assert [result.detail for result in results] == [ComparisonDetail.SOME_FEATURES_OUTAGE]
	assert results[0].impacted_features == ["Authentication"]


def test_all_features_outage():
	previous = [make_status()]
	current = [make_status(authentication="Outage", matchmaking="Outage", purchase="Outage")]

	results = compare_server_status(previous, current)

	assert [result.detail for result in results] == [ComparisonDetail.ALL_FEATURES_OUTAGE]


def test_features_outage_resolved():
	previous = [make_status(authentication="Outage")]
	current = [make_status()]

	results = compare_server_status(previous, current)

	assert [result.detail for result in results] == [ComparisonDetail.ALL_FEATURES_OUTAGE_RESOLVED]
	assert results[0].resolved_impacted_features == ["Authentication"]


def test_same_change_on_multiple_platforms_is_grouped():
	previous = [make_status(Platform.PC), make_status(Platform.PS5)]
	current = [make_status(Platform.PC, authentication="Outage"), make_status(Platform.PS5, authentication="Outage")]

	results = compare_server_status(previous, current)

	assert len(results) == 1
	assert results[0].platforms == [Platform.PC, Platform.PS5]


def test_missing_previous_platform_is_skipped():
	results = compare_server_status([], [make_status()])

	assert results == []
