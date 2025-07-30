import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [textResult, setTextResult] = useState('');
  const [imageUrl, setImageUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setTextResult('');
    setImageUrl(null);

    try {
      const response = await axios.post('http://localhost:8000/ask', { query });
      const { result, image_url, error } = response.data;

      if (error) {
        setError(error);
      } else {
        setTextResult(result || "No response");
        setImageUrl(image_url || null);
      }
    } catch (err) {
      setError("Error contacting backend.");
    } finally {
      setLoading(false);
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
        <button type="submit" disabled={loading}>Submit</button>
      </form>

      <div className="result-container">
        {loading && <p className="loading">Loading...</p>}
        {error && <div className="error">{error}</div>}

        {textResult && !error && (
          <div className="text-result">
            <h3>Result:</h3>
            <pre>{textResult}</pre>
          </div>
        )}

        {imageUrl && !error && (
          <div className="image-result">
            <img
              src={`http://localhost:8000${imageUrl}`}
              alt="Generated visualization"
              style={{ maxWidth: "100%", marginTop: "10px" }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
