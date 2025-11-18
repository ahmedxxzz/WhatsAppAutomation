# L-WAS: WhatsApp Automation

## Overview

L-WAS is a desktop tool that automates sending WhatsApp messages in bulk. It combines:

- **Python GUI** (CustomTkinter) for configuring campaigns and monitoring progress.
- **Node.js server** using **@wppconnect-team/wppconnect** and **Express** to communicate with WhatsApp Web.

You provide a CSV of contacts, define message templates, and the app sends messages through a connected WhatsApp session while respecting a configurable schedule and rate limit.

---

## Project Structure

- `src/`
  - `main.py` – Entry point for the Python GUI.
  - `gui.py` – CustomTkinter-based UI.
  - `worker.py` – Background thread that sends messages via the Node API.
  - `scheduler.py` – Controls when sending is allowed (days & time range).
  - `csv_manager.py` – Loads input CSV and logs worked/failed contacts.
  - `node_client.py` – HTTP client that calls the Node.js server.
  - `utils.py` – Shared utilities (e.g., message formatting).
- `data/`
  - `input.csv` – Example input file: contacts and types.
- `node_server/`
  - `index.js` – Node.js server using `@wppconnect-team/wppconnect` and Express.
  - `package.json` – Node dependencies.
- `requirements.txt` – Python dependencies.

---

## Prerequisites

- **Python** 3.8+ (recommended: 3.10+)
- **Node.js** and **npm** (required for the WhatsApp client)
- A WhatsApp account that will be used to send the messages

> The Node.js/npm installation must be done **before** installing the `@wppconnect-team/wppconnect` package.

---

## 1. Python Environment Setup

From the project root (`WhatsAppAutomation`):

```bash
# (Optional) create a virtual environment
python -m venv .venv

# Windows: activate
.venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

This installs:

- `customtkinter` – GUI
- `requests` – HTTP client for Node server
- `pandas`, `packaging`, `pillow` – CSV handling, utilities, and image support

---

## 2. Node.js & @wppconnect-team/wppconnect Setup

1. **Install Node.js and npm first**

   - Download from: https://nodejs.org/
   - Confirm installation:

     ```bash
     node -v
     npm -v
     ```

2. **Install @wppconnect-team/wppconnect** (as requested):

   From the project root or directly inside `node_server`:

   ```bash
   cd node_server

   # Install the WhatsApp client library
   npm i --save @wppconnect-team/wppconnect
   ```

3. **Install remaining Node dependencies** (from `package.json`):

   Still inside `node_server`:

   ```bash
   npm install
   ```

   This ensures that both `@wppconnect-team/wppconnect` and `express` are installed.

---

## 3. Starting the Node.js WhatsApp Server

From the project root:

```bash
cd node_server
node index.js
```

On first run:

- A QR code is printed in the terminal (ASCII).
- Open **WhatsApp** on your phone → **Linked Devices** → **Link a device**.
- Scan the QR code.
- Once logged in, the console will show that the client is ready and the API server will listen on:

```text
http://localhost:3000
```

The Python GUI will call the `/send-message` endpoint on this server.

> Keep this Node.js process running while you use the Python GUI.

---

## 4. Running the Python GUI Application

In a **separate terminal**, from the project root (`WhatsAppAutomation`):

```bash
# If you use a virtual environment, activate it first
.venv\Scripts\activate  # on Windows

# Run the GUI
py .\src\main.py
# or
python src/main.py
```

This opens the **L-WAS: WhatsApp Automation** window.

Make sure that:

- The Node.js server (`node index.js`) is already running.
- The WhatsApp session is logged in (QR code scanned).

---

## 5. CSV Input Format

The app expects a CSV with at least these columns:

```csv
name,phone,username_type
Ahmed Elbahgy,201028908117,male
Rajab Shabaan,201102555563,female
El Hokage bashaa,201001928364,group
```

- **name** – Display name for the contact
- **phone** – Phone number (including country code, without `+`), e.g. `201028908117`
- **username_type** – One of:
  - `male`
  - `female`
  - `group` (or default)

Place your CSV in `data/input.csv` (or any other path you choose) and select it from the GUI.

---

## 6. Using the GUI

1. **Load CSV**

   - Click **"Load CSV"**.
   - Choose your `input.csv` file.

2. **Configure schedule** (Configuration tab)

   - **Working Days**: e.g. `Mon,Tue,Wed,Thu,Fri`
   - **Start Time / End Time**: e.g. `09:00` to `18:00`
   - Only within these days and times will messages be sent.

3. **Configure rate limit & notification**

   - **Messages per Minute**: e.g. `5`
   - **Completion Notification Number**: optional phone number that will receive a "batch completed" message when the run finishes.

4. **Define templates** (Templates tab)

   There are three templates:

   - **Male Template**
   - **Female Template**
   - **Group/Default Template**

   You can use placeholders:

   - `{name}`
   - `{phone}`
   - `{username_type}`

   Example:

   ```text
   Hi {name}, this is a reminder for your appointment.
   ```

5. **Run Dashboard**

   - Click **START** to begin sending messages.
   - Use **PAUSE/RESUME** to temporarily stop and resume.
   - Use **STOP** to end the run.
   - Progress bar and log window will show real-time status.

---

## 7. Outputs & Logs

- **`worked.csv`** – Contacts successfully processed.
- **`failed.csv`** – Contacts where sending failed, with a reason.
- **`state.json`** – Saved GUI settings (schedule, templates, etc.) so they persist between runs.

These files are created/updated in the project directory when runs complete.

---

## 8. Troubleshooting

- **`ModuleNotFoundError: No module named 'customtkinter'`**
  - Make sure `pip install -r requirements.txt` ran successfully.

- **Cannot connect to Node.js server** or errors like `Connection Error: Node.js server is not reachable.`
  - Ensure `node index.js` is running in `node_server`.
  - Confirm it printed `API server listening at http://localhost:3000`.

- **WhatsApp client is not ready**
  - Make sure you scanned the QR code and the terminal shows that the client is logged in.

- **CSV issues**
  - Check that column headers are exactly: `name`, `phone`, `username_type`.
  - Ensure there are no extra spaces in the header names.

If you encounter a specific traceback or error message, share it along with your steps and configuration to debug further.
