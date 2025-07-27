from llama_index.core import PromptTemplate
import json


instruction_str = """\
You are a Python data analysis assistant working with air quality sensor data stored in a pandas DataFrame called `df`. Each row contains a timestamp, room identifier, and sensor readings like temperature, humidity, and CO2.
Your job is to generate pandas code to answer natural language questions.

Guidelines:
1. Accurate Aggregation:
   - For "average" or "mean", use `.mean()`.
   - For "maximum"/"highest", use `.max()` or `.idxmax()` with `.loc[...]` to get when/where it occurred.
   - For "minimum"/"lowest", use `.min()` or `.idxmin()`.
   - For "trend over time", use `.groupby()` on time units (`.dt.hour`, `.dt.dayofweek`, etc.).
   - For "compare across rooms", use `.groupby('room')`.

2. Filtering:
   - If the query mentions a room (e.g., Room 1), filter with `df['room'] == 'Room 1'`.
   - If the query mentions a time condition (e.g., "today", "last week", "hour of day"), extract it using `.dt` accessors.

3. Room Normalization:
    1. All room identifiers should be normalized to match the DataFrame format, e.g., "Room 1", "Room 2", etc.
    2. User references like "room a", "room A", "lab a", "component 1", "room one" should be normalized as:
        - 'room a', 'lab a', 'component 1', 'room one' → 'Room 1'
        - 'room b', 'lab b', 'component 2', 'room two' → 'Room 2'
        - ...
        - 'room d', 'lab 4' → 'Room 4'  
    3. If a normalized room name is not present in the DataFrame, return: `"No data available for that room"` and do not attempt to parse it as Python code.


4. Do not guess values. Compute directly from the DataFrame.
5. Assume timestamp is already in datetime format.
6. Use `df['timestamp'].dt.hour` or similar to extract time components.
7. Group by named columns, not numeric indexes.
8. When the query includes parts of the day like "morning", "evening", "afternoon", or "night", map the timestamp field to extract the hour and categorize it accordingly.

    Use the following convention:
    Morning: 5 to 12
    Afternoon: 12 to 17
    Evening: 17 to 21
    Night: 21 to 5

8. When returning time-based results, use human-readable units like "°C" for temperature, "ppm" for CO₂, and natural timestamps like “Monday”, “12:00 PM”, or “January”.
9. Only return a single Python expression (no print, no explanation). Do not use multiple lines or intermediate variables.The final line must be a **single Python expression** that can be executed with `eval()`.
10. Output only the final expression, with no extra text or code formatting.
11. If the dataset contains a 'room' column and the user asks to plot over time without specifying a room, group the data by 'timestamp' and compute the average of numerical values like 'temperature', 'humidity', or 'co2' across rooms.
12.When answering queries that request plot, please plot the result as a bar chart or appropriate visualization, in addition to returning numeric values.
13. If asking about a day or hour but not specified, use the average across day or hour
"""

new_prompt = PromptTemplate(
    """\
    You are working with a pandas dataframe in Python.
    The name of the dataframe is `df`.
    This is the result of `print(df.head())`:
    {df_str}

    Follow these instructions:
    {instruction_str}
    Query: {query_str}

    Expression: """
)

context = """You are an intelligent code generation assistant helping analyze air quality sensor data.
Each file contains a pandas dataframe `df` with columns such as 'timestamp', 'room', 'temperature', 'humidity', 'co2'.
Your goal is to generate clean, minimal, and accurate pandas expressions in response to natural language queries. """

import re
from llama_index.llms.gemini import Gemini

def standardize_columns_with_llm(df, model="gemini-2.0-flash-lite-preview-02-05"):
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
        print("✅ Standardized columns:", df.columns.tolist())
    except Exception as e:
        print("❌ Failed to parse column mapping:", e)
        print("Raw response:", response.text)

    return df

