from dotenv import load_dotenv
import os
import pandas as pd
import json
from llama_index.experimental.query_engine import PandasQueryEngine
from prompts import new_prompt, instruction_str, context,standardize_columns_with_llm
from note_engine import note_engine
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
import time
import google.api_core.exceptions
from llama_index.core.memory import ChatMemoryBuffer
import matplotlib.pyplot as plt


import google.generativeai as genai

load_dotenv()
# Configure Gemini first
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Then proceed with your existing imports and code
from llama_index.core import Settings
Settings.llm = Gemini(model="gemini-2.0-flash-lite-preview-02-05")

# Folder where all .ndjson files are stored
data_folder = "sensor_data"
all_dfs = []

# Loop through all NDJSON files and apply LLM standardization
for filename in os.listdir(data_folder):
    if filename.endswith(".ndjson") and filename.startswith("sensor_data_"):
        filepath = os.path.join(data_folder, filename)
        with open(filepath, "r") as f:
            records = [json.loads(line) for line in f if line.strip()]
            if not records:
                continue
            df = pd.DataFrame(records)

            # Add room name
            room_name = filename.replace("sensor_data_", "").replace(".ndjson", "").strip()
            df["room"] = room_name

            print(f"\n📁 Processing {filename}")
            print("Before standardization:", list(df.columns))

            success = False
            while not success:
                try:
                    df = standardize_columns_with_llm(df)
                    success = True
                except google.api_core.exceptions.ResourceExhausted as e:
                    print("⏳ Quota exceeded. Waiting 60 seconds before retrying...")
                    time.sleep(60)

            print("After standardization:", list(df.columns))

            all_dfs.append(df)

# Combine all DataFrames
if not all_dfs:
    raise ValueError("No valid NDJSON files found.")
final_df = pd.concat(all_dfs, ignore_index=True)

# Optional: convert timestamp
if "timestamp" in final_df.columns:
    final_df["timestamp"] = pd.to_datetime(final_df["timestamp"], errors="coerce")

print("\n✅ Combined DataFrame shape:", final_df.shape)
print("✅ Final columns:", list(final_df.columns))


population_query_engine = PandasQueryEngine(
    df=final_df, 
    verbose=True, 
    instruction_str=instruction_str,
    enable_visualization=True 
)
population_query_engine.update_prompts({"pandas_prompt": new_prompt})

tools = [
    QueryEngineTool(
        query_engine=population_query_engine,
        metadata=ToolMetadata(
            name="sensor_data",
            description="timestamp', 'co2', 'temperature', 'humidity' value for each room",
        ),
    )
]

memory = ChatMemoryBuffer.from_defaults(token_limit=4000)

agent = ReActAgent.from_tools(tools, llm=Settings.llm, memory=memory, verbose=True, context=context)

# while (prompt := input("Enter a prompt (q to quit): ")) != "q":
#     result = agent.query(prompt)
#     print(result)

response = agent.query("how temperature change over time on july 03")
fig = plt.gcf()  # Get current figure
fig.savefig("chart.png")
print("✅ Chart saved as chart.png")