@echo off
echo === Health ===
curl -i http://localhost:8000/health
echo.
echo === Missing topic should return 400 ===
curl -i -X POST http://localhost:8000/reports -H "Content-Type: application/json" -d "{}"
echo.
echo === Unknown report should return 404 ===
curl -i http://localhost:8000/reports/nope
echo.
echo === Submit report (copy the returned ID for polling) ===
curl -i -X POST http://localhost:8000/reports -H "Content-Type: application/json" -d "{\"topic\":\"cats\"}"
echo.
pause
