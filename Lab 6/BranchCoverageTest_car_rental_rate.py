import pytest

from car_rental_rate import (
    process_rental_fleet,
    check_fleet_telematics,
)


def test_invalid_rentals_type():
    with pytest.raises(ValueError):
        process_rental_fleet("invalid", 10)


def test_negative_admin_fee():
    with pytest.raises(ValueError):
        process_rental_fleet([], -1)


def test_empty_rental_batch():
    result = process_rental_fleet([], 10)
    assert result["status"] == "EMPTY_BATCH"


def test_unconfirmed_rental():
    result = process_rental_fleet(
        [{"is_confirmed": False}], 10
    )
    assert result["status"] == "EMPTY_BATCH"


def test_invalid_days():
    result = process_rental_fleet(
        [{"is_confirmed": True, "days": 0}], 10
    )
    assert result["total_revenue"] == 0.0


def test_luxury_vehicle():
    result = process_rental_fleet(
        [{
            "is_confirmed": True,
            "vehicle_type": "luxury",
            "driver_age": 30,
            "days": 1,
        }],
        10,
    )
    assert result["total_revenue"] == 130.0


def test_suv_vehicle():
    result = process_rental_fleet(
        [{
            "is_confirmed": True,
            "vehicle_type": "suv",
            "driver_age": 30,
            "days": 1,
        }],
        10,
    )
    assert result["total_revenue"] == 80.0


def test_economy_vehicle():
    result = process_rental_fleet(
        [{
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 1,
        }],
        10,
    )
    assert result["total_revenue"] == 50.0


def test_negative_trip_miles():
    result = process_rental_fleet(
        [{
            "is_confirmed": True,
            "driver_age": 30,
            "days": 1,
            "trip_segments": [-5],
        }],
        10,
    )
    assert result["total_revenue"] == 50.0


def test_trip_exactly_300_miles():
    result = process_rental_fleet(
        [{
            "is_confirmed": True,
            "driver_age": 30,
            "days": 1,
            "trip_segments": [300],
        }],
        10,
    )
    assert result["total_revenue"] == 110.0


def test_long_trip_adult():
    result = process_rental_fleet(
        [{
            "is_confirmed": True,
            "driver_age": 30,
            "days": 1,
            "trip_segments": [301],
        }],
        10,
    )
    assert result["total_revenue"] == 170.4


def test_long_trip_young_driver():
    result = process_rental_fleet(
        [{
            "is_confirmed": True,
            "driver_age": 20,
            "days": 1,
            "trip_segments": [301, 50],
        }],
        10,
    )
    assert result["total_revenue"] == 320.0


def test_driver_age_24():
    result = process_rental_fleet(
        [{
            "is_confirmed": True,
            "driver_age": 24,
            "days": 2,
        }],
        10,
    )
    assert result["total_revenue"] == 130.0


def test_driver_age_25():
    result = process_rental_fleet(
        [{
            "is_confirmed": True,
            "driver_age": 25,
            "days": 1,
        }],
        10,
    )
    assert result["total_revenue"] == 50.0


def test_telematics_no_data():
    assert check_fleet_telematics([]) == "NO_DATA"


def test_speed_below_threshold():
    assert check_fleet_telematics([[80, 90, 100]]) == "SAFE"


def test_single_speeding_reading():
    assert check_fleet_telematics([[120]]) == "SAFE"


def test_consecutive_speeding_readings():
    assert check_fleet_telematics(
        [[110, 120]]
    ) == "GROUND_VEHICLE"


def test_speeding_streak_reset():
    assert check_fleet_telematics(
        [[110, 90, 120, 130]]
    ) == "GROUND_VEHICLE"