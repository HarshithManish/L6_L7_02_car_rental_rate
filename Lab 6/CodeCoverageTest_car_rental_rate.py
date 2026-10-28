import pytest

from car_rental_rate import (
    process_rental_fleet,
    check_fleet_telematics,
)


def test_economy_rental():
    rentals = [{
        "is_confirmed": True,
        "vehicle_type": "economy",
        "driver_age": 30,
        "days": 2,
        "trip_segments": [100],
    }]
    result = process_rental_fleet(rentals, 10.0)
    assert result == {"total_revenue": 110.0, "status": "STANDARD"}


def test_luxury_rental_young_driver():
    rentals = [{
        "is_confirmed": True,
        "vehicle_type": "luxury",
        "driver_age": 20,
        "days": 2,
        "trip_segments": [100],
    }]
    result = process_rental_fleet(rentals, 10.0)
    assert result["total_revenue"] == 370.0


def test_suv_rental():
    rentals = [{
        "is_confirmed": True,
        "vehicle_type": "suv",
        "driver_age": 30,
        "days": 1,
        "trip_segments": [50],
    }]
    result = process_rental_fleet(rentals, 10.0)
    assert result["total_revenue"] == 90.0


def test_unconfirmed_rental():
    result = process_rental_fleet(
        [{"is_confirmed": False}], 10.0
    )
    assert result["status"] == "EMPTY_BATCH"


def test_empty_rental_list():
    result = process_rental_fleet([], 10.0)
    assert result["status"] == "EMPTY_BATCH"


def test_invalid_rental_input():
    with pytest.raises(ValueError):
        process_rental_fleet("invalid", 10.0)


def test_negative_admin_fee():
    with pytest.raises(ValueError):
        process_rental_fleet([], -1.0)


def test_invalid_rental_days():
    result = process_rental_fleet(
        [{"is_confirmed": True, "days": 0}], 10.0
    )
    assert result["total_revenue"] == 0.0


def test_long_trip_adult_driver():
    result = process_rental_fleet(
        [{
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 1,
            "trip_segments": [400],
        }],
        10.0,
    )
    assert result["total_revenue"] == 210.0


def test_long_trip_young_driver():
    result = process_rental_fleet(
        [{
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 20,
            "days": 1,
            "trip_segments": [400, 50],
        }],
        10.0,
    )
    assert result["total_revenue"] == 320.0


def test_negative_trip_distance():
    result = process_rental_fleet(
        [{
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 1,
            "trip_segments": [-10, 50],
        }],
        10.0,
    )
    assert result["total_revenue"] == 60.0


def test_high_risk_audit():
    rentals = [
        {"is_confirmed": True, "days": 0}
        for _ in range(5)
    ]
    result = process_rental_fleet(rentals, 10.0)
    assert result["status"] == "HIGH_RISK_AUDIT"


def test_default_rental_values():
    result = process_rental_fleet(
        [{"is_confirmed": True}], 0.0
    )
    assert result["total_revenue"] == 40.0


def test_no_telematics_data():
    assert check_fleet_telematics([]) == "NO_DATA"


def test_safe_telematics():
    assert check_fleet_telematics(
        [[50, 80, 100, 70], [90, 60]]
    ) == "SAFE"


def test_two_consecutive_speeding_readings():
    assert check_fleet_telematics(
        [[110, 120]]
    ) == "GROUND_VEHICLE"


def test_speeding_streak_reset():
    assert check_fleet_telematics(
        [[110, 90, 120, 130]]
    ) == "GROUND_VEHICLE"