import datetime

from r6sss import MaintenanceSchedule, Platform, Status


def test_status_unknown_features():
	status = Status(
		Platform.PC,
		{
			"Status": {
				"Connectivity": "Operational",
				"Features": {},
				"Maintenance": False,
			},
			"UpdatedAt": 1700000000,
		},
	)

	assert status.authentication == "Unknown"
	assert status.matchmaking == "Unknown"
	assert status.purchase == "Unknown"
	assert status.maintenance is False
	assert status.updated_at == datetime.datetime.fromtimestamp(1700000000, tz=datetime.UTC)


def test_maintenance_schedule_defaults():
	schedule = MaintenanceSchedule()

	assert schedule.title == ""
	assert schedule.detail == ""
	assert schedule.downtime == 0
	assert schedule.date == datetime.datetime.fromtimestamp(0, tz=datetime.UTC)
	assert schedule.patchnotes == ""
	assert schedule.platforms == []


def test_maintenance_schedule_create():
	date = datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC)

	schedule = MaintenanceSchedule.create(
		title="Maintenance",
		detail="Detail",
		downtime=60,
		date=date,
		patchnotes="https://example.com",
		platforms=[Platform.PC, Platform.PS5],
	)

	assert schedule.title == "Maintenance"
	assert schedule.date == date
	assert schedule.platforms == [Platform.PC, Platform.PS5]


def test_maintenance_schedule_create_with_all_platforms():
	schedule = MaintenanceSchedule.create(
		title="Maintenance",
		detail="Detail",
		downtime=60,
		date=datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC),
		patchnotes="https://example.com",
		platforms=list(Platform),
	)

	assert schedule.platforms == list(Platform)
