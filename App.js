// src/components/FileUpload.js
import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = () => {
    const [file, setFile] = useState(null);
    const [text, setText] = useState('');
    const [audioUrl, setAudioUrl] = useState('');

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:5000/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });

            setText(response.data.text);
            setAudioUrl(response.data.audio);
        } catch (error) {
            console.error('Error uploading file', error);
        }
    };

    return (
        <div>
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleUpload}>Upload</button>
            <div>
                <h3>Text Output:</h3>
                <p>{text}</p>
                <h3>Audio Output:</h3>
                {audioUrl && <audio controls src={audioUrl}></audio>}
            </div>
        </div>
    );
};

export default FileUpload;
