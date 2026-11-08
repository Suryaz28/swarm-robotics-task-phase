"""Task 1 Python practice. Run with: python3 python_basics.py"""
from pathlib import Path

# Question 1: Example readings; these are invented, not real flight data.
SENSORS = {
    'altitude': ([10, 25, 60, 85, 105], 'meters', 100, 'above'),
    'battery': ([12.6, 12.1, 11.5, 10.8, 10.2], 'volts', 10.5, 'below'),
    'temperature': ([25, 32, 40, 55, 70], 'degrees C', 60, 'above'),
}

def summarize(readings):
    return min(readings), max(readings), sum(readings) / len(readings), len(readings)

def sensor_analysis():
    choice = input('Choose altitude, battery, or temperature: ').strip().lower()
    if choice not in SENSORS:
        print('Unknown sensor. Please run again and choose one of the options.')
        return
    readings, unit, unsafe_limit, direction = SENSORS[choice]
    low, high, mean, count = summarize(readings)
    print(f'Readings ({unit}): {readings}')
    print(f'Minimum: {low}; maximum: {high}; average: {mean:.2f}; count: {count}')
    try:
        threshold = float(input(f'Enter a threshold in {unit}: '))
    except ValueError:
        print('The threshold must be a number.')
        return
    compare = (lambda value, limit: value < limit) if direction == 'below' else (lambda value, limit: value > limit)
    print(f'Readings {direction} your threshold: {sum(compare(value, threshold) for value in readings)}')
    if any(compare(value, unsafe_limit) for value in readings):
        print(f'Warning: at least one reading is {direction} the example limit of {unsafe_limit} {unit}.')
    print('The example limits are illustrative, not real drone safety specifications.')

# Question 2: A dictionary stores each detail under a descriptive key.
drone = {'drone_id': 'D001', 'model': 'Example Drone', 'altitude_m': 50,
         'battery_percent': 85, 'flight_mode': 'Hover'}

def flight_log():
    # Question 3: Read a text file and append a new sample record.
    path = Path(__file__).resolve().parent / 'flight_log.txt'
    try:
        with path.open('r', encoding='utf-8') as file:
            print('\nExisting flight log:\n' + file.read())
        with path.open('a', encoding='utf-8') as file:
            file.write('D002, sample flight, 15 minutes, completed\n')
        print('Added a sample flight record to flight_log.txt.')
    except OSError as error:
        print(f'Could not read or update the flight log: {error}')

if __name__ == '__main__':
    sensor_analysis()
    print('\nDrone information:', drone)
    flight_log()
