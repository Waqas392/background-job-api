import datetime
import logging
import uuid
from typing import Any

import inngest
import inngest.fast_api
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Background Job API", version="1.0.0")

inngest_client = inngest.Inngest(
    app_id="report-api",
    is_production=False,
    logger=logging.getLogger("uvicorn"),
)

# Demo storage only: reports disappear when the API process restarts.
reports: dict[str, dict[str, Any]] = {}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context) -> str:
    await ctx.step.sleep("wait-5s", datetime.timedelta(seconds=5))
    return "Hello from the background!"


@app.post("/reports")
async def create_report(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = None

    topic = body.get("topic") if isinstance(body, dict) else None
    if not isinstance(topic, str) or not topic.strip():
        return JSONResponse({"error": "topic is required"}, status_code=400)

    report_id = str(uuid.uuid4())
    reports[report_id] = {
        "id": report_id,
        "topic": topic.strip(),
        "status": "pending",
    }

    try:
        await inngest_client.send(
            inngest.Event(
                name="report/requested",
                data={"id": report_id, "topic": topic.strip()},
            )
        )
    except Exception:
        reports.pop(report_id, None)
        logging.exception("Could not send report/requested event")
        return JSONResponse(
            {"error": "Could not queue report. Is the Inngest Dev Server running?"},
            status_code=503,
        )

    return JSONResponse(
        {"id": report_id, "status": "pending"},
        status_code=202,
    )


@app.get("/reports/{report_id}")
def get_report(report_id: str):
    report = reports.get(report_id)
    if report is None:
        return JSONResponse({"error": "not found"}, status_code=404)
    return report


@app.get("/reports")
def list_reports():
    return list(reports.values())


@inngest_client.create_function(
    fn_id="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=2,
)
async def make_report(ctx: inngest.Context) -> dict[str, Any]:
    report_id = ctx.event.data["id"]
    topic = ctx.event.data["topic"]

    # Stretch goal: avoid rebuilding reports that are already complete.
    if reports.get(report_id, {}).get("status") == "done":
        return {"skipped": True, "id": report_id}

    await ctx.step.sleep("do-the-slow-work", datetime.timedelta(seconds=8))

    async def build_report() -> dict[str, Any]:
        # Deliberately fail for the assignment's retry demonstration.
        if topic == "fail":
            raise Exception("The report oven is broken!")

        result = f"Report about {topic}: this is a sample generated report."
        report = reports.get(report_id)
        if report is None:
            # The in-memory store may have been cleared by an API restart.
            raise RuntimeError("Report record is missing from in-memory storage")
        report.update({"status": "done", "result": result})
        return report

    try:
        return await ctx.step.run("build-report", build_report)
    except Exception:
        # Best effort status update before Inngest retries. Do not mark failed
        # until the final attempt; ctx.attempt is SDK-version dependent.
        if topic == "fail":
            # Inngest will show the actual final failure in the dashboard.
            # The report status is not relied on as the retry proof.
            report = reports.get(report_id)
            if report is not None:
                report["status"] = "failed"
        raise


@inngest_client.create_function(
    fn_id="heartbeat",
    trigger=inngest.TriggerCron(cron="* * * * *"),
)
async def heartbeat(ctx: inngest.Context) -> None:
    counts = {"pending": 0, "done": 0, "failed": 0}
    for report in reports.values():
        status = report.get("status", "pending")
        counts[status] = counts.get(status, 0) + 1
    ctx.logger.info(
        "heartbeat: pending=%s done=%s failed=%s",
        counts.get("pending", 0),
        counts.get("done", 0),
        counts.get("failed", 0),
    )


inngest.fast_api.serve(
    app,
    inngest_client,
    [say_hello, make_report, heartbeat],
)
