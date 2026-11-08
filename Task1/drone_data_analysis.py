"""Explore and clean the supplied drone dataset; no visualization required here."""
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
source = HERE / 'dataset.csv'
data = pd.read_csv(source)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 180)
print('FIRST FIVE ROWS\n', data.head().to_string(index=False))
print('\nSHAPE (rows, columns):', data.shape)
print('\nCOLUMN NAMES\n', data.columns.tolist())
print('\nDATA TYPES\n', data.dtypes.to_string())
print('\nNUMERICAL SUMMARY\n', data.describe().to_string())
print('\nMISSING VALUES\n', data.isna().sum().to_string())
print('\nEXACT DUPLICATE ROWS:', data.duplicated().sum())

# Exact duplicate rows and rows with no data carry no additional information.
clean = data.dropna(how='all').drop_duplicates().copy()
print('\nROWS AFTER REMOVING EMPTY AND EXACT DUPLICATE ROWS:', len(clean))
# Parse known numeric fields explicitly. Unparseable values remain missing.
numeric = ['Propeller Count', 'Max Carry Weight (kg)', 'Actual Carry Weight (kg)',
           'Altitude (meters)', 'Flight Duration (minutes)', 'Distance Flown (km)',
           'Battery Remaining (%)', 'GPS Accuracy (meters)', 'Wind Speed (m/s)']
for col in numeric:
    clean[col] = pd.to_numeric(clean[col], errors='coerce')
clean['Flight Date'] = pd.to_datetime(clean['Flight Date'], format='%d-%m-%Y', errors='coerce')
print('\nUNPARSEABLE OR MISSING DATES:', clean['Flight Date'].isna().sum())
# Negative quantities and battery outside 0-100 are invalid. Preserve the row,
# mark only the affected cell missing; do not guess replacement measurements.
for col in numeric:
    invalid = clean[col].lt(0)
    if col == 'Battery Remaining (%)':
        invalid |= clean[col].gt(100)
    print(f'Invalid {col}: {invalid.sum()}')
    clean.loc[invalid, col] = np.nan
# Size categories are expected to be Small, Medium, or Large; numeric entries
# cannot be interpreted safely, so retain the row and mark its size missing.
invalid_size = clean['Drone Size'].notna() & ~clean['Drone Size'].isin(['Small', 'Medium', 'Large'])
print('Invalid drone size values:', clean.loc[invalid_size, 'Drone Size'].tolist())
clean.loc[invalid_size, 'Drone Size'] = np.nan
# Flag inconsistent or extreme values without claiming they are definitely wrong.
overload = clean['Actual Carry Weight (kg)'] > clean['Max Carry Weight (kg)']
print('\nROWS EXCEEDING STATED MAXIMUM PAYLOAD:', int(overload.sum()))
print(clean.loc[overload, ['Drone ID', 'Max Carry Weight (kg)', 'Actual Carry Weight (kg)']].to_string(index=False))
for col in numeric:
    q1, q3 = clean[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    flagged = clean[col].lt(q1 - 1.5 * iqr) | clean[col].gt(q3 + 1.5 * iqr)
    print(f'Possible IQR outliers in {col}: {int(flagged.sum())}')
print('\nHIGHEST ALTITUDES (possible outliers, retained):')
print(clean.nlargest(5, 'Altitude (meters)')[['Drone ID', 'Altitude (meters)']].to_string(index=False))
clean = clean.sort_values('Flight Date', na_position='last', kind='stable')
clean.to_csv(HERE / 'cleaned_drone_data.csv', index=False, date_format='%Y-%m-%d')
print('\nCLEANED DATA SUMMARY\n', clean[numeric].describe().to_string())
print('\nAPPLICATION COUNTS\n', clean['Application'].value_counts(dropna=False).to_string())
print('\nFLIGHT STATUS COUNTS\n', clean['Flight Status'].value_counts(dropna=False).to_string())
print('\nMEAN FLIGHT DURATION BY DRONE SIZE\n', clean.groupby('Drone Size')['Flight Duration (minutes)'].agg(['count', 'mean']).to_string())
print('\nOBSTACLE COUNTS\n', clean['Obstacles Encountered'].value_counts(dropna=False).to_string())
print('\nSaved cleaned_drone_data.csv. Missing values and flagged outliers are retained for review.')
