// const { Client, LocalAuth } = require('whatsapp-web.js');
// const qrcode = require('qrcode-terminal');
// const express = require('express');
// const http = require('http');
// const socketIO = require('socket.io');

// const app = express();
// const server = http.createServer(app);
// const io = socketIO(server);

// // WhatsApp Client
// const client = new Client({
//     authStrategy: new LocalAuth(),
//     puppeteer: { headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] }
// });

// // Handle QR Code
// client.on('qr', (qr) => {
//     console.log('QR RECEIVED', qr);
//     qrcode.generate(qr, { small: true });
//     io.emit('qr', qr); // Send QR to frontend via WebSocket
// });

// // Authenticated
// client.on('authenticated', () => {
//     console.log('WhatsApp Authenticated');
//     io.emit('authenticated');
// });

// // Ready
// client.on('ready', () => {
//     console.log('WhatsApp Client Ready!');
//     io.emit('ready');
// });

// // API Endpoint to Send Message
// app.use(express.json());
// app.post('/send-message', (req, res) => {
//     const { number, message } = req.body;
//     client.sendMessage(number + '@c.us', message)
//         .then(response => res.send(response))
//         .catch(err => res.status(500).send(err));
// });

// client.initialize();

// server.listen(3000, () => {
//     console.log('WhatsApp Server running on http://localhost:3000');
// });









//2
// const { Client, LocalAuth } = require('whatsapp-web.js');
// const qrcode = require('qrcode-terminal');
// const express = require('express');
// const bodyParser = require('body-parser');

// const app = express();
// app.use(bodyParser.json());
// const port = 3000;

// // Initialize WhatsApp client
// const client = new Client({
//   authStrategy: new LocalAuth({ dataPath: './session' }), // Save session locally
//   puppeteer: { headless: true } // Run in background
// });

// // Generate QR code and print to terminal
// client.on('qr', (qr) => {
//   qrcode.generate(qr, { small: true }); // Terminal display
//   console.log("QR generated. Share this with Frappe.");
// });

// // Ready to send messages
// client.on('ready', () => {
//   console.log('Client is ready!');
// });

// // Start the client
// client.initialize();

// // API endpoint to send messages
// app.post('/send', async (req, res) => {
//   const { phone, message } = req.body;
//   try {
//     await client.sendMessage(`${phone}@c.us`, message);
//     res.json({ status: 'sent' });
//   } catch (error) {
//     res.status(500).json({ error: 'Failed to send' });
//   }
// });

// // Start the server
// app.listen(port, () => {
//   console.log(`Node.js bridge running on port ${port}`);
// });



//3
// const express = require('express');
// const { Client, LocalAuth } = require('whatsapp-web.js');
// const qrcode = require('qrcode-terminal');

// const app = express();
// app.use(express.json());

// // Initialize WhatsApp client
// const client = new Client({
//   authStrategy: new LocalAuth(),
//   puppeteer: { headless: true } // Run in headless mode
// });

// client.on('qr', (qr) => {
//   qrcode.generate(qr, { small: true }); // Show QR code in terminal
// });

// client.on('ready', () => {
//   console.log('WhatsApp client is ready!');
// });

// client.initialize();

// // API endpoint to send messages
// app.post('/send-message', async (req, res) => {
//   const { phone, message } = req.body;
//   try {
//     const sanitizedPhone = phone.replace(/[^0-9]/g, '');
//     const chatId = `${sanitizedPhone}@c.us`;
//     await client.sendMessage(chatId, message);
//     res.json({ success: true });
//   } catch (error) {
//     res.status(500).json({ error: error.message });
//   }
// });

// app.listen(3000, () => {
//   console.log('Node.js service running on http://localhost:3000');
// });










//4
const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const app = express();
app.use(express.json());

// Configure authentication strategy
const client = new Client({
  authStrategy: new LocalAuth({ dataPath: './sessions' }), // Sessions stored in ./sessions
  puppeteer: { headless: true }
});

let qrCodeData = null;
let isAuthenticated = false;

client.on('qr', async (qr) => {
  qrCodeData = await qrcode.toDataURL(qr); // Generate QR as Data URL
  console.log('QR code generated' + qrCodeData);
});
// client.on('qr', (qr) => {
//     console.log('QR RECEIVED', qr);
//     qrcode.generate(qr, { small: true });
//     io.emit('qr', qr); // Send QR to frontend via WebSocket
// });

client.on('ready', () => {
  isAuthenticated = true;
  console.log('WhatsApp client is ready!');
});

client.on('disconnected', () => {
  isAuthenticated = false;
  console.log('Client disconnected');
});

client.initialize();

// Middleware: API Key Auth (shared with Frappe)
const API_KEY = process.env.API_KEY || 'frappe-secret-key';
app.use((req, res, next) => {
  if (req.headers['x-api-key'] !== API_KEY) {
    return res.status(403).json({ error: 'Unauthorized' });
  }
  next();
});

// Endpoints
app.get('/qr', (req, res) => {
  res.json({ qr: qrCodeData, authenticated: isAuthenticated });
});

app.post('/send-message', async (req, res) => {
  const { phone, message } = req.body;
  if (!isAuthenticated) return res.status(400).json({ error: 'WhatsApp client not authenticated' });
  
  try {
    const chatId = `${phone.replace(/[^0-9]/g, '')}@c.us`;
    await client.sendMessage(chatId, message);
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log('Node.js service running on port 3000');
});