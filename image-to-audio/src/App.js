// src/App.js
import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
    const [file, setFile] = useState(null);
    const [text, setText] = useState('');
    const [audioUrl, setAudioUrl] = useState('');
    const [loading, setLoading] = useState(false);

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) {
            alert("Please select a file first.");
            return;
        }

        setLoading(true);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:5000/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });

            console.log('Response:', response.data);

            const { text, audiobase64 } = response.data;
            setText(text);
            setAudioUrl(`data:audio/mp3;base64,${audiobase64}`);
        } catch (error) {
            console.error('Error uploading file', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="App">
            <h1>Image to Text and Audio Converter</h1>
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleUpload} disabled={loading}>Upload</button>
            {loading ? (
                <p>Processing... Please wait.</p>
            ) : (
                <div>
                    <h3>Text Output:</h3>
                    <p>{text}</p>
                    <h3>Audio Output:</h3>
                    {audioUrl && <audio controls src={audioUrl}></audio>}
                </div>
            )}
        </div>
    );
};

export default App;
