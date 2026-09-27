import React, { useCallback, useEffect, useRef, useState } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || '/upload';
const GLOSSARY_URL = process.env.REACT_APP_GLOSSARY_URL || API_URL.replace(/\/upload\/?$/, '/glossary');

function LinkedText({ text, terms, language, onLookup }) {
  const names = [...new Set((terms || []).filter(Boolean))].sort((a, b) => b.length - a.length);
  if (!names.length) return text;
  const pattern = new RegExp(`(${names.map((name) => name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'gi');
  return String(text).split(pattern).map((part, index) => {
    const match = names.find((name) => name.toLowerCase() === part.toLowerCase());
    return match
      ? <button className="glossary-link" type="button" key={`${part}-${index}`} onClick={() => onLookup(match, language)}>{part}</button>
      : part;
  });
}

function ReportBlocks({ blocks, fallback, terms, language, onLookup }) {
  if (!Array.isArray(blocks) || blocks.length === 0) {
    return <p className="report-prose"><LinkedText text={fallback} terms={terms} language={language} onLookup={onLookup} /></p>;
  }
  return blocks.map((block, index) => {
    const linked = (text) => <LinkedText text={text} terms={terms} language={language} onLookup={onLookup} />;
    if (block.type === 'heading') return <h3 className="report-heading" key={index}>{linked(block.text)}</h3>;
    if (block.type === 'bullets' || block.type === 'numbered') {
      const List = block.type === 'bullets' ? 'ul' : 'ol';
      return <List className="report-list" key={index}>{(block.items || []).map((item, itemIndex) => <li key={itemIndex}>{linked(item)}</li>)}</List>;
    }
    return <p className="report-prose" key={index}>{linked(block.text)}</p>;
  });
}

function App() {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState('english');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [glossary, setGlossary] = useState(null);
  const glossaryCache = useRef(new Map());
  const glossaryRequests = useRef(new Map());

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
      setError(requestError instanceof TypeError
        ? 'Could not connect to the NightingAIe service. Check that the API is running and REACT_APP_API_URL points to its /upload endpoint.'
        : requestError.message || 'Unable to process this document. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  const loadGlossary = useCallback((term, glossaryLanguage) => {
    const key = `${glossaryLanguage}:${term.trim().toLocaleLowerCase()}`;
    if (glossaryCache.current.has(key)) return Promise.resolve(glossaryCache.current.get(key));
    if (glossaryRequests.current.has(key)) return glossaryRequests.current.get(key);

    const url = `${GLOSSARY_URL}?term=${encodeURIComponent(term)}&language=${encodeURIComponent(glossaryLanguage)}`;
    const request = fetch(url)
      .then(async (response) => {
        const data = await response.json();
        if (response.status === 404) {
          const missing = { term, error: data.error || data.detail || 'No trusted definition was found for this term.' };
          glossaryCache.current.set(key, missing);
          return missing;
        }
        if (!response.ok) throw new Error(data.error || data.detail || 'The glossary is temporarily unavailable.');
        glossaryCache.current.set(key, data);
        return data;
      })
      .finally(() => glossaryRequests.current.delete(key));
    glossaryRequests.current.set(key, request);
    return request;
  }, []);

  const openGlossary = useCallback(async (term, glossaryLanguage) => {
    setGlossary({ term, loading: true });
    try {
      setGlossary({ ...(await loadGlossary(term, glossaryLanguage)), loading: false });
    } catch (lookupError) {
      setGlossary({ term, error: lookupError.message || 'The glossary is temporarily unavailable.', loading: false });
    }
  }, [loadGlossary]);

  useEffect(() => {
    const terms = result?.report?.glossary_terms || [];
    if (!terms.length) return undefined;
    const languages = language === 'english' ? ['english'] : ['english', language];
    const queue = terms.flatMap((term) => languages.map((itemLanguage) => [term, itemLanguage]));
    let next = 0;
    let cancelled = false;
    const worker = async () => {
      while (!cancelled && next < queue.length) {
        const [term, itemLanguage] = queue[next++];
        try { await loadGlossary(term, itemLanguage); } catch (_) { /* retry on user click */ }
      }
    };
    Promise.all(Array.from({ length: Math.min(3, queue.length) }, worker));
    return () => { cancelled = true; };
  }, [result, language, loadGlossary]);

  return (
    <main className="App">
      <header className="brand"><span className="brand-mark" aria-hidden="true">✳</span> NightingAIe</header>
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
          <p className="privacy">This app does not save your image. Google Gemini processes it; gTTS receives translated text for audio. Recognized medical terms are checked against U.S. National Library of Medicine sources, and definitions are translated by Gemini when needed.</p>
        </form>
        <section className="panel output" aria-live="polite" aria-busy={loading}>
          <p className="eyebrow">02 · YOUR RESULTS</p>
          <h2>{result ? 'Your report, made clearer' : 'NightingAIe'}</h2>
          {loading && <p className="state">Reading your document…</p>}
          {error && <p className="error" role="alert">{error}</p>}
          {!loading && !error && !result && <p className="state">Your summary and translation will appear here.</p>}
          {result && <>
            <div className="result-block"><p className="result-label">PLAIN-LANGUAGE SUMMARY</p><ReportBlocks blocks={result.report.summary_blocks} fallback={result.report.summary} terms={result.report.glossary_terms} language="english" onLookup={openGlossary} /></div>
            <div className="result-block"><p className="result-label">TRANSLATION</p><ReportBlocks blocks={result.report.translation_blocks} fallback={result.report.translation} terms={result.report.glossary_terms} language={language} onLookup={openGlossary} /></div>
            <details><summary>View extracted text</summary><p>{result.report.source_text}</p></details>
            {result.audio_base64 && <audio controls preload="none" src={`data:${result.audio_mime_type};base64,${result.audio_base64}`} />}
            {!result.audio_base64 && <p className="state">Audio isn’t available right now; you can still read the translation.</p>}
          </>}
          <p className="disclaimer">For understanding documents only. This is not medical advice.</p>
        </section>
      </div>
      {glossary && <div className="glossary-backdrop" role="presentation" onClick={(event) => { if (event.target === event.currentTarget) setGlossary(null); }}>
        <section className="glossary-dialog" role="dialog" aria-modal="true" aria-labelledby="glossary-title">
          <button className="glossary-close" type="button" aria-label="Close definition" onClick={() => setGlossary(null)}>×</button>
          <p className="eyebrow">MEDICAL GLOSSARY</p>
          <h2 id="glossary-title">{glossary.term}</h2>
          {glossary.loading && <p className="state">Looking up a trusted explanation…</p>}
          {glossary.error && <p className="error" role="alert">{glossary.error}</p>}
          {glossary.definition && <p className="glossary-definition">{glossary.definition}</p>}
          {glossary.translated && <p className="glossary-translation-note">AI translation of information from {glossary.sources?.[0]?.name || 'the cited medical source'}.</p>}
          {glossary.sources?.length > 0 && <div className="glossary-sources"><strong>Sources</strong>{glossary.sources.map((source) => <a key={source.url} href={source.url} target="_blank" rel="noreferrer">{source.name}</a>)}</div>}
          <p className="glossary-note">For general education only. This explanation does not say whether the medicine or term applies to you.</p>
        </section>
      </div>}
    </main>
  );
}

export default App;
