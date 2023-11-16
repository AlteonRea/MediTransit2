// server.js
const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require("fs");

const app = express();
const port = 3000;


app.use(express.static(path.join(__dirname, '../')));

// Set up multer for file upload
const storage = multer.diskStorage({
    destination: 'uploads/',
    filename: (req, file, cb) => {
        cb(null, file.originalname);
    }
});

const upload = multer({ storage });

// Serve HTML file
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

// Handle file upload
app.post('/upload', upload.single('file'), (req, res) => {
    res.json({ message: 'File uploaded successfully', fileName: req.file.originalname });
});

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/route.html');
});

app.get('../assets/panduan.pdf', (req, res) => {
    res.download(__dirname + '../assets/panduan.pdf');
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});

// Check file

app.get('/checkFileStatus', (req, res) => {
    const encodedFileName = req.query.fileName;
    const filePath = path.join(__dirname, '../uploads', encodedFileName);

    if (fs.existsSync(filePath)) {
        res.json({ fileExists: true });
    } else {
        res.json({ fileExists: false});
    }
});