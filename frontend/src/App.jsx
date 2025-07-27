import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult("Loading...");
    try {
      const response = await axios.post('http://localhost:8000/ask', { query });
      setResult(response.data.result || response.data.error);
    } catch (err) {
      setResult("Error contacting backend.");
    }
  };

  return (
    <div className="App">
      <h1>🌿 Air Quality Query</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          rows={4}
          cols={50}
          placeholder="Ask something like: What's the average CO₂ level in Room 2 last week?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <br />
        <button type="submit">Submit</button>
      </form>
      <div className="result">
        <h3>📊 Result:</h3>
        <pre>{result}</pre>
      </div>
    </div>
  );
}

export default App;
