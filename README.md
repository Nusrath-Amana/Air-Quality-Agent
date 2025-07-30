# 🌿 Air Quality AI Agent

An intelligent web application that lets users analyze air quality sensor data from multiple rooms using **natural language queries**.

The system uses **LlamaIndex**, **Gemini API**, and custom tool use to read and process raw `.ndjson` sensor data files directly.

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

## 📂 Project Structure

```plaintext
Air_quality_web/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── agent_loader.py      # Loads LLM agent with tools
│   ├── prompts.py           # Prompt templates and instructions
│   ├── data.py              # Loads and standardizes NDJSON sensor data
│   ├── sensor_data/         # Folder with .ndjson sensor files
│   ├── .env                 # Gemini API key and configs
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   └── App.jsx          # React frontend
│   └── public/
└── README.md 
```
## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- Google Gemini API key

### Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/Nusrath-Amana/Air-Quality-Agent.git
   cd Air-Quality-Agent
   ```
2. **Set up the backend**  
  - Create and activate a virtual environment:  
  ```bash
  python -m venv venv
  source venv\Scripts\activate # On Windows
  ```
  - Install dependencies:
  ```bash
  cd backend
  pip install -r requirements.txt
  ```

  - Add .env file:
    - Create a .env file inside the backend/ folder with the following content:
  ```env
  GOOGLE_API_KEY=your_gemini_api_key_here
  ```

  - Start the FastAPI backend:
  ```bash
  uvicorn main:app --reload
  ```
3. Set up the frontend  
- Open a new terminal window/tab:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

## ✅ Notes
- Place your .ndjson sensor data files inside the backend/sensor_data/ folder.
- Ensure the .env file has a valid Google Gemini API key.

---

## 🧪 Example Queries

- "How does the temperature in Room A change by hour of the day?"
- "Which room had the highest temperature reading last week?"
- "How does CO₂ vary by day of the week?"
- "List the rooms from hottest to coolest by daily average temperature"
