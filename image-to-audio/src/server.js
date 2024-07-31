// server.js or app.js

const express = require('express');
const cors = require('cors');
const multer = require('multer'); // Assuming you're using multer for file uploads
const path = require('path');

// Create an instance of Express
const app = express();

// Enable CORS for all origins
app.use(cors());

// Configure body parsing and file upload middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const upload = multer({ dest: 'uploads/' }); // Configure multer to handle file uploads

// Define your upload endpoint
app.post('/upload', upload.single('file'), (req, res) => {
    // Your upload handling logic here
    const file = req.file;
    // Process the file and return a response
    res.json({
        text: 'example text', // Replace with actual text processing result
        audio: '/audio/cantonese.mp3' // Replace with actual audio file URL
    });
});

// Start the server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
