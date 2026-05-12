# CodePulse

A self-hosted developer productivity and codebase intelligence platform.
It tracks your coding activity, analyzes codebase health, and generates AI weekly summaries.

## Architecture

```text
                    +-------------------+
                    |   VS Code Ext     |
                    +---------+---------+
                              | (Heartbeats)
                              v
+-----------------------------+-----------------------------+
|                       FastAPI Backend                     |
+-------+---------------------+---------------------+-------+
        |                     |                     |
        | (Storage)           | (Pub/Sub)           | (WS)
        v                     v                     v
+-------+-------+     +-------+-------+     +-------+-------+
|  PostgreSQL   |     |     Redis     |     | React Dashbd  |
| (TimescaleDB) |     |               |     |               |
+---------------+     +---------------+     +---------------+
```

## Quickstart

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/yourusername/codepulse.git
   cd codepulse
   ```

2. **Configure environment**:
   Copy `.env.example` to `.env` and fill in your Gemini API key and email settings.
   ```bash
   cp .env.example .env
   ```

3. **Run with Docker Compose**:
   ```bash
   docker compose up --build
   ```

   The dashboard will be available at `http://localhost:5173`.
   The API will be available at `http://localhost:8000`.

## Extension Installation

1. Navigate to the `extension` folder.
2. Run `npm install`.
3. Press `F5` in VS Code to run it in a new Extension Development Host, or run `vsce package` to build a `.vsix` file and install it manually.
4. In the CodePulse Dashboard, go to **Settings**, create a Device, and copy the API key.
5. In VS Code, run the command `CodePulse: Set API Key` and paste your key.

## API Reference

| Endpoint | Method | Description | Auth |
|---|---|---|---|
| `/api/devices` | `POST` | Create a new device and API key | None |
| `/api/devices` | `GET` | List all devices | None |
| `/api/devices/{id}` | `DELETE` | Delete a device | None |
| `/api/heartbeat` | `POST` | Send heartbeats | Bearer (API Key) |
| `/api/stats/heatmap` | `GET` | Get coding heatmap data | Bearer (API Key) |
| `/api/stats/languages`| `GET` | Get top languages | Bearer (API Key) |
| `/api/stats/projects` | `GET` | Get top projects | Bearer (API Key) |
| `/api/stats/focus` | `GET` | Get focus statistics | Bearer (API Key) |
| `/api/repos` | `POST` | Register a new repository | Bearer (API Key) |
| `/api/repos` | `GET` | List registered repositories | Bearer (API Key) |
| `/api/repos/{id}/analyze` | `POST` | Trigger background analysis | Bearer (API Key) |
| `/api/repos/{id}/health` | `GET` | Get repo health history | Bearer (API Key) |
| `/ws/live/{device_id}` | `WS` | Subscribe to live session feed | None |
