@echo off
rem Site Watch nightly: the agent tests every client site, then the verifier (not the AI) writes the report.
rem The fixture sites must already be served (python serve.py). For real client sites, see README "Limits".
rem Needs your Claude login or ANTHROPIC_API_KEY in the environment (API-KEY-SETUP.md). Each run is billed.
cd /d "%~dp0"
python site_watch.py --run nightly --mode hardened --scenario clean --model sonnet --max-turns 40 --budget 1.00
python verify.py runs\nightly
