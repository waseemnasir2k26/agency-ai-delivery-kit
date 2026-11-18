# kiran-noor

Noor Dental Clinic connector (fictional clinic, synthetic data). Enable it only in the clinic repo.

Ships the `noor-bookings` MCP server (four read and draft tools: `list_tomorrow_bookings`, `find_available_slots`, `get_booking_summary`, `draft_reschedule`). Tool names with the plugin loaded: `mcp__plugin_kiran-noor_noor-bookings__<tool>`.

Setup on each machine: a Python 3.11+ with `pip install -r requirements.txt` (the `mcp` SDK). If plain `python` on PATH lacks it, set `NOOR_PYTHON` to that interpreter. Set `NOOR_API_TOKEN` to the read-only-connector key in the shell, never in a file. The plugin carries no key and no permission rules: allow rules stay in the clinic repo settings.

Install (in the client repo, replace `<your-org>`):

    claude plugin install kiran-noor --marketplace <your-org>/kiran-marketplace --scope project
