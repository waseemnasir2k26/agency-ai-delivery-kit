@echo off
rem ==========================================================================================
rem Kiran Studio 7 AM report robot (Windows). Runs headless Claude, validates the result,
rem writes reports\<date>.json or a reports\FAILED-<time>.txt receipt. Never fakes success.
rem
rem NOTE: This run needs skills and hooks, so it must NOT run in bare mode. Claude Code docs say
rem bare mode is planned to become the default for `claude -p`. If an update flips it, the
rem validator writes a FAILED receipt: check the flags first. Unattended runs: consider
rem `--permission-prompts none` so a prompt is denied instead of waited on.
rem
rem Setup: copy .robot.env.example to .robot.env (ROBOT_CLIENT, ROBOT_BUDGET in USD).
rem Needs: claude on PATH and logged in, python with jsonschema (pip install jsonschema).
rem Schedule (runs only while you are logged on; laptop must be awake, not on battery):
rem   schtasks /create /tn KiranDailyReport /sc daily /st 07:00 /tr "<your-project>\run-report.cmd" /f
rem   schtasks /run /tn KiranDailyReport          (test it now)
rem   schtasks /query /tn KiranDailyReport /v /fo list   (Last Result 0 = green, 1 = receipt)
rem   schtasks /change /tn KiranDailyReport /disable
rem   schtasks /delete /tn KiranDailyReport /f
rem ==========================================================================================
cd /d "%~dp0"
if not exist reports mkdir reports
if not exist .robot.env (
  echo FAILED: .robot.env not found. Copy .robot.env.example to .robot.env> reports\FAILED-no-robot-env.txt
  exit /b 1
)
rem load settings from a local file kept off screen
for /f "usebackq tokens=1,* delims==" %%a in (".robot.env") do set "%%a=%%b"
set /p SCHEMA=<schema.json
set "SCHEMA=%SCHEMA:"=\"%"
call claude -p "/client-report %ROBOT_CLIENT%" --model sonnet --setting-sources project --strict-mcp-config --no-session-persistence --output-format json --json-schema "%SCHEMA%" --max-budget-usd %ROBOT_BUDGET% > reports\_last.json 2> reports\_last.err
set CLAUDE_EXIT=%ERRORLEVEL%
python scripts\validate-report.py %CLAUDE_EXIT% %ROBOT_CLIENT%
exit /b %ERRORLEVEL%
