from drone_monitoring.telemetry_monitor import classify
from drone_monitoring.warning_publisher import warnings_for


def test_waiting_and_thresholds():
    assert classify(None, 50, 25) == 'WAITING FOR SENSOR DATA'
    assert classify(30, 20, 60) == 'NORMAL'
    assert classify(10, 19, 30) == 'LOW BATTERY'
    assert classify(10, 50, 61) == 'OVERHEATING'
    assert classify(31, 50, 30) == 'ALTITUDE LIMIT EXCEEDED'
    assert classify(31, 19, 61) == 'LOW BATTERY, OVERHEATING, ALTITUDE LIMIT EXCEEDED'


def test_warning_output():
    assert warnings_for('NORMAL') == 'No active warnings'
    assert warnings_for('WAITING FOR SENSOR DATA') == 'Waiting for telemetry'
    result = warnings_for('LOW BATTERY, OVERHEATING, ALTITUDE LIMIT EXCEEDED')
    assert result.count('[WARNING]') == 3
