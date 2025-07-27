# 🧠 Air Quality AI Agent

An intelligent web application that lets users analyze air quality sensor data from multiple rooms using **natural language queries**.

The system uses **Retrieval-Augmented Generation (RAG)** powered by **LlamaIndex**, **Gemini Pro API**, and custom tool use to read and process raw `.ndjson` sensor data files directly.

---

## 🔍 Features

- 💬 Natural language query interface
- 📁 Works directly with raw `.ndjson` files (one per room)
- 🧠 Uses **LlamaIndex** to power semantic understanding of queries
- 🔌 Integrated with **Gemini API** for LLM capabilities
- 🛠️ Handles inconsistencies in field names across files (e.g., `co2`, `CO2 (PPM)`, etc.)
- 📊 Generates answers with **text, tables, and charts**
- 🧱 Built with:
  - `FastAPI` (Python backend)
  - `React.js` (frontend)
  - `.env` support for API keys and config
- 🧠 Dynamically executes code for analysis as part of the agent

---

## 🧪 Example Queries

- "How does the temperature in Room A change by hour of the day?"
- "Which room had the highest temperature reading last week?"
- "How does CO₂ vary by day of the week?"
- "List the rooms from hottest to coolest by daily average temperature"

---


## 📂 Project Structure

```plaintext
Air_quality_web/
├── backend/
│   ├── main.py               # FastAPI backend
│   ├── agent.py              # LLM + tool integration
│   ├── utils/
│   │   └── file_reader.py    # Data loading and normalization
│   ├── .env                  # API keys and config
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # React UI
│   │   ├── components/       # UI components
│   └── public/
├── data/
│   └── room_a.ndjson
│   └── room_b.ndjson
└── README.md
