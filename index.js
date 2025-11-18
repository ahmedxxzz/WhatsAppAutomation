const wppconnect = require('@wppconnect-team/wppconnect');
const express = require('express');

const app = express();
app.use(express.json());

let client;

// Endpoint to send a message
app.post('/send-message', async (req, res) => {
  const { number, message } = req.body;

  if (!client) {
    return res.status(500).json({ status: 'error', message: 'WhatsApp client is not ready' });
  }

  if (!number || !message) {
    return res.status(400).json({ status: 'error', message: 'Missing "number" or "message" in request body' });
  }

  try {
    // Add @c.us to the number for personal messages.
    const result = await client.sendText(`${number}@c.us`, message);
    res.status(200).json({ status: 'success', response: result });
  } catch (error) {
    console.error('Error when sending: ', error);
    res.status(500).json({ status: 'error', message: 'Error sending message', error: error });
  }
});

// Main function to start the WhatsApp client
function startWpp() {
  wppconnect
    .create({
      session: 'mySessionName',
      catchQR: (base64Qr, asciiQR) => {
        console.log('Scan the QR Code below:');
        console.log(asciiQR);
      },
      statusFind: (statusSession, session) => {
        console.log('Status Session: ', statusSession);
        if (statusSession === 'isLogged') {
          // Once logged in, store the client instance
          console.log('Client is logged in!');
        }
      },
    })
    .then((readyClient) => {
      client = readyClient;
      // Now that the client is ready, start the API server
      const port = 3000;
      app.listen(port, () => {
        console.log(`API server listening at http://localhost:${port}`);
      });

      // Optional: Set up a listener for incoming messages
      client.onMessage((message) => {
        console.log(`Received message from ${message.from}: ${message.body}`);
        // For a full solution, you would send this to your Python app via a webhook.
      });
    })
    .catch((error) => {
      console.log(error);
    });
}

// Start the whole process
startWpp();

