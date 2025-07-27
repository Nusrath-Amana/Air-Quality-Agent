import os
import json
import pandas as pd
import matplotlib.pyplot as plt

# Set your data folder path
data_folder = "sensor_data"
all_dfs = []

# Rule-based mapping: extend this if needed
COLUMN_MAPPING = {
    "temp": "temperature",
    "temperature": "temperature",
    "temperature (°c)": "temperature",
    "humidity": "humidity",
    "rh": "humidity",
    "relative humidity (%)": "humidity",
    "co2 (ppm)": "co2",
    "co2": "co2",
    "carbon_dioxide": "co2",
    "timestamp": "timestamp",
    "time": "timestamp",
}


def standardize_columns(df):
    new_cols = {}
    for col in df.columns:
        lower_col = col.strip().lower()
        for key, val in COLUMN_MAPPING.items():
            if key in lower_col:
                new_cols[col] = val
                break
    return df.rename(columns=new_cols)

# Load and standardize all NDJSON files
for filename in os.listdir(data_folder):
    if filename.endswith(".ndjson") and filename.startswith("sensor_data_"):
        filepath = os.path.join(data_folder, filename)
        with open(filepath, "r") as f:
            records = [json.loads(line) for line in f if line.strip()]
            if not records:
                continue
            df = pd.DataFrame(records)

            # Add room name from filename
            room_name = filename.replace("sensor_data_", "").replace(".ndjson", "").strip()
            df["room"] = room_name

            print(f"\n📁 Processing {filename}")
            print("Before standardization:", list(df.columns))

            df = standardize_columns(df)

            print("After standardization:", list(df.columns))
            all_dfs.append(df)

# Combine all rooms into one DataFrame
df_all = pd.concat(all_dfs, ignore_index=True)

# Parse timestamp
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Filter for July 3
df_july_03 = df[df['timestamp'].dt.date == pd.to_datetime('2025-07-03').date()]

# Group by time and take average
temperature_over_time = df_july_03.groupby(df_july_03['timestamp'])['temperature'].mean()

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(temperature_over_time.index, temperature_over_time.values, marker='o')
plt.xlabel('Time')
plt.ylabel('Average Temperature (°C)')
plt.title('Temperature Over Time for July 03')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()