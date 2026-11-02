# Background Job API (FlyRank A7)

A small FastAPI service that accepts a report request quickly and processes it
as an Inngest background function. It also includes retries, input validation,
a status endpoint, and a scheduled heartbeat.

> **Important:** This is a starter project. It has not been executed or verified
> in your environment. Run the checkpoints below and replace the proof section
> with your own real outputs and screenshots before submitting.

## Requirements

- Python 3.10+
- Node.js/npm (to run the local Inngest Dev Server)
- Git

## Setup (Windows Command Prompt)

```bat
cd background-job
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the API

Terminal 1 — activate the environment if needed, then:

```bat
.venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

Terminal 2 — from the project folder:

```bat
npx inngest-cli@latest dev -u http://localhost:8000/api/inngest
```

Open the local dashboard at http://localhost:8288.

Keep both terminals running.

## Endpoints and functions

| Name | Type | Purpose |
|---|---|---|
| `GET /health` | HTTP endpoint | Returns `{"status":"ok"}` |
| `POST /reports` | HTTP endpoint | Validates a topic, queues a report event, returns HTTP 202 |
| `GET /reports/{report_id}` | HTTP endpoint | Returns the saved report or HTTP 404 |
| `GET /reports` | HTTP endpoint | Lists reports held in memory |
| `say-hello` | Inngest function | Triggered by `test/hello`, sleeps 5 seconds |
| `make-report` | Inngest function | Triggered by `report/requested`, sleeps 8 seconds, builds a report, retries twice |
| `heartbeat` | Cron function | Runs every minute and logs status counts |

## Checkpoints

### Stage 0 — health endpoint

```bat
curl -i http://localhost:8000/health
```

Expected: HTTP 200 and `{"status":"ok"}`.

### Stage 1 — say-hello

Open the dashboard at http://localhost:8288, find `say-hello`, invoke it with `{}`, and confirm it completes after the 5-second step.

### Stage 2 — background report

Submit a report:

```bat
curl -i -X POST http://localhost:8000/reports -H "Content-Type: application/json" -d "{\"topic\":\"cats\"}"
```

Copy the returned ID into this command:

```bat
curl http://localhost:8000/reports/PASTE_REPORT_ID_HERE
```

It should first show `pending`. Wait about 10 seconds and run the same GET command again. It should show `done` and a `result`.

Unknown ID should return 404:

```bat
curl -i http://localhost:8000/reports/nope
```

### Stage 3 — retries and validation

Submit the deliberately failing topic:

```bat
curl -i -X POST http://localhost:8000/reports -H "Content-Type: application/json" -d "{\"topic\":\"fail\"}"
```

In the Inngest dashboard, open the `make-report` run and verify that it has three attempts and ends in `Failed` (initial attempt + two retries).

Missing topic must be rejected:

```bat
curl -i -X POST http://localhost:8000/reports -H "Content-Type: application/json" -d "{}"
```

Expected: HTTP 400, and no job should be queued.

### Stage 4 — cron heartbeat

Wait at least two minutes. In the dashboard, check for two `heartbeat` runs approximately one minute apart and inspect the logs for pending/done/failed counts.

Cron expressions for the README:
- `0 8 * * *` — every day at 08:00.
- `0 22 * * 0` — every Sunday at 22:00.

Check the scheduler timezone before interpreting clock times.

## Proof to add before submission

Capture your own real evidence:
1. Terminal output showing the POST returns HTTP 202 quickly.
2. A GET response showing `pending`, followed by a later GET showing `done` and `result`.
3. Dashboard screenshot showing `say-hello` completed, `make-report` completed, `make-report` failed after three attempts, and at least two `heartbeat` runs.
4. The HTTP 400 result for a missing topic and HTTP 404 result for an unknown report ID.

Do not paste sample output as if it were real. Add your actual outputs and screenshots here after testing.

## Stage 3 README sentence

A retry is useful for a temporary failure, while missing or invalid input should be rejected immediately with HTTP 400 rather than retried.

## Stage 4 README sentences

`0 8 * * *` runs every day at 08:00.  
`0 22 * * 0` runs every Sunday at 22:00.

## Storage limitation

Reports are stored in an in-memory dictionary for this learning assignment. They disappear when the API process restarts, and this demo store is not shared across multiple API worker processes.

## Git commits

Commit each stage only after its checkpoint passes. Example messages:

```text
Stage 0: hello server
Stage 1: Inngest connected, first function runs
Stage 2: 202 + background job + status endpoint
Stage 3: retries seen, bad input rejected
Stage 4: cron heartbeat
Stage 5: publish and docs
```

For the optional AI rematch, keep AI-generated code in a separate folder or branch and document the actual differences you observe after running it.
