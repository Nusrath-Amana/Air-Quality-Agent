import pandas as pd
import json
import os
import google.api_core.exceptions
import re
from llama_index.llms.gemini import Gemini
import time
from dotenv import load_dotenv

load_dotenv()

def standardize_columns_with_llm(df, model="gemini-2.5-flash-lite"):
    # Extract sample data
    column_overview = "Here are the columns and their sample values:\n"
    for col in df.columns:
        sample_values = df[col].dropna().astype(str).unique()[:3].tolist()
        column_overview += f"- {col}: {sample_values}\n"

    prompt = f"""{column_overview}

Please map the above columns to a standard schema. 
Use these labels if they match semantically: 'timestamp', 'co2', 'temperature', 'humidity', and 'room'.
Return a JSON object where each key is the original column name and the value is the new standard name.
If a column does not match any, return 'ignore'. 
Respond ONLY with the JSON object.
"""

    llm = Gemini(model=model, temperature=0)
    response = llm.complete(prompt)
    
    # Clean the response to extract JSON
    try:
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = re.sub(r"```(?:json)?", "", raw)
            raw = raw.replace("```", "").strip()

        mapping = json.loads(raw)
        rename_map = {old: new for old, new in mapping.items() if new != "ignore"}
        df.rename(columns=rename_map, inplace=True)
        print("Standardized columns:", df.columns.tolist())
    except Exception as e:
        print("Failed to parse column mapping:", e)
        print("Raw response:", response.text)

    return df



# Folder where all .ndjson files are stored
data_folder = "sensor_data"
df = []

# Loop through all NDJSON files and apply LLM standardization
for filename in os.listdir(data_folder):
    if filename.endswith(".ndjson") and filename.startswith("sensor_data_"):
        filepath = os.path.join(data_folder, filename)
        with open(filepath, "r") as f:
            records = [json.loads(line) for line in f if line.strip()]
            if not records:
                continue
            single_df = pd.DataFrame(records)

            # Add room name
            room_name = filename.replace("sensor_data_", "").replace(".ndjson", "").strip()
            single_df["room"] = room_name

            print(f"\n Processing {filename}")
            print("Before standardization:", list(single_df.columns))

            success = False
            while not success:
                try:
                    single_df = standardize_columns_with_llm(single_df)
                    success = True
                except google.api_core.exceptions.ResourceExhausted as e:
                    print("Quota exceeded. Waiting 60 seconds before retrying...")
                    time.sleep(60)

            print("After standardization:", list(single_df.columns))

            df.append(single_df)

# Combine all DataFrames
if not df:
    raise ValueError("No valid NDJSON files found.")
df = pd.concat(df, ignore_index=True)

# Optional: convert timestamp
if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

print("\n Combined DataFrame shape:", df.shape)
print("Final columns:", list(df.columns))


