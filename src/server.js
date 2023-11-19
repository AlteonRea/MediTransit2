// server.js
const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require("fs");
const execSync = require('child_process').execSync;

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

app.get('/checkFileStatus', (req, res) => {
    const encodedFileName = req.query.fileName;
    const filePath = path.join(__dirname, '../uploads', encodedFileName);

    if (fs.existsSync(filePath)) {
        res.json({ fileExists: true });
    } else {
        res.json({ fileExists: false});
    }
});

app.post('/getFileList', (req, res) => {
    const idDriver = req.query.idDriver;
    const folderPath = path.join(__dirname, '../uploads/PackingResults/', idDriver);
    console.log(folderPath);
    
    fs.readdir(folderPath, (err, data) => {
        if(err){
            console.error(err);
            res.status(500).json({ error: 'Internal Server Error' });
            return;
        }
        const filteredFiles = data.filter(file => /\.(html|txt)$/i.test(file));
        res.json({files: filteredFiles});
    });
});

app.post('/runcmd', (req, res) => {
    execSync('cd uploads && python main.py', (error, stdout, stderr) => {
        if (error) {
            console.error(`Error: ${error.message}`);   
            return;
        }
        console.log(`stdout: ${stdout}`);
        res.status(200).send(`stdout: ${stdout}\nstderr: ${stderr}`);
    });
});


app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});