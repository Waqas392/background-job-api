# Background Job API — FastAPI + Inngest

A background job processing API built with **FastAPI** and **Inngest** as part of FlyRank Internship Assignment A7: *Your First Background Job*.

The application demonstrates how to accept a request immediately, process it asynchronously in the background, and allow clients to check the job's status.

## Project Overview

When a client submits a report request, the API:

1. Validates the request.
2. Creates a report with a unique ID.
3. Returns `202 Accepted` immediately.
4. Sends an event to Inngest for background processing.
5. Processes the report asynchronously.
6. Updates the report status to `done` or `failed`.

The application also demonstrates automatic retries, input validation, and scheduled cron jobs.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | REST API |
| Inngest | Background job orchestration |
| Uvicorn | ASGI development server |
| Inngest Dev Server | Local workflow monitoring |
| Git and GitHub | Version control and project hosting |

## Project Structure

```text
background-job/
│
├── main.py
├── requirements.txt
├── README.md
├── START_HERE.txt
├── test_requests.bat
├── .gitignore
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

## Getting Started

### Requirements

- Python 3.10 or newer
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Waqas392/background-job-api.git
cd background-job-api
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Application

You need two terminal windows.

### Terminal 1 — Start FastAPI

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at:

`http://localhost:8000`

### Terminal 2 — Start Inngest Dev Server

```bash
npx inngest-cli@latest dev -u http://localhost:8000/api/inngest
```

Open the Inngest dashboard:

`http://localhost:8288`

The dashboard allows you to inspect function executions, event runs, retries, and scheduled jobs.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks API health |
| POST | `/reports` | Creates a background report |
| GET | `/reports/{report_id}` | Retrieves a report by ID |
| GET | `/reports` | Lists available reports |

## Background Functions

The application contains three Inngest functions.

| Function | Trigger | Purpose |
|---|---|---|
| `say-hello` | `test/hello` | Runs a simple background task with a 5-second delay |
| `make-report` | `report/requested` | Generates a report asynchronously with an 8-second delay |
| `heartbeat` | Cron schedule | Periodically checks report counts |

## Implementation Stages

### Stage 0 — Hello Server

Created the FastAPI application and health-check endpoint.

Endpoint:

```http
GET /health
```

Expected response:

```json
{
  "status": "ok"
}
```

### Stage 1 — Inngest Integration

Integrated Inngest with FastAPI using the client ID `report-api`.

Created the `say-hello` function, triggered by the `test/hello` event.

The function waits for five seconds before completing.

**Screenshot evidence:**

![Stage 1 - Say Hello](screenshots/stage-1-say-hello.png)

### Stage 2 — Background Report Processing

Implemented asynchronous report creation.

A client submits a report request:

```http
POST /reports
Content-Type: application/json
```

Request body:

```json
{
  "topic": "cats"
}
```

The API responds immediately with HTTP `202 Accepted` rather than waiting for report generation.

**Actual POST response:**

```http
HTTP/1.1 202 Accepted
```

```json
{
  "id": "ebb1af58-3f02-40ed-b477-49b0b7289f82",
  "status": "pending"
}
```

**POST request screenshot:**

![Stage 2 - HTTP 202 Accepted](screenshots/stage-2-http-202.png)

The report can then be checked using:

```http
GET /reports/ebb1af58-3f02-40ed-b477-49b0b7289f82
```

**Actual completed report response:**

```json
{
  "id": "ebb1af58-3f02-40ed-b477-49b0b7289f82",
  "topic": "cats",
  "status": "done",
  "result": "Report about cats: this is a sample generated report."
}
```

**Completed report screenshot:**

![Stage 2 - Report Done](screenshots/stage-2-report-done.png)

### Stage 3 — Retries and Validation

Implemented error handling and input validation.

**Retry handling**

The `make-report` function is configured with two retries.

When a report is submitted with the topic `fail`, the function raises an error during processing. Inngest retries the function and eventually marks the run as failed after the configured attempts.

**Input validation**

Requests with missing or invalid required input are rejected with HTTP `400 Bad Request`.

Invalid requests are rejected before a background job is queued.

**Why retries and validation are different:**

Retries handle failures that occur during background processing. Validation rejects incorrect requests before processing begins, so retrying invalid input would not solve the problem.

**Screenshot evidence:**

![Stage 3 - Failed Run](screenshots/stage-3-failed-run.png)

![Stage 3 - Failed Report](screenshots/stage-3-report-failed.png)

![Stage 3 - Retries Confirmed](screenshots/stage-3-retries-confirmed.png)

![Stage 3 - Validation 400](screenshots/stage-3-validation-400.png)

### Stage 4 — Scheduled Cron Job

Implemented a scheduled `heartbeat` function using Inngest cron.

The function runs every minute:

```text
* * * * *
```

It periodically checks and logs the number of reports in different states:

- Pending reports
- Completed reports
- Failed reports

**Screenshot evidence:**

![Stage 4 - Heartbeat](screenshots/stage-4-heartbeat.png)

#### Cron Schedule Examples

| Cron Expression | Schedule |
|---|---|
| `* * * * *` | Every minute |
| `0 8 * * *` | Every day at 08:00 |
| `0 22 * * 0` | Every Sunday at 22:00 |

## Important Implementation Details

### Asynchronous Processing

The API does not wait for report generation to finish. It returns `202 Accepted` and lets Inngest execute the background function.

### Report Status Tracking

Reports have statuses that indicate their processing state:

- `pending`
- `done`
- `failed`

Clients can retrieve a report using its unique ID.

### Error Handling

The application demonstrates how Inngest handles configured retries when a background function fails.

### Storage

The current implementation uses in-memory report storage. This is suitable for the local assignment demonstration, but report records are not persistent across application restarts.

## Assignment Demonstration

This project demonstrates:

- Building a background job API with FastAPI.
- Integrating Inngest with a Python application.
- Returning HTTP `202 Accepted`.
- Tracking asynchronous job status.
- Handling background function failures.
- Configuring automatic retries.
- Validating incoming requests.
- Scheduling recurring cron jobs.
- Monitoring executions using the Inngest Dev Server.

## Author

**Waqas Ahmad**

GitHub: [@Waqas392](https://github.com/Waqas392)

Repository: [background-job-api](https://github.com/Waqas392/background-job-api)

**Program:** FlyRank Internship  
**Assignment:** A7 — Your First Background Job
