// server.js
const express = require('express');
const bodyParser = require('body-parser');
const multer = require('multer');
const path = require('path');
const fs = require("fs");
const execSync = require('child_process').execSync;
const mysql = require('mysql2');

const app = express();
const port = 3000;


app.use(express.static(path.join(__dirname, '../')));
app.use(bodyParser.json());

// Set up multer for file upload
const storage = multer.diskStorage({
    destination: 'vrp3d/',
    filename: (req, file, cb) => {
        cb(null, file.originalname);
    }
});


const db = mysql.createConnection({
    host: 'localhost',
    user: 'MediTransit',
    password: 'MedTrans',
    database: 'MediTransit',
});

db.connect(err => {
    if (err) {
        console.error('Database connection failed:', err);
    } else {
        console.log('Connected to the database');
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
/*
app.get('/checkFileStatus', (req, res) => {
    const encodedFileName = req.query.fileName;
    const filePath = path.join(__dirname, '../vrp3d', encodedFileName);

    if (fs.existsSync(filePath)) {
        res.json({ fileExists: true });
    } else {
        res.json({ fileExists: false});
    }
});
*/
app.post('/getFileList', (req, res) => {
    const idDriver = req.query.idDriver;
    const folderPath = path.join(__dirname, '../vrp3d/PackingResults/', idDriver);
    console.log(folderPath);
    
    fs.readdir(folderPath, (err, data) => {
        if(err){
            console.error(err);
            res.status(500).json({ error: 'Internal Server Error' });
            return;
        }
        const filteredFiles = data.filter(file => /\.(html)$/i.test(file));
        res.json({files: filteredFiles});
    });
});

app.post('/runcmd', (req, res) => {
    execSync('cd vrp3d && python main.py', (error, stdout, stderr) => {
        if (error) {
            console.error(`Error: ${error.message}`);   
            return;
        }
        console.log(`stdout: ${stdout}`);
        res.status(200).send(`stdout: ${stdout}\nstderr: ${stderr}`);
    });
});


app.post('/runRebuildDatabase', (req, res) => {
    execSync('cd vrp3d && python rebuild_database.py', (error, stdout, stderr) => {
        if (error) {
            console.error(`Error: ${error.message}`);   
            return;
        }
        console.log(`stdout: ${stdout}`);
        res.status(200).send(`stdout: ${stdout}\nstderr: ${stderr}`);
    });
});

app.post('/runGenerateOrders', (req, res) => {
    execSync('cd vrp3d && python generate_orders.py', (error, stdout, stderr) => {
        if (error) {
            console.error(`Error: ${error.message}`);   
            return;
        }
        console.log(`stdout: ${stdout}`);
        res.status(200).send(`stdout: ${stdout}\nstderr: ${stderr}`);
    });
});

app.post('/runGenerateAvalVehicle', (req, res) => {
    execSync('cd vrp3d && python generate_vehicles.py', (error, stdout, stderr) => {
        if (error) {
            console.error(`Error: ${error.message}`);   
            return;
        }
        console.log(`stdout: ${stdout}`);
        res.status(200).send(`stdout: ${stdout}\nstderr: ${stderr}`);
    });
});

app.post('/runDeliverAll', (req, res) => {
    execSync('cd vrp3d && python deliver_orders.py', (error, stdout, stderr) => {
        if (error) {
            console.error(`Error: ${error.message}`);   
            return;
        }
        console.log(`stdout: ${stdout}`);
        res.status(200).send(`stdout: ${stdout}\nstderr: ${stderr}`);
    });
});

// QUERIES

app.get('/avalVehicleList', (req, res) => {
    try{
        const query = `select Vehicle.id, Vehicle.type, Driver.name, Branch.code from AvailableVehicle
        inner join Vehicle on AvailableVehicle.vehicle_id = Vehicle.id
        inner join Driver on Vehicle.driver_id = Driver.id
        inner join Branch on Vehicle.branch_id = Branch.id;`;
        db.query(query, (err, result) => {
            if(err){
                console.error('Database query error: ', err);
                res.status(500).json({error: 'Internal Server Error'});
            }else{
                //console.log('Available Vehicle query: ', result);
                res.json(result);
            }
        })
    }catch(err){
        console.error('Error in /avalVehicleList', err);
    }
});

app.get('/orderList', (req, res) => {
    try{
        const query = `select order_id, relation_id, Branch.code as branch_code, product_id, quantity, Product.code as product_code, status, delivery_category from Orders 
        inner join OrderDetail on Orders.id = OrderDetail.order_id 
        inner join Product on OrderDetail.product_id = Product.id 
        inner join Branch on Orders.branch_id = Branch.id
        where Orders.status in ('Pending', 'Not-Sent');`;
        db.query(query, (err, result) => {
            if(err){
                console.error('Database query error: ', err);
                res.status(500).json({error: 'Internal Server Error'});
            }else{
                //console.log('Order List Query: ', result);
                res.json(result);
            }
        })
    }catch(err){
        console.error('Error in /avalVehicleList', err);
    }
});

app.get('/tbDistributedCount', (req, res) => {
    try{
        const query = `select count(*) from Orders
        where Orders.status in ('Pending', 'Not-Sent');`;
        db.query(query, (err, result) => {
            if(err){
                console.error('Database query error: ', err);
                res.status(500).json({error: 'Internal Server Error'});
            }else{
                //console.log('To-be Distributed count: ', result);
                res.json(result);
            }
        })
    }catch(err){
        console.error('Error in /avalVehicleList', err);
    }
});

app.get('/onDistributionCount', (req, res) => {
    try{
        const query = `select count(*) from Orders
        where Orders.status in ('On-Delivery');`;
        db.query(query, (err, result) => {
            if(err){
                console.error('Database query error: ', err);
                res.status(500).json({error: 'Internal Server Error'});
            }else{
                //console.log('On Distribution count:  ', result);
                res.json(result);
            }
        })
    }catch(err){
        console.error('Error in /avalVehicleList', err);
    }
});

app.get('/distributedCount', (req, res) => {
    try{
        const query = `select count(*) from Orders
        where Orders.status in ('Delivered');`;
        db.query(query, (err, result) => {
            if(err){
                console.error('Database query error: ', err);
                res.status(500).json({error: 'Internal Server Error'});
            }else{
                //console.log('Distributed Count: ', result);
                res.json(result);
            }
        })
    }catch(err){
        console.error('Error in /avalVehicleList', err);
    }
});

app.get('/citocount', (req, res) => {
    try{
        const query = `select count(*) from (
            select Orders.id from Orders 
            inner join OrderDetail on Orders.id = OrderDetail.order_id
            inner join Product on OrderDetail.product_id = Product.id
            where Orders.status in ('Pending', 'Not-Sent') and Product.is_life_saving = '1' group by Orders.id
            ) temp;`;
        db.query(query, (err, result) => {
            if(err){
                console.error('Database query error: ', err);
                res.status(500).json({error: 'Internal Server Error'});
            }else{
                //console.log('CITO count: ', result);
                res.json(result);
            }
        })
    }catch(err){
        console.error('Error in /avalVehicleList', err);
    }
});

app.get('/accidentCount', (req, res) => {
    try{
        const query = `select count(*) from DeliveryTrouble 
        where status = 'Urgent' and trouble_type = 'Traffic Accident';`;

        db.query(query, (err, result) => {
            if(err){
                console.error('Database query error: ', err);
                res.status(500).json({error: 'Internal Server Error'});
            }else{
                //console.log('Accident Count: ', result);
                res.json(result);
            }
        })
    }catch(err){
        console.error('Error in /avalVehicleList', err);
    }
});

app.get('/shipmentList', (req, res) => {
    try{
        const query = `select * from Shipment
        where status in ('On-Delivery');`;
        db.query(query, (err, result) => {
            if(err){
                console.error('Database query error: ', err);
                res.status(500).json({error: 'Internal Server Error'});
            }else{
                //console.log('On Delivery List: ', result);
                res.json(result);
            }
        })
    }catch(err){
        console.error('Error in /avalVehicleList', err);
    }
});

app.get('/deliveryTroubleList', (req, res) => {
    try{
        const query = `select Vehicle.driver_id, Driver.name, DeliveryTrouble.id, DeliveryTrouble.vehicle_id, DeliveryTrouble.trouble_type, DeliveryTrouble.status, DeliveryTrouble.event_time from DeliveryTrouble 
        inner join Vehicle on DeliveryTrouble.vehicle_id = Vehicle.id
        inner join Driver on Vehicle.driver_id = Driver.id
        where DeliveryTrouble.status = 'Urgent' and (trouble_type = 'Traffic Congestion' OR trouble_type = 'Traffic Accident');`;
        db.query(query, (err, result) => {
            if(err){
                console.error('Database query error: ', err);
                res.status(500).json({error: 'Internal Server Error'});
            }else{
                //console.log('Delivery Troubles: ', result);
                res.json(result);
            }
        })
    }catch(err){
        console.error('Error in /avalVehicleList', err);
    }
});

app.post('/deliveryTroubleResolve', (req, res) => {
    try {
        const { id } = req.body; 

        const query = 'UPDATE DeliveryTrouble SET status = "Resolved" WHERE id = ?';
        db.query(query, [id]);

        res.status(200).json({ success: true });
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.get('/deliverytroubleAll', (req, res) => {
    try {
        const query = `SELECT * FROM deliverytrouble WHERE trouble_type = 'Traffic Accident'`;
        db.query(query, (err, result) => {
            if(err){
                console.error('Database query error:', err);
                res.status(500).json({error: 'Internal Server Error'});
            } else{
                //console.log('Delivery trouble query: ', result);
                res.json(result);
            }
        })
    } catch (err) {
        console.error('error in /deliverytrouble', error);
        res.status(500).json({error: 'Internal Server Error'});
    }
});

app.get('/deliverytroubleAccident', (req, res) => {
    try {
        const query = `SELECT * FROM deliverytrouble WHERE trouble_type = 'Traffic Accident'`;
        db.query(query, (err, result) => {
            if(err){
                console.error('Database query error:', err);
                res.status(500).json({error: 'Internal Server Error'});
            } else{
                //console.log('Delivery trouble query: ', result);
                res.json(result);
            }
        })
    } catch (err) {
        console.error('error in /deliverytrouble', error);
        res.status(500).json({error: 'Internal Server Error'});
    }
});

app.get('/shipmentIdList', (req, res) => {
    try {
        const idDriver = req.query.idDriver;
        const query = `select Shipment.id from Shipment
        inner join Vehicle on Shipment.vehicle_id = Vehicle.id
        where Vehicle.driver_id = '${idDriver}';`;
        db.query(query, (err, result) => {
            if(err){
                console.error('Database query error:', err);
                res.status(500).json({error: 'Internal Server Error'});
            } else{
                //console.log('Delivery trouble query: ', result);
                res.json(result);
            }
        })
    } catch (err) {
        console.error('error in /deliverytrouble', error);
        res.status(500).json({error: 'Internal Server Error'});
    }
});

app.get('/routes', async (req, res) => {
    try {
        let idShipment = req.query.shipmentId;

        idShipment = parseInt(idShipment);

        const query = `select RouteData.shipment_id, Driver.name as driver_name, Vehicle.type as vehicle_type, RouteData.visitation_order, Relation.address, Relation.latitude, Relation.longitude, Orders.id as order_id from RouteData
        inner join Shipment on Shipment.id = RouteData.shipment_id
        inner join Vehicle on Shipment.vehicle_id = Vehicle.id
        inner join Driver on Vehicle.driver_id = Driver.id
        inner join Relation on RouteData.relation_id = Relation.id
        inner join Orders on Orders.shipment_id = Shipment.id and Orders.relation_id = Relation.id
        where Shipment.id = ${idShipment}
        order by visitation_order;`;
        //console.log('Query:', query);

        db.query(query, (err, result) => {
            if (err) {
                console.error('Database query error:', err);
                res.status(500).json({ error: 'Internal Server Error' });
            } else {
                //console.log('Routes List:', result);
                res.json(result);
            }
        });
    } catch (error) {
        console.error('Error in /routes:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.get('/warehouseLocation', async (req, res) => {
    try {
        let idShipment = req.query.shipmentId;

        idShipment = parseInt(idShipment);

        const query = `select Branch.code, latitude, longitude, address from Branch
        inner join Shipment on Branch.id = Shipment.branch_id
        where Shipment.id = ${idShipment};`;
        //console.log('Query:', query);

        db.query(query, (err, result) => {
            if (err) {
                console.error('Database query error:', err);
                res.status(500).json({ error: 'Internal Server Error' });
            } else {
                //console.log('Routes List:', result);
                res.json(result);
            }
        });
    } catch (error) {
        console.error('Error in /routes:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.get('/username', async (req, res) => {
    try {
        let idDriver = req.query.idDriver;

        idDriver = parseInt(idDriver);

        const query = `select name from driver where id=${idDriver};`;
        //console.log('Query:', query);

        db.query(query, (err, result) => {
            if (err) {
                console.error('Database query error:', err);
                res.status(500).json({ error: 'Internal Server Error' });
            } else {
                //console.log('Routes List:', result);
                res.json(result);
            }
        });
    } catch (error) {
        console.error('Error in /routes:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.get('/vehicleId', async (req, res) => {
    try {
        let idDriver = req.query.idDriver;

        idDriver = parseInt(idDriver);

        const query = `select Vehicle.id from Vehicle
        inner join Driver on Vehicle.driver_id = Driver.id
        where Driver.id = ${idDriver};`;

        //console.log('Query:', query);

        db.query(query, (err, result) => {
            if (err) {
                console.error('Database query error:', err);
                res.status(500).json({ error: 'Internal Server Error' });
            } else {
                //console.log('Routes List:', result);
                res.json(result);
            }
        });
    } catch (error) {
        console.error('Error in /routes:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.post('/report', (req, res) => {
    try {
        const { vehicleId, troubleType, details } = req.body;
        const query = `INSERT INTO DeliveryTrouble(vehicle_id, trouble_type, details, status, event_time)
                       VALUES (?, ?, ?, 'Urgent', NOW());`;

        //console.log('Executing SQL query:', query);
        //console.log('Query parameters:', [vehicleId, troubleType, details]);
        db.query(query, [vehicleId, troubleType, details]);

        res.status(200).json({ success: true });
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});