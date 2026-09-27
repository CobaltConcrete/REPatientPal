import React, { useState } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || '/upload';

function App() {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState('english');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setError('Choose an image to continue.');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);
    const body = new FormData();
    body.append('file', file);
    body.append('language', language);

    try {
      const response = await fetch(API_URL, { method: 'POST', body });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to process the image.');
      setResult(data);
    } catch (requestError) {
      setError(requestError.message || 'Unable to reach PatientPal.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="App">
      <header className="brand"><span className="brand-mark" aria-hidden="true">✳</span> patientpal</header>
      <section className="hero">
        <p className="eyebrow">YOUR REPORT, MADE CLEARER</p>
        <h1>Understand your<br /><span>health documents.</span></h1>
        <p className="intro">Upload a photo to get a plain-language summary, a translation, and audio you can listen to.</p>
      </section>
      <div className="columns">
        <form className="panel" onSubmit={handleSubmit}>
          <p className="eyebrow">01 · ADD A DOCUMENT</p>
          <h2>Start with a clear photo</h2>
          <label className="dropzone">
            <span className="upload-mark" aria-hidden="true">↑</span>
            <strong>{file ? file.name : 'Choose a photo to upload'}</strong>
            <small>PNG, JPG, or WebP · up to 8 MB</small>
            <input type="file" accept="image/png,image/jpeg,image/webp" onChange={(event) => setFile(event.target.files[0] || null)} />
          </label>
          <label className="field-label" htmlFor="language">TRANSLATE INTO</label>
          <select id="language" value={language} onChange={(event) => setLanguage(event.target.value)}>
            <option value="english">English</option><option value="chinese">简体中文</option><option value="cantonese">廣東話</option><option value="hindi">हिन्दी</option>
          </select>
          <button className="primary-button" disabled={loading}>{loading ? 'Working on it…' : 'Make it clearer'} <span aria-hidden="true">→</span></button>
          <p className="privacy">This app doesn’t save your image. Google Gemini processes it; gTTS receives translated text to create audio.</p>
        </form>
        <section className="panel output" aria-live="polite" aria-busy={loading}>
          <p className="eyebrow">02 · YOUR RESULTS</p>
          <h2>{result ? 'Your report, made clearer' : 'A clearer picture'}</h2>
          {loading && <p className="state">Reading your document…</p>}
          {error && <p className="error" role="alert">{error}</p>}
          {!loading && !error && !result && <p className="state">Your summary and translation will appear here.</p>}
          {result && <>
            <div className="result-block"><p className="result-label">PLAIN-LANGUAGE SUMMARY</p><p>{result.report.summary}</p></div>
            <div className="result-block"><p className="result-label">TRANSLATION</p><p>{result.report.translation}</p></div>
            <details><summary>View extracted text</summary><p>{result.report.source_text}</p></details>
            {result.audio_base64 && <audio controls preload="none" src={`data:${result.audio_mime_type};base64,${result.audio_base64}`} />}
            {!result.audio_base64 && <p className="state">Audio isn’t available right now; you can still read the translation.</p>}
          </>}
          <p className="disclaimer">For understanding documents only. This is not medical advice.</p>
        </section>
      </div>
    </main>
  );
}

export default App;
