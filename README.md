# Background Job API — FastAPI + Inngest

A background job processing system built with **FastAPI** and **Inngest** for the FlyRank A7 assignment.

The application accepts report-generation requests through a REST API, immediately returns an HTTP `202 Accepted` response, and processes the work asynchronously using Inngest background functions.

It also demonstrates input validation, automatic retries, report status tracking, and scheduled cron execution.

## Features

- FastAPI REST API.
- Asynchronous background job processing with Inngest.
- Immediate HTTP 202 responses for accepted requests.
- Report status tracking (`pending`, `done`, `failed`).
- Automatic retries for failed background jobs.
- Input validation with HTTP 400 responses.
- HTTP 404 handling for unknown reports.
- Idempotency check to avoid rebuilding completed reports.
- Scheduled heartbeat function running every minute.
- Screenshots documenting implementation and testing.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | REST API framework |
| Inngest | Background job orchestration |
| Uvicorn | ASGI server |
| Node.js / npm | Inngest Dev Server |
| Git | Version control |
| GitHub | Source code hosting |

## Project Structure

```text
background-job-api/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── START_HERE.txt
├── test_requests.bat
│
└── screenshots/
    ├── stage-1-say-hello.png
    ├── stage-2-http-202.png
    ├── stage-2-report-done.png
    ├── stage-3-failed-run.png
    ├── stage-3-report-failed.png
    ├── stage-3-retries-confirmed.png
    ├── stage-3-validation-400.png
    └── stage-4-heartbeat.png
```

## Requirements

Install the following before running the project:

- Python 3.10 or later.
- Node.js and npm.
- Git.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Waqas392/background-job-api.git
cd background-job-api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows Command Prompt:

```cmd
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Application

The application requires two running processes.

### Terminal 1 — Start FastAPI

Activate the virtual environment and run:

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at:

```text
http://localhost:8000
```

### Terminal 2 — Start Inngest Dev Server

From the project directory, run:

```bash
npx inngest-cli@latest dev -u http://localhost:8000/api/inngest
```

Open the Inngest dashboard:

```text
http://localhost:8288
```

Keep both terminals running while testing.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks API health |
| POST | `/reports` | Validates and submits a report request |
| GET | `/reports/{report_id}` | Retrieves a report by ID |
| GET | `/reports` | Lists all reports |

### Health Check

```http
GET /health
```

Returns:

```json
{
  "status": "ok"
}
```

### Submit a Report

```http
POST /reports
Content-Type: application/json
```

Example request:

```json
{
  "topic": "cats"
}
```

The API validates the request, stores a pending report, sends an Inngest event, and returns HTTP 202.

Example response:

```json
{
  "id": "generated-report-id",
  "status": "pending"
}
```

### Retrieve Report Status

```http
GET /reports/{report_id}
```

A successful report eventually returns its result with status `done`.

## Inngest Background Functions

### 1. say-hello

- Trigger: `test/hello`
- Waits for five seconds using an Inngest sleep step.
- Returns a greeting message.

### 2. make-report

- Trigger: `report/requested`
- Waits for eight seconds before processing.
- Generates a report for valid topics.
- Updates report status to `done`.
- Uses two retries for failed executions.
- Marks the deliberately failing `fail` topic as `failed` after the final attempt.

### 3. heartbeat

- Trigger: Cron schedule.
- Runs automatically every minute.
- Counts reports by status.
- Logs pending, done, and failed report counts.

Cron expression:

```text
* * * * *
```

## Implementation Stages

### Stage 0 — Health Endpoint

Implemented a basic FastAPI health endpoint to verify that the API server is running.

### Stage 1 — Inngest Integration

Connected FastAPI with Inngest and implemented the `say-hello` background function.

### Stage 2 — Background Report Processing

Implemented:

- Report submission.
- HTTP 202 Accepted responses.
- Background report generation.
- Report status polling.
- Successful report completion.

### Stage 3 — Retries and Input Validation

Implemented automatic retries and request validation.

The `make-report` function uses:

```python
retries=2
```

This allows three total execution attempts:

1. Initial execution.
2. First retry.
3. Second retry.

The deliberately failing topic demonstrates retry behavior.

Missing or invalid topics are rejected immediately with HTTP 400 rather than being submitted as background jobs.

### Stage 4 — Cron Heartbeat

Implemented a scheduled heartbeat function using:

```python
inngest.TriggerCron(cron="* * * * *")
```

The function executes every minute and logs report status counts without requiring an HTTP request.

## Screenshots and Testing Evidence

The following screenshots document the implementation and local testing of the project.

### Stage 1 — Say Hello

![Stage 1 Say Hello](screenshots/stage-1-say-hello.png)

### Stage 2 — Background Job Processing

**HTTP 202 Accepted**

![Stage 2 HTTP 202](screenshots/stage-2-http-202.png)

**Report Successfully Completed**

![Stage 2 Report Done](screenshots/stage-2-report-done.png)

### Stage 3 — Retries and Validation

**Failed Background Job**

![Stage 3 Failed Run](screenshots/stage-3-failed-run.png)

**Failed Report Status**

![Stage 3 Report Failed](screenshots/stage-3-report-failed.png)

**Three Execution Attempts Confirmed**

![Stage 3 Retries Confirmed](screenshots/stage-3-retries-confirmed.png)

**HTTP 400 Validation**

![Stage 3 Validation](screenshots/stage-3-validation-400.png)

### Stage 4 — Cron Heartbeat

![Stage 4 Heartbeat](screenshots/stage-4-heartbeat.png)

## Important Implementation Details

### Retry vs. Validation

Retries are useful when a background operation fails temporarily.

However, invalid input should not be retried because the same invalid request will continue to fail.

This application handles these situations separately:

- Temporary or processing failures are handled through Inngest retries.
- Missing or invalid topics are rejected immediately with HTTP 400.

### Idempotency

The background function checks whether a report has already been completed before building it again.

This helps prevent duplicate processing of completed reports.

### Storage Limitation

This project uses an in-memory Python dictionary to store reports.

Consequently:

- Reports disappear when the FastAPI process restarts.
- Data is not persistent.
- Multiple API worker processes would not share the same report store.

Persistent database storage is outside the scope of this demonstration.

## Useful Cron Examples

| Cron Expression | Schedule |
|---|---|
| `* * * * *` | Every minute |
| `0 8 * * *` | Every day at 08:00 |
| `0 22 * * 0` | Every Sunday at 22:00 |

Actual execution times depend on the scheduler's configured timezone.

## Author

**Waqas Ahmad**

GitHub: [@Waqas392](https://github.com/Waqas392)

Project: [Background Job API](https://github.com/Waqas392/background-job-api)

## Assignment

**FlyRank — A7 Background Job Processing**

Built using FastAPI and Inngest to demonstrate asynchronous task processing, retries, validation, status tracking, and scheduled background execution.
